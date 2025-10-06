from dataclasses import dataclass
from typing import Optional, List

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.db import prisma
from core.security import verify_token
from .io import RoleOutput, RoleResponse, RolesResponse, RoleCreateInput, RoleUpdateInput

security = HTTPBearer()


@dataclass(kw_only=True)
class RoleController:
    async def _verify_auth(self, credentials: HTTPAuthorizationCredentials) -> str:
        """Verify authentication token and return user email"""
        email = verify_token(credentials.credentials)
        if not email:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return email

    async def create(self, name: str, description: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)) -> RoleResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        existing = await prisma.role.find_unique(where={"name": name})
        if existing:
            raise HTTPException(status_code=409, detail="Role name already exists")
        
        role = await prisma.role.create(data={
            "name": name,
            "description": description
        })
        return RoleResponse(data=RoleOutput.model_validate(role.model_dump()))

    async def get(self, role_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> RoleResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        role = await prisma.role.find_unique(
            where={"id": role_id},
            include={
                "rolePermissions": {
                    "include": {
                        "permission": True
                    }
                },
                "groupRoles": {
                    "include": {
                        "group": True
                    }
                }
            }
        )
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return RoleResponse(data=RoleOutput.model_validate(role.model_dump()))

    async def list(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> RolesResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        roles = await prisma.role.find_many(
            include={
                "rolePermissions": {
                    "include": {
                        "permission": True
                    }
                },
                "groupRoles": {
                    "include": {
                        "group": True
                    }
                }
            }
        )
        return RolesResponse(data=[RoleOutput.model_validate(r.model_dump()) for r in roles])

    async def update(self, role_id: int, name: Optional[str] = None, description: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)) -> RoleResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        role = await prisma.role.find_unique(where={"id": role_id})
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        update_data = {}
        if name is not None:
            # Kiểm tra tên mới không trùng với role khác
            existing = await prisma.role.find_first(where={"name": name, "id": {"not": role_id}})
            if existing:
                raise HTTPException(status_code=409, detail="Role name already exists")
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        
        updated_role = await prisma.role.update(
            where={"id": role_id},
            data=update_data
        )
        return RoleResponse(data=RoleOutput.model_validate(updated_role.model_dump()))

    async def delete(self, role_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> RoleResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        role = await prisma.role.find_unique(where={"id": role_id})
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        deleted_role = await prisma.role.delete(where={"id": role_id})
        return RoleResponse(data=RoleOutput.model_validate(deleted_role.model_dump()))

    async def assign_permission(self, role_id: int, permission_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> RoleResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        # Kiểm tra role tồn tại
        role = await prisma.role.find_unique(where={"id": role_id})
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Kiểm tra permission tồn tại
        permission = await prisma.permission.find_unique(where={"id": permission_id})
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        # Kiểm tra permission đã được gán chưa
        existing = await prisma.rolepermission.find_first(
            where={"roleId": role_id, "permissionId": permission_id}
        )
        if existing:
            raise HTTPException(status_code=409, detail="Permission already assigned to this role")
        
        # Gán permission cho role
        await prisma.rolepermission.create(data={
            "roleId": role_id,
            "permissionId": permission_id
        })
        
        # Trả về role đã cập nhật
        updated_role = await prisma.role.find_unique(
            where={"id": role_id},
            include={
                "rolePermissions": {
                    "include": {
                        "permission": True
                    }
                }
            }
        )
        return RoleResponse(data=RoleOutput.model_validate(updated_role.model_dump()))

    async def remove_permission(self, role_id: int, permission_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> RoleResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        # Kiểm tra role tồn tại
        role = await prisma.role.find_unique(where={"id": role_id})
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Kiểm tra permission được gán cho role này
        role_permission = await prisma.rolepermission.find_first(
            where={"roleId": role_id, "permissionId": permission_id}
        )
        if not role_permission:
            raise HTTPException(status_code=404, detail="Permission not assigned to this role")
        
        # Xóa permission khỏi role
        await prisma.rolepermission.delete_many(
            where={"roleId": role_id, "permissionId": permission_id}
        )
        
        # Trả về role đã cập nhật
        updated_role = await prisma.role.find_unique(
            where={"id": role_id},
            include={
                "rolePermissions": {
                    "include": {
                        "permission": True
                    }
                }
            }
        )
        return RoleResponse(data=RoleOutput.model_validate(updated_role.model_dump()))

    async def create_with_body(self, body: RoleCreateInput) -> RoleResponse:
        return await self.create(
            name=body.name,
            description=body.description
        )

    async def update_with_body(self, role_id: int, body: RoleUpdateInput) -> RoleResponse:
        return await self.update(
            role_id=role_id,
            name=body.name,
            description=body.description
        )
