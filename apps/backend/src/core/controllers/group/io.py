from pydantic import BaseModel, field_validator
from typing import Optional, List
from core.controllers.commons import BaseResponse


class GroupCreateInput(BaseModel):
    name: str
    description: Optional[str] = None
    is_admin: bool = False

    @field_validator("name")
    def validate_name(cls, v: str):
        if len(v.strip()) < 2:
            raise ValueError("Group name must be at least 2 characters")
        if len(v.strip()) > 50:
            raise ValueError("Group name must be at most 50 characters")
        return v.strip()


class GroupUpdateInput(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_admin: Optional[bool] = None

    @field_validator("name")
    def validate_name(cls, v: Optional[str]):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError("Group name must be at least 2 characters")
            if len(v.strip()) > 50:
                raise ValueError("Group name must be at most 50 characters")
            return v.strip()
        return v


class GroupOutput(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_admin: bool
    created_at: str
    updated_at: str
    users: Optional[List[dict]] = None
    group_roles: Optional[List[dict]] = None


class GroupResponse(BaseResponse[GroupOutput]):
    pass


class GroupsResponse(BaseResponse[List[GroupOutput]]):
    pass
