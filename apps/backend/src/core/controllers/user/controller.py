from dataclasses import dataclass
from typing import Optional, List

from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials

from core.db import prisma
from core.auth_utils import verify_auth
from .io import UserOutput, UserResponse, UsersResponse, UserPermissionsResponse


@dataclass(kw_only=True)
class UserController:
    async def create(self, email: str, password: str, name: Optional[str] = None, group_id: Optional[int] = None, is_admin: bool = False, credentials: HTTPAuthorizationCredentials = Depends(verify_auth)) -> UserResponse:
        
        existing = await prisma.user.find_unique(where={"email": email})
        if existing:
            raise HTTPException(status_code=409, detail="email already exists")
        
        # Kiểm tra group tồn tại nếu được cung cấp
        if group_id:
            group = await prisma.group.find_unique(where={"id": group_id})
            if not group:
                raise HTTPException(status_code=404, detail="Group not found")
        
        user = await prisma.user.create(data={
            "email": email, 
            "password": password, 
            "name": name,
            "groupId": group_id,
            "isAdmin": is_admin
        })
        return UserResponse(data=UserOutput.model_validate(user.model_dump()))

    async def get(self, user_id: int, credentials: HTTPAuthorizationCredentials = Depends(verify_auth)) -> UserResponse:
        
        user = await prisma.user.find_unique(
            where={"id": user_id},
            include={
                "group": {
                    "include": {
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
                }
            }
        )
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        return UserResponse(data=UserOutput.model_validate(user.model_dump()))

    async def list(self, credentials: HTTPAuthorizationCredentials = Depends(verify_auth)) -> UsersResponse:
        
        users = await prisma.user.find_many(
            include={
                "group": {
                    "include": {
                        "groupRoles": {
                            "include": {
                                "role": True
                            }
                        }
                    }
                }
            }
        )
        return UsersResponse(data=[UserOutput.model_validate(u.model_dump()) for u in users])

    async def update(self, user_id: int, name: Optional[str] = None, group_id: Optional[int] = None, is_admin: Optional[bool] = None, credentials: HTTPAuthorizationCredentials = Depends(verify_auth)) -> UserResponse:
        
        user = await prisma.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if group_id is not None:
            # Kiểm tra group tồn tại
            if group_id != 0:  # 0 có nghĩa là xóa group
                group = await prisma.group.find_unique(where={"id": group_id})
                if not group:
                    raise HTTPException(status_code=404, detail="Group not found")
            update_data["groupId"] = group_id if group_id != 0 else None
        if is_admin is not None:
            update_data["isAdmin"] = is_admin
        
        updated_user = await prisma.user.update(
            where={"id": user_id},
            data=update_data
        )
        return UserResponse(data=UserOutput.model_validate(updated_user.model_dump()))

    async def delete(self, user_id: int, credentials: HTTPAuthorizationCredentials = Depends(verify_auth)) -> UserResponse:
        
        user = await prisma.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        
        deleted_user = await prisma.user.delete(where={"id": user_id})
        return UserResponse(data=UserOutput.model_validate(deleted_user.model_dump()))

    async def get_permissions(self, user_id: int) -> UserPermissionsResponse:
        """Lấy tất cả permissions của user"""
        user = await prisma.user.find_unique(
            where={"id": user_id},
            include={
                "group": {
                    "include": {
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
                }
            }
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        
        permissions = []
        
        # Nếu user là admin hoặc group có isAdmin = True
        if user.get("isAdmin") or (user.get("group") and user["group"].get("isAdmin")):
            # Trả về tất cả permissions
            all_permissions = await prisma.permission.find_many()
            permissions = [{"resource": p["resource"], "action": p["action"], "name": p["name"]} for p in all_permissions]
        else:
            # Lấy permissions từ roles của group
            if user.get("group") and user["group"].get("groupRoles"):
                for group_role in user["group"]["groupRoles"]:
                    role = group_role.get("role")
                    if role and role.get("rolePermissions"):
                        for role_permission in role["rolePermissions"]:
                            permission = role_permission.get("permission")
                            if permission:
                                permissions.append({
                                    "resource": permission["resource"],
                                    "action": permission["action"],
                                    "name": permission["name"]
                                })
        
        return UserPermissionsResponse(data=permissions)

    async def check_permission(self, user_id: int, resource: str, action: str) -> bool:
        """Kiểm tra user có permission cụ thể không"""
        permissions = await self.get_permissions(user_id)
        return {"resource": resource, "action": action} in [{"resource": p["resource"], "action": p["action"]} for p in permissions.data]

    async def is_admin(self, user_id: int) -> bool:
        """Kiểm tra user có phải admin không"""
        user = await prisma.user.find_unique(
            where={"id": user_id},
            include={"group": True}
        )
        
        if not user:
            return False
        
        # Kiểm tra user có isAdmin = True
        if user.get("isAdmin"):
            return True
        
        # Kiểm tra group có isAdmin = True
        if user.get("group") and user["group"].get("isAdmin"):
            return True
        
        return False


