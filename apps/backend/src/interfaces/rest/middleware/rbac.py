"""
RBAC Middleware - Kiểm tra quyền truy cập dựa trên RBAC
"""

from typing import List, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from core.security import verify_token
from core.db import prisma
from core.rbac import PermissionChecker


class RBACMiddleware(BaseHTTPMiddleware):
    """Middleware để kiểm tra quyền truy cập RBAC"""
    
    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.permission_checker = PermissionChecker()
        
        # Mapping các endpoint patterns với permissions cần thiết
        self.endpoint_permissions = {
            # Users API
            "GET /api/users/": {"resource": "users", "action": "read"},
            "POST /api/users/": {"resource": "users", "action": "create"},
            "GET /api/users/{user_id}": {"resource": "users", "action": "read"},
            "PUT /api/users/{user_id}": {"resource": "users", "action": "update"},
            "DELETE /api/users/{user_id}": {"resource": "users", "action": "delete"},
            
            # Groups API
            "GET /api/groups/": {"resource": "groups", "action": "read"},
            "POST /api/groups/": {"resource": "groups", "action": "create"},
            "GET /api/groups/{group_id}": {"resource": "groups", "action": "read"},
            "PUT /api/groups/{group_id}": {"resource": "groups", "action": "update"},
            "DELETE /api/groups/{group_id}": {"resource": "groups", "action": "delete"},
            "POST /api/groups/{group_id}/users/{user_id}": {"resource": "groups", "action": "update"},
            "DELETE /api/groups/{group_id}/users/{user_id}": {"resource": "groups", "action": "update"},
            "POST /api/groups/{group_id}/roles/{role_id}": {"resource": "groups", "action": "update"},
            "DELETE /api/groups/{group_id}/roles/{role_id}": {"resource": "groups", "action": "update"},
            
            # Roles API
            "GET /api/roles/": {"resource": "roles", "action": "read"},
            "POST /api/roles/": {"resource": "roles", "action": "create"},
            "GET /api/roles/{role_id}": {"resource": "roles", "action": "read"},
            "PUT /api/roles/{role_id}": {"resource": "roles", "action": "update"},
            "DELETE /api/roles/{role_id}": {"resource": "roles", "action": "delete"},
            "POST /api/roles/{role_id}/permissions/{permission_id}": {"resource": "roles", "action": "update"},
            "DELETE /api/roles/{role_id}/permissions/{permission_id}": {"resource": "roles", "action": "update"},
            
            # Permissions API
            "GET /api/permissions/": {"resource": "permissions", "action": "read"},
            "POST /api/permissions/": {"resource": "permissions", "action": "create"},
            "GET /api/permissions/{permission_id}": {"resource": "permissions", "action": "read"},
            "PUT /api/permissions/{permission_id}": {"resource": "permissions", "action": "update"},
            "DELETE /api/permissions/{permission_id}": {"resource": "permissions", "action": "delete"},
            "GET /api/permissions/resource/{resource}": {"resource": "permissions", "action": "read"},
        }
    
    async def dispatch(self, request: Request, call_next):
        """Xử lý middleware cho mỗi request"""
        
        # Kiểm tra xem path có được exclude không
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Lấy method và path để tạo endpoint pattern
        method = request.method
        path = request.url.path
        
        # Tìm permission pattern phù hợp
        permission_required = self._get_required_permission(method, path)
        
        if not permission_required:
            # Không có permission requirement, cho phép truy cập
            return await call_next(request)
        
        # Kiểm tra authentication
        user_id = await self._get_user_id_from_request(request)
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )
        
        # Kiểm tra permission
        has_permission = await self.permission_checker.check_permission(
            user_id, 
            permission_required["resource"], 
            permission_required["action"]
        )
        
        if not has_permission:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": f"Access denied. Required permission: {permission_required['action']} on {permission_required['resource']}"
                }
            )
        
        return await call_next(request)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Kiểm tra xem path có được exclude không"""
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        return False
    
    def _get_required_permission(self, method: str, path: str) -> Optional[dict]:
        """Lấy permission cần thiết cho endpoint"""
        endpoint_pattern = f"{method} {path}"
        
        # Tìm exact match trước
        if endpoint_pattern in self.endpoint_permissions:
            return self.endpoint_permissions[endpoint_pattern]
        
        # Tìm pattern match với path parameters
        for pattern, permission in self.endpoint_permissions.items():
            if self._match_pattern(pattern, endpoint_pattern):
                return permission
        
        return None
    
    def _match_pattern(self, pattern: str, endpoint: str) -> bool:
        """Kiểm tra xem endpoint có match với pattern không"""
        pattern_parts = pattern.split()
        endpoint_parts = endpoint.split()
        
        if len(pattern_parts) != len(endpoint_parts):
            return False
        
        method_pattern, path_pattern = pattern_parts
        method_endpoint, path_endpoint = endpoint_parts
        
        if method_pattern != method_endpoint:
            return False
        
        # So sánh path parts
        pattern_path_parts = path_pattern.split("/")
        endpoint_path_parts = path_endpoint.split("/")
        
        if len(pattern_path_parts) != len(endpoint_path_parts):
            return False
        
        for pattern_part, endpoint_part in zip(pattern_path_parts, endpoint_path_parts):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                # Đây là path parameter, bỏ qua
                continue
            if pattern_part != endpoint_part:
                return False
        
        return True
    
    async def _get_user_id_from_request(self, request: Request) -> Optional[int]:
        """Lấy user_id từ request"""
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None
        
        token = authorization.split(" ")[1]
        email = verify_token(token)
        if not email:
            return None
        
        try:
            # Lấy user từ email
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                return None
            
            return user.id
        except Exception as e:
            # Nếu có lỗi database connection, trả về None
            print(f"Database error in RBAC middleware: {e}")
            return None
