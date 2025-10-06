from dataclasses import dataclass
from typing import Optional, List

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.db import prisma
from core.security import verify_token
from .io import PermissionOutput, PermissionResponse, PermissionsResponse, PermissionCreateInput, PermissionUpdateInput

security = HTTPBearer()


@dataclass(kw_only=True)
class PermissionController:
    async def _verify_auth(self, credentials: HTTPAuthorizationCredentials) -> str:
        """Verify authentication token and return user email"""
        email = verify_token(credentials.credentials)
        if not email:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return email

    async def create(self, name: str, resource: str, action: str, description: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)) -> PermissionResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        existing = await prisma.permission.find_first(where={"resource": resource, "action": action})
        if existing:
            raise HTTPException(status_code=409, detail="Permission with this resource and action already exists")
        
        permission = await prisma.permission.create(data={
            "name": name,
            "resource": resource,
            "action": action,
            "description": description
        })
        return PermissionResponse(data=PermissionOutput.model_validate(permission.model_dump()))

    async def get(self, permission_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> PermissionResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        permission = await prisma.permission.find_unique(
            where={"id": permission_id},
            include={
                "rolePermissions": {
                    "include": {
                        "role": True
                    }
                }
            }
        )
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return PermissionResponse(data=PermissionOutput.model_validate(permission.model_dump()))

    async def get_by_resource_action(self, resource: str, action: str, credentials: HTTPAuthorizationCredentials = Depends(security)) -> PermissionResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        permission = await prisma.permission.find_first(
            where={"resource": resource, "action": action},
            include={
                "rolePermissions": {
                    "include": {
                        "role": True
                    }
                }
            }
        )
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        return PermissionResponse(data=PermissionOutput.model_validate(permission.model_dump()))

    async def list(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> PermissionsResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        permissions = await prisma.permission.find_many(
            include={
                "rolePermissions": {
                    "include": {
                        "role": True
                    }
                }
            }
        )
        return PermissionsResponse(data=[PermissionOutput.model_validate(p.model_dump()) for p in permissions])

    async def list_by_resource(self, resource: str, credentials: HTTPAuthorizationCredentials = Depends(security)) -> PermissionsResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        permissions = await prisma.permission.find_many(
            where={"resource": resource},
            include={
                "rolePermissions": {
                    "include": {
                        "role": True
                    }
                }
            }
        )
        return PermissionsResponse(data=[PermissionOutput.model_validate(p.model_dump()) for p in permissions])

    async def update(self, permission_id: int, name: Optional[str] = None, resource: Optional[str] = None, 
                    action: Optional[str] = None, description: Optional[str] = None, credentials: HTTPAuthorizationCredentials = Depends(security)) -> PermissionResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        permission = await prisma.permission.find_unique(where={"id": permission_id})
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if resource is not None:
            update_data["resource"] = resource
        if action is not None:
            update_data["action"] = action
        if description is not None:
            update_data["description"] = description
        
        # Kiểm tra resource + action mới không trùng với permission khác
        if resource is not None or action is not None:
            new_resource = resource if resource is not None else permission.resource
            new_action = action if action is not None else permission.action
            existing = await prisma.permission.find_first(
                where={"resource": new_resource, "action": new_action, "id": {"not": permission_id}}
            )
            if existing:
                raise HTTPException(status_code=409, detail="Permission with this resource and action already exists")
        
        updated_permission = await prisma.permission.update(
            where={"id": permission_id},
            data=update_data
        )
        return PermissionResponse(data=PermissionOutput.model_validate(updated_permission.model_dump()))

    async def delete(self, permission_id: int, credentials: HTTPAuthorizationCredentials = Depends(security)) -> PermissionResponse:
        # Verify authentication
        await self._verify_auth(credentials)
        permission = await prisma.permission.find_unique(where={"id": permission_id})
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")
        
        deleted_permission = await prisma.permission.delete(where={"id": permission_id})
        return PermissionResponse(data=PermissionOutput.model_validate(deleted_permission.model_dump()))

    async def create_with_body(self, body: PermissionCreateInput) -> PermissionResponse:
        return await self.create(
            name=body.name,
            resource=body.resource,
            action=body.action,
            description=body.description
        )

    async def update_with_body(self, permission_id: int, body: PermissionUpdateInput) -> PermissionResponse:
        return await self.update(
            permission_id=permission_id,
            name=body.name,
            resource=body.resource,
            action=body.action,
            description=body.description
        )
