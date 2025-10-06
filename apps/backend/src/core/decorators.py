"""
RBAC Decorators - Các decorator để kiểm tra quyền truy cập
"""

from typing import Callable, Optional, List, Dict, Any
from functools import wraps
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.db import prisma
from core.security import verify_token
from core.rbac import PermissionChecker

security = HTTPBearer()


def get_user_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Lấy user_id từ JWT token"""
    email = verify_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    # Tìm user theo email để lấy user_id
    # Cần implement async function để lấy user_id
    # Tạm thời return 0, sẽ được implement trong auth controller
    return 0


def require_permission(resource: str, action: str):
    """
    Decorator để yêu cầu permission cụ thể
    
    Args:
        resource: Tài nguyên cần kiểm tra (ví dụ: "users", "groups")
        action: Hành động cần kiểm tra (ví dụ: "create", "read", "update", "delete")
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Tìm request trong args hoặc kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không thể lấy request object"
                )
            
            # Lấy user_id từ token
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            token = authorization.split(" ")[1]
            email = verify_token(token)
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            # Lấy user từ email
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User không tồn tại"
                )
            
            # Kiểm tra permission
            permission_checker = PermissionChecker()
            has_permission = await permission_checker.check_permission(
                user.id, resource, action
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Không có quyền {action} trên {resource}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_admin():
    """
    Decorator để yêu cầu quyền admin
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Tìm request trong args hoặc kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không thể lấy request object"
                )
            
            # Lấy user_id từ token
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            token = authorization.split(" ")[1]
            email = verify_token(token)
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            # Lấy user từ email
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User không tồn tại"
                )
            
            # Kiểm tra admin
            permission_checker = PermissionChecker()
            is_admin = await permission_checker.is_admin(user.id)
            
            if not is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Chỉ admin mới có quyền truy cập"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_role(role_name: str):
    """
    Decorator để yêu cầu role cụ thể
    
    Args:
        role_name: Tên role cần kiểm tra
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Tìm request trong args hoặc kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không thể lấy request object"
                )
            
            # Lấy user_id từ token
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            token = authorization.split(" ")[1]
            email = verify_token(token)
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            # Lấy user từ email
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User không tồn tại"
                )
            
            # Kiểm tra role
            has_role = await _check_user_has_role(user.id, role_name)
            
            if not has_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Không có role '{role_name}'"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_any_permission(permissions: List[Dict[str, str]]):
    """
    Decorator để yêu cầu ít nhất một trong các permissions
    
    Args:
        permissions: Danh sách permissions cần kiểm tra
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Tìm request trong args hoặc kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không thể lấy request object"
                )
            
            # Lấy user_id từ token
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            token = authorization.split(" ")[1]
            email = verify_token(token)
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            # Lấy user từ email
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User không tồn tại"
                )
            
            # Kiểm tra permissions
            permission_checker = PermissionChecker()
            has_permission = await permission_checker.check_multiple_permissions(
                user.id, permissions, require_all=False
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không có quyền truy cập"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_all_permissions(permissions: List[Dict[str, str]]):
    """
    Decorator để yêu cầu tất cả các permissions
    
    Args:
        permissions: Danh sách permissions cần kiểm tra
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Tìm request trong args hoặc kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không thể lấy request object"
                )
            
            # Lấy user_id từ token
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            token = authorization.split(" ")[1]
            email = verify_token(token)
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token không hợp lệ"
                )
            
            # Lấy user từ email
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User không tồn tại"
                )
            
            # Kiểm tra permissions
            permission_checker = PermissionChecker()
            has_permission = await permission_checker.check_multiple_permissions(
                user.id, permissions, require_all=True
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Không có đủ quyền truy cập"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Helper functions
async def _check_user_has_role(user_id: int, role_name: str) -> bool:
    """Kiểm tra user có role cụ thể không"""
    user = await prisma.user.find_unique(
        where={"id": user_id},
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
    
    if not user:
        return False
    
    # Nếu user là admin hoặc group có isAdmin = True
    if user.get("isAdmin") or (user.get("group") and user["group"].get("isAdmin")):
        return True
    
    # Kiểm tra role trong group
    if user.get("group") and user["group"].get("groupRoles"):
        for group_role in user["group"]["groupRoles"]:
            role = group_role.get("role")
            if role and role.get("name") == role_name:
                return True
    
    return False
