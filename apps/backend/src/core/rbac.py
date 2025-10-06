"""
RBAC Utilities - Các hàm tiện ích để quản lý RBAC
"""

from typing import List, Optional, Dict, Any
from core.db import prisma


class RBACManager:
    """Class chính để quản lý RBAC"""
    
    async def initialize_default_permissions(self) -> bool:
        """Khởi tạo các permissions mặc định"""
        default_permissions = [
            # User permissions
            {"name": "user_create", "resource": "users", "action": "create", "description": "Tạo user mới"},
            {"name": "user_read", "resource": "users", "action": "read", "description": "Xem thông tin user"},
            {"name": "user_update", "resource": "users", "action": "update", "description": "Cập nhật thông tin user"},
            {"name": "user_delete", "resource": "users", "action": "delete", "description": "Xóa user"},
            
            # Group permissions
            {"name": "group_create", "resource": "groups", "action": "create", "description": "Tạo group mới"},
            {"name": "group_read", "resource": "groups", "action": "read", "description": "Xem thông tin group"},
            {"name": "group_update", "resource": "groups", "action": "update", "description": "Cập nhật thông tin group"},
            {"name": "group_delete", "resource": "groups", "action": "delete", "description": "Xóa group"},
            
            # Role permissions
            {"name": "role_create", "resource": "roles", "action": "create", "description": "Tạo role mới"},
            {"name": "role_read", "resource": "roles", "action": "read", "description": "Xem thông tin role"},
            {"name": "role_update", "resource": "roles", "action": "update", "description": "Cập nhật thông tin role"},
            {"name": "role_delete", "resource": "roles", "action": "delete", "description": "Xóa role"},
            
            # Permission permissions
            {"name": "permission_create", "resource": "permissions", "action": "create", "description": "Tạo permission mới"},
            {"name": "permission_read", "resource": "permissions", "action": "read", "description": "Xem thông tin permission"},
            {"name": "permission_update", "resource": "permissions", "action": "update", "description": "Cập nhật thông tin permission"},
            {"name": "permission_delete", "resource": "permissions", "action": "delete", "description": "Xóa permission"},
        ]
        
        try:
            for perm_data in default_permissions:
                # Kiểm tra xem permission đã tồn tại chưa
                existing = await prisma.permission.find_first(
                    where={"resource": perm_data["resource"], "action": perm_data["action"]}
                )
                if not existing:
                    await prisma.permission.create(data=perm_data)
            
            return True
        except Exception as e:
            print(f"Lỗi khi khởi tạo permissions mặc định: {str(e)}")
            return False
    
    async def create_default_roles(self) -> bool:
        """Tạo các roles mặc định"""
        default_roles = [
            {
                "name": "super_admin",
                "description": "Quản trị viên cấp cao - có tất cả quyền"
            },
            {
                "name": "admin",
                "description": "Quản trị viên - quản lý users và groups"
            },
            {
                "name": "moderator",
                "description": "Điều hành viên - quản lý nội dung"
            },
            {
                "name": "user",
                "description": "Người dùng thông thường"
            }
        ]
        
        try:
            for role_data in default_roles:
                # Kiểm tra xem role đã tồn tại chưa
                existing = await prisma.role.find_unique(
                    where={"name": role_data["name"]}
                )
                if not existing:
                    await prisma.role.create(data=role_data)
            
            return True
        except Exception as e:
            print(f"Lỗi khi tạo roles mặc định: {str(e)}")
            return False
    
    async def create_default_groups(self) -> bool:
        """Tạo các groups mặc định"""
        default_groups = [
            {
                "name": "super_admins",
                "description": "Nhóm quản trị viên cấp cao",
                "isAdmin": True
            },
            {
                "name": "admins", 
                "description": "Nhóm quản trị viên",
                "isAdmin": False
            },
            {
                "name": "users",
                "description": "Nhóm người dùng thông thường",
                "isAdmin": False
            }
        ]
        
        try:
            for group_data in default_groups:
                # Kiểm tra xem group đã tồn tại chưa
                existing = await prisma.group.find_unique(
                    where={"name": group_data["name"]}
                )
                if not existing:
                    await prisma.group.create(data=group_data)
            
            return True
        except Exception as e:
            print(f"Lỗi khi tạo groups mặc định: {str(e)}")
            return False
    
    async def assign_permissions_to_role(self, role_name: str, permissions: List[Dict[str, str]]) -> bool:
        """Gán permissions cho role"""
        try:
            role = await prisma.role.find_unique(where={"name": role_name})
            if not role:
                raise Exception(f"Role '{role_name}' không tồn tại")
            
            for perm_data in permissions:
                permission = await prisma.permission.find_first(
                    where={"resource": perm_data["resource"], "action": perm_data["action"]}
                )
                if permission:
                    # Kiểm tra xem đã gán chưa
                    existing = await prisma.rolepermission.find_first(
                        where={"roleId": role["id"], "permissionId": permission["id"]}
                    )
                    if not existing:
                        await prisma.rolepermission.create(data={
                            "roleId": role["id"],
                            "permissionId": permission["id"]
                        })
            
            return True
        except Exception as e:
            print(f"Lỗi khi gán permissions cho role: {str(e)}")
            return False
    
    async def assign_roles_to_group(self, group_name: str, role_names: List[str]) -> bool:
        """Gán roles cho group"""
        try:
            group = await prisma.group.find_unique(where={"name": group_name})
            if not group:
                raise Exception(f"Group '{group_name}' không tồn tại")
            
            for role_name in role_names:
                role = await prisma.role.find_unique(where={"name": role_name})
                if role:
                    # Kiểm tra xem đã gán chưa
                    existing = await prisma.grouprole.find_first(
                        where={"groupId": group["id"], "roleId": role["id"]}
                    )
                    if not existing:
                        await prisma.grouprole.create(data={
                            "groupId": group["id"],
                            "roleId": role["id"]
                        })
            
            return True
        except Exception as e:
            print(f"Lỗi khi gán roles cho group: {str(e)}")
            return False
    
    async def setup_default_rbac(self) -> bool:
        """Thiết lập RBAC mặc định"""
        try:
            # Khởi tạo permissions
            await self.initialize_default_permissions()
            
            # Tạo roles
            await self.create_default_roles()
            
            # Tạo groups
            await self.create_default_groups()
            
            # Gán permissions cho roles
            await self.assign_permissions_to_role("super_admin", [
                {"resource": "users", "action": "create"},
                {"resource": "users", "action": "read"},
                {"resource": "users", "action": "update"},
                {"resource": "users", "action": "delete"},
                {"resource": "groups", "action": "create"},
                {"resource": "groups", "action": "read"},
                {"resource": "groups", "action": "update"},
                {"resource": "groups", "action": "delete"},
                {"resource": "roles", "action": "create"},
                {"resource": "roles", "action": "read"},
                {"resource": "roles", "action": "update"},
                {"resource": "roles", "action": "delete"},
                {"resource": "permissions", "action": "create"},
                {"resource": "permissions", "action": "read"},
                {"resource": "permissions", "action": "update"},
                {"resource": "permissions", "action": "delete"},
            ])
            
            await self.assign_permissions_to_role("admin", [
                {"resource": "users", "action": "create"},
                {"resource": "users", "action": "read"},
                {"resource": "users", "action": "update"},
                {"resource": "groups", "action": "read"},
            ])
            
            await self.assign_permissions_to_role("user", [
                {"resource": "users", "action": "read"},
            ])
            
            # Gán roles cho groups
            await self.assign_roles_to_group("super_admins", ["super_admin"])
            await self.assign_roles_to_group("admins", ["admin"])
            await self.assign_roles_to_group("users", ["user"])
            
            return True
        except Exception as e:
            print(f"Lỗi khi thiết lập RBAC mặc định: {str(e)}")
            return False


