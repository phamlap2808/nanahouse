"""Pydantic schemas for authentication and user management."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    id: int
    email: str
    full_name: str
    role: str
    avatar_url: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: str = Field(min_length=1, max_length=255)


class PasswordChange(BaseModel):
    """Schema for changing password."""

    current_password: str
    new_password: str = Field(min_length=6, max_length=128)


class UserRoleUpdate(BaseModel):
    """Schema for admin changing a user's role."""

    role: str = Field(pattern="^(admin|staff|viewer)$")


class UserStatusUpdate(BaseModel):
    """Schema for admin activating/deactivating a user."""

    is_active: bool


class AdminCreateUser(BaseModel):
    """Schema for admin creating a new user with role."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: str = Field(default="staff", pattern="^(admin|staff|viewer)$")

