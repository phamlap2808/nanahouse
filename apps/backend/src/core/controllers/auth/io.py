from typing import Optional

from pydantic import BaseModel, EmailStr

from core.controllers.commons import BaseResponse


class RegisterInput(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


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
    role: str


class UserResponse(BaseResponse[UserOutput]):
    pass


class TokenResponse(BaseResponse[TokenOutput]):
    pass