class PermissionChecker:
    """Class để kiểm tra quyền truy cập"""
    
    async def check_permission(self, user_id: int, resource: str, action: str) -> bool:
        """Kiểm tra user có permission không"""
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
            return False
        
        # Nếu user là admin hoặc group có isAdmin = True
        if user.get("isAdmin") or (user.get("group") and user["group"].get("isAdmin")):
            return True
        
        # Kiểm tra permission trong roles của group
        if user.get("group") and user["group"].get("groupRoles"):
            for group_role in user["group"]["groupRoles"]:
                role = group_role.get("role")
                if role and role.get("rolePermissions"):
                    for role_permission in role["rolePermissions"]:
                        permission = role_permission.get("permission")
                        if permission and permission["resource"] == resource and permission["action"] == action:
                            return True
        
        return False
    
    async def check_multiple_permissions(self, user_id: int, permissions: List[Dict[str, str]], require_all: bool = True) -> bool:
        """Kiểm tra nhiều permissions"""
        results = []
        for perm in permissions:
            result = await self.check_permission(user_id, perm["resource"], perm["action"])
            results.append(result)
        
        if require_all:
            return all(results)
        else:
            return any(results)
    
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
    
    async def get_user_permissions(self, user_id: int) -> List[Dict[str, str]]:
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
            return []
        
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
        
        return permissions
