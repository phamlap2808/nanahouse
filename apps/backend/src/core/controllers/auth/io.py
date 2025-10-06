from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator

from core.controllers.commons import BaseResponse


class RegisterInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72, description="Password must be between 8 and 72 characters")
    name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('password must be at least 8 characters')
        if len(v) > 72:
            raise ValueError('password cannot be longer than 72 characters')
        return v


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TokenOutput(BaseModel):
    access_token: str
    token_type: str


class MeUpdateInput(BaseModel):
    name: Optional[str] = None


class UserOutput(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    status: str
    groupId: Optional[int] = None
    isAdmin: bool = False


class UserResponse(BaseResponse[UserOutput]):
    pass


class TokenResponse(BaseResponse[TokenOutput]):
    pass


