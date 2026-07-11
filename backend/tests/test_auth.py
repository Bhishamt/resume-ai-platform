"""Authentication test suite.

Tests cover:
- Registration (valid, duplicate email, weak password)
- Login (valid, wrong password, non-existent email)
- JWT token creation and validation
- Protected route access (valid token, no token, invalid token)
- Password hashing
- Profile endpoints (get, update)
- Refresh token flow
"""

from app.core.security import hash_password, validate_password_strength, verify_password
from app.utils.jwt_utils import create_access_token, decode_token

# ---------- Password Hashing ----------


class TestPasswordHashing:
    """Tests for bcrypt password hashing."""

    def test_hash_and_verify(self):
        password = "SecureP@ss1"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        password = "SecureP@ss1"
        hashed = hash_password(password)
        assert verify_password("WrongP@ss1", hashed) is False

    def test_hash_is_unique(self):
        password = "SecureP@ss1"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # Different salts


# ---------- Password Strength Validation ----------


class TestPasswordValidation:
    """Tests for password strength requirements."""

    def test_valid_password_passes(self):
        validate_password_strength("SecureP@ss1")

    def test_short_password_fails(self):
        try:
            validate_password_strength("Ab@1xyz")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "8 characters" in str(e)

    def test_no_uppercase_fails(self):
        try:
            validate_password_strength("securep@ss1")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "uppercase" in str(e)

    def test_no_lowercase_fails(self):
        try:
            validate_password_strength("SECUREP@SS1")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "lowercase" in str(e)

    def test_no_digit_fails(self):
        try:
            validate_password_strength("SecureP@ss")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "digit" in str(e)

    def test_no_special_char_fails(self):
        try:
            validate_password_strength("SecurePass1")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "special character" in str(e)


# ---------- JWT Token Tests ----------


class TestJWT:
    """Tests for JWT token utilities."""

    def test_create_and_decode_access_token(self):
        token = create_access_token(subject="test-user-id")
        payload = decode_token(token)
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "access"

    def test_expired_token_raises(self):
        from datetime import timedelta

        import jwt as pyjwt

        token = create_access_token(
            subject="test-user-id",
            expires_delta=timedelta(seconds=-1),
        )
        try:
            decode_token(token)
            assert False, "Should have raised ExpiredSignatureError"
        except pyjwt.ExpiredSignatureError:
            pass


# ---------- Registration ----------


class TestRegistration:
    """Tests for the registration endpoint."""

    def test_register_success(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Jane Doe",
                "email": "jane@example.com",
                "password": "SecureP@ss1",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "jane@example.com"
        assert data["data"]["full_name"] == "Jane Doe"
        assert "password" not in data["data"]
        assert "password_hash" not in data["data"]

    def test_register_duplicate_email(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Another User",
                "email": registered_user["email"],
                "password": "SecureP@ss1",
            },
        )
        assert response.status_code == 409
        assert response.json()["success"] is False

    def test_register_weak_password(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Weak Pass",
                "email": "weak@example.com",
                "password": "weak",
            },
        )
        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "full_name": "Bad Email",
                "email": "not-an-email",
                "password": "SecureP@ss1",
            },
        )
        assert response.status_code == 422


# ---------- Login ----------


class TestLogin:
    """Tests for the login endpoint."""

    def test_login_success(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["email"] == registered_user["email"]

    def test_login_wrong_password(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": registered_user["email"],
                "password": "WrongP@ss1",
            },
        )
        assert response.status_code == 401
        assert response.json()["success"] is False

    def test_login_nonexistent_email(self, client):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nobody@example.com",
                "password": "SecureP@ss1",
            },
        )
        assert response.status_code == 401


# ---------- Protected Routes ----------


class TestProtectedRoutes:
    """Tests for JWT-protected endpoints."""

    def test_get_profile_authenticated(self, client, auth_headers):
        response = client.get("/api/v1/users/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "test@example.com"

    def test_get_profile_no_token(self, client):
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 422  # Missing required header

    def test_get_profile_invalid_token(self, client):
        response = client.get(
            "/api/v1/users/profile",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_update_profile(self, client, auth_headers):
        response = client.put(
            "/api/v1/users/profile",
            json={"full_name": "Updated Name"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["full_name"] == "Updated Name"


# ---------- Token Refresh ----------


class TestTokenRefresh:
    """Tests for the token refresh endpoint."""

    def test_refresh_success(self, client, auth_tokens):
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_tokens["refresh_token"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_refresh_invalid_token(self, client):
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )
        assert response.status_code == 401


# ---------- Logout ----------


class TestLogout:
    """Tests for the logout endpoint."""

    def test_logout_success(self, client):
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        assert response.json()["success"] is True


# ---------- Forgot / Reset Password ----------


class TestPasswordReset:
    """Tests for forgot and reset password flow."""

    def test_forgot_password_existing_email(self, client, registered_user):
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": registered_user["email"]},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_forgot_password_nonexistent_email(self, client):
        """Should still return 200 to prevent email enumeration."""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "nobody@example.com"},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_reset_password_invalid_token(self, client):
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid.token",
                "new_password": "NewSecureP@ss1",
            },
        )
        assert response.status_code == 400
