"""Pydantic schemas for authentication and user management."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import validate_password_strength


# --- Request Schemas ---

class UserRegister(BaseModel):
    """Schema for user registration."""
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        validate_password_strength(v)
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Full name cannot be empty.")
        return v.strip()


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""
    email: EmailStr = Field(..., description="Email address")


class ResetPasswordRequest(BaseModel):
    """Schema for reset password request."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        validate_password_strength(v)
        return v


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Full name")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Full name cannot be empty.")
        return v.strip() if v else v


# --- Response Schemas ---

class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    id: UUID
    full_name: str
    email: str
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class APIResponse(BaseModel):
    """Consistent API response wrapper."""
    success: bool
    message: str
    data: Optional[Any] = None
