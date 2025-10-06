from pydantic import BaseModel, field_validator
from typing import Optional, List
from core.controllers.commons import BaseResponse


class RoleCreateInput(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v: str):
        if len(v.strip()) < 2:
            raise ValueError("Role name must be at least 2 characters")
        if len(v.strip()) > 50:
            raise ValueError("Role name must be at most 50 characters")
        return v.strip()


class RoleUpdateInput(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v: Optional[str]):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError("Role name must be at least 2 characters")
            if len(v.strip()) > 50:
                raise ValueError("Role name must be at most 50 characters")
            return v.strip()
        return v


class RoleOutput(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str
    role_permissions: Optional[List[dict]] = None
    group_roles: Optional[List[dict]] = None


class RoleResponse(BaseResponse[RoleOutput]):
    pass


class RolesResponse(BaseResponse[List[RoleOutput]]):
    pass
