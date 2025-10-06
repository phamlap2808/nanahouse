from pydantic import BaseModel, field_validator
from typing import Optional, List
from core.controllers.commons import BaseResponse


class PermissionCreateInput(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v: str):
        if len(v.strip()) < 2:
            raise ValueError("Permission name must be at least 2 characters")
        if len(v.strip()) > 50:
            raise ValueError("Permission name must be at most 50 characters")
        return v.strip()

    @field_validator("resource")
    def validate_resource(cls, v: str):
        if len(v.strip()) < 2:
            raise ValueError("Resource must be at least 2 characters")
        if len(v.strip()) > 30:
            raise ValueError("Resource must be at most 30 characters")
        return v.strip().lower()

    @field_validator("action")
    def validate_action(cls, v: str):
        valid_actions = ["create", "read", "update", "delete", "list", "manage"]
        if v.strip().lower() not in valid_actions:
            raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")
        return v.strip().lower()


class PermissionUpdateInput(BaseModel):
    name: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v: Optional[str]):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError("Permission name must be at least 2 characters")
            if len(v.strip()) > 50:
                raise ValueError("Permission name must be at most 50 characters")
            return v.strip()
        return v

    @field_validator("resource")
    def validate_resource(cls, v: Optional[str]):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError("Resource must be at least 2 characters")
            if len(v.strip()) > 30:
                raise ValueError("Resource must be at most 30 characters")
            return v.strip().lower()
        return v

    @field_validator("action")
    def validate_action(cls, v: Optional[str]):
        if v is not None:
            valid_actions = ["create", "read", "update", "delete", "list", "manage"]
            if v.strip().lower() not in valid_actions:
                raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")
            return v.strip().lower()
        return v


class PermissionOutput(BaseModel):
    id: int
    name: str
    resource: str
    action: str
    description: Optional[str] = None
    created_at: str
    updated_at: str
    role_permissions: Optional[List[dict]] = None


class PermissionResponse(BaseResponse[PermissionOutput]):
    pass


class PermissionsResponse(BaseResponse[List[PermissionOutput]]):
    pass
