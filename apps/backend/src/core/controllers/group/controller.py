from dataclasses import dataclass
from typing import Optional, List

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.db import prisma
from core.security import verify_token
from .io import GroupOutput, GroupResponse, GroupsResponse, GroupCreateInput, GroupUpdateInput

security = HTTPBearer()


@dataclass(kw_only=True)
class GroupController:
    async def _verify_auth(self, credentials: HTTPAuthorizationCredentials) -> str:
        """Verify authentication token and return user email"""
        email = verify_token(credentials.credentials)
        if not email:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return email

    async def create(self, name: str, description: Optional[str] = None, is_admin: bool = False, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        existing = await prisma.group.find_unique(where={"name": name})
        if existing:
            raise HTTPException(status_code=409, detail="Group name already exists")
        
        group = await prisma.group.create(data={
            "name": name,
            "description": description,
            "isAdmin": is_admin
        })
        return GroupResponse(data=GroupOutput.model_validate(group.model_dump()))

    async def get(self, group_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        group = await prisma.group.find_unique(
            where={"id": group_id},
            include={
                "users": True,
                "groupRoles": {
                    "include": {
                        "role": {
                            "include": {
                                "rolePermissions": {
                                    "include": {
                                        "permission": True
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        return GroupResponse(data=GroupOutput.model_validate(group.model_dump()))

    async def list(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupsResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        groups = await prisma.group.find_many(
            include={
                "users": True,
                "groupRoles": {
                    "include": {
                        "role": True
                    }
                }
            }
        )
        return GroupsResponse(data=[GroupOutput.model_validate(g.model_dump()) for g in groups])

    async def update(self, group_id: int, name: Optional[str] = None, description: Optional[str] = None, is_admin: Optional[bool] = None, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        group = await prisma.group.find_unique(where={"id": group_id})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        update_data = {}
        if name is not None:
            # Kiểm tra tên mới không trùng với group khác
            existing = await prisma.group.find_first(where={"name": name, "id": {"not": group_id}})
            if existing:
                raise HTTPException(status_code=409, detail="Group name already exists")
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if is_admin is not None:
            update_data["isAdmin"] = is_admin
        
        updated_group = await prisma.group.update(
            where={"id": group_id},
            data=update_data
        )
        return GroupResponse(data=GroupOutput.model_validate(updated_group.model_dump()))

    async def delete(self, group_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        group = await prisma.group.find_unique(where={"id": group_id})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        deleted_group = await prisma.group.delete(where={"id": group_id})
        return GroupResponse(data=GroupOutput.model_validate(deleted_group.model_dump()))

    async def add_user(self, group_id: int, user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        # Kiểm tra group tồn tại
        group = await prisma.group.find_unique(where={"id": group_id})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Kiểm tra user tồn tại
        user = await prisma.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Thêm user vào group
        await prisma.user.update(
            where={"id": user_id},
            data={"groupId": group_id}
        )
        
        # Trả về group đã cập nhật
        updated_group = await prisma.group.find_unique(
            where={"id": group_id},
            include={"users": True}
        )
        return GroupResponse(data=GroupOutput.model_validate(updated_group.model_dump()))

    async def remove_user(self, group_id: int, user_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        # Kiểm tra group tồn tại
        group = await prisma.group.find_unique(where={"id": group_id})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Kiểm tra user tồn tại và thuộc group này
        user = await prisma.user.find_unique(where={"id": user_id, "groupId": group_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found in this group")
        
        # Xóa user khỏi group
        await prisma.user.update(
            where={"id": user_id},
            data={"groupId": None}
        )
        
        # Trả về group đã cập nhật
        updated_group = await prisma.group.find_unique(
            where={"id": group_id},
            include={"users": True}
        )
        return GroupResponse(data=GroupOutput.model_validate(updated_group.model_dump()))

    async def assign_role(self, group_id: int, role_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        # Kiểm tra group tồn tại
        group = await prisma.group.find_unique(where={"id": group_id})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Kiểm tra role tồn tại
        role = await prisma.role.find_unique(where={"id": role_id})
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Kiểm tra role đã được gán chưa
        existing = await prisma.grouprole.find_first(
            where={"groupId": group_id, "roleId": role_id}
        )
        if existing:
            raise HTTPException(status_code=409, detail="Role already assigned to this group")
        
        # Gán role cho group
        await prisma.grouprole.create(data={
            "groupId": group_id,
            "roleId": role_id
        })
        
        # Trả về group đã cập nhật
        updated_group = await prisma.group.find_unique(
            where={"id": group_id},
            include={
                "groupRoles": {
                    "include": {
                        "role": True
                    }
                }
            }
        )
        return GroupResponse(data=GroupOutput.model_validate(updated_group.model_dump()))

    async def remove_role(self, group_id: int, role_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> GroupResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        # Kiểm tra group tồn tại
        group = await prisma.group.find_unique(where={"id": group_id})
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Kiểm tra role được gán cho group này
        group_role = await prisma.grouprole.find_first(
            where={"groupId": group_id, "roleId": role_id}
        )
        if not group_role:
            raise HTTPException(status_code=404, detail="Role not assigned to this group")
        
        # Xóa role khỏi group
        await prisma.grouprole.delete_many(
            where={"groupId": group_id, "roleId": role_id}
        )
        
        # Trả về group đã cập nhật
        updated_group = await prisma.group.find_unique(
            where={"id": group_id},
            include={
                "groupRoles": {
                    "include": {
                        "role": True
                    }
                }
            }
        )
        return GroupResponse(data=GroupOutput.model_validate(updated_group.model_dump()))

    async def create_with_body(self, body: GroupCreateInput) -> GroupResponse:
        return await self.create(
            name=body.name,
            description=body.description,
            is_admin=body.is_admin
        )

    async def update_with_body(self, group_id: int, body: GroupUpdateInput) -> GroupResponse:
        return await self.update(
            group_id=group_id,
            name=body.name,
            description=body.description,
            is_admin=body.is_admin
        )
