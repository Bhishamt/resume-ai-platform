"""Authentication API endpoints.

POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh
POST /auth/forgot-password
POST /auth/reset-password
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.user import (
    APIResponse,
    ForgotPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(schema: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account with email and password."""
    user = auth_service.register(db, schema)
    return APIResponse(
        success=True,
        message="Registration successful.",
        data=user.model_dump(mode="json"),
    )


@router.post(
    "/login",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Login",
)
def login(schema: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return JWT tokens."""
    token_data = auth_service.login(db, schema)
    return APIResponse(
        success=True,
        message="Login successful.",
        data=token_data.model_dump(mode="json"),
    )


@router.post(
    "/logout",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout",
)
def logout():
    """Logout the current user.

    Client-side token removal. Server acknowledges the request.
    Token blacklisting can be added with Redis in a future phase.
    """
    return APIResponse(
        success=True,
        message="Logged out successfully.",
    )


@router.post(
    "/refresh",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh token",
)
def refresh(schema: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access and refresh tokens using a valid refresh token."""
    token_data = auth_service.refresh_token(db, schema.refresh_token)
    return APIResponse(
        success=True,
        message="Token refreshed successfully.",
        data=token_data.model_dump(mode="json"),
    )


@router.post(
    "/forgot-password",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Forgot password",
)
def forgot_password(schema: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request a password reset. Always returns success to prevent email enumeration."""
    message = auth_service.forgot_password(db, schema)
    return APIResponse(
        success=True,
        message=message,
    )


@router.post(
    "/reset-password",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
)
def reset_password(schema: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using a valid reset token and new password."""
    message = auth_service.reset_password(db, schema)
    return APIResponse(
        success=True,
        message=message,
    )
