from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from core.controllers.commons import BaseResponse


class UserCreateInput(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    group_id: Optional[int] = None
    is_admin: bool = False

    @field_validator("password")
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        if any(ch.isspace() for ch in v):
            raise ValueError("password must not contain whitespace")
        if not any(ch.islower() for ch in v):
            raise ValueError("password must include a lowercase letter")
        if not any(ch.isupper() for ch in v):
            raise ValueError("password must include an uppercase letter")
        if not any(ch.isdigit() for ch in v):
            raise ValueError("password must include a digit")
        if not any(ch in "!@#$%^&*()-_=+[]{};:'\",.<>/?|`~" for ch in v):
            raise ValueError("password must include a special character")
        return v


class UserUpdateInput(BaseModel):
    name: Optional[str] = None
    group_id: Optional[int] = None
    is_admin: Optional[bool] = None


class UserOutput(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    status: str
    created_at: str
    updated_at: str
    group_id: Optional[int] = None
    is_admin: bool
    group: Optional[Dict[str, Any]] = None


class UserPermissionOutput(BaseModel):
    resource: str
    action: str
    name: str


class UserResponse(BaseResponse[UserOutput]):
    pass


class UsersResponse(BaseResponse[List[UserOutput]]):
    pass


class UserPermissionsResponse(BaseResponse[List[UserPermissionOutput]]):
    pass


