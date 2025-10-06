"""
Ví dụ sử dụng RBAC trong ứng dụng FastAPI

File này chứa các ví dụ về cách sử dụng RBAC với cấu trúc controller hiện tại
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.db import prisma
from core.rbac import RBACManager, PermissionChecker
from core.decorators import require_permission, require_admin, require_role
from core.security import verify_token
from core.controllers.user import UserController
from core.controllers.group import GroupController
from core.controllers.role import RoleController
from core.controllers.permission import PermissionController

# Khởi tạo FastAPI app
app = FastAPI(title="RBAC Example API")

# Khởi tạo controllers
user_controller = UserController()
group_controller = GroupController()
role_controller = RoleController()
permission_controller = PermissionController()

# Khởi tạo RBAC Manager
rbac_manager = RBACManager()
permission_checker = PermissionChecker()

security = HTTPBearer()


@app.on_event("startup")
async def startup_event():
    """Khởi tạo database và RBAC khi app start"""
    await prisma.connect()
    
    # Thiết lập RBAC mặc định
    await rbac_manager.setup_default_rbac()
    print("RBAC đã được khởi tạo thành công!")


@app.on_event("shutdown")
async def shutdown_event():
    """Đóng kết nối database khi app shutdown"""
    await prisma.disconnect()


# Helper function để lấy user từ token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Lấy user hiện tại từ JWT token"""
    email = verify_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = await prisma.user.find_unique(where={"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    return user


# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """Endpoint công khai"""
    return {"message": "Chào mừng đến với RBAC API!"}


# ==================== USER ENDPOINTS ====================

@app.get("/users")
@require_permission("users", "read")
async def get_users():
    """Lấy danh sách users - yêu cầu quyền read users"""
    return await user_controller.list()


@app.post("/users")
@require_permission("users", "create")
async def create_user(user_data: dict):
    """Tạo user mới - yêu cầu quyền create users"""
    return await user_controller.create(**user_data)


@app.get("/users/{user_id}")
@require_permission("users", "read")
async def get_user(user_id: int):
    """Lấy thông tin user - yêu cầu quyền read users"""
    return await user_controller.get(user_id)


@app.put("/users/{user_id}")
@require_permission("users", "update")
async def update_user(user_id: int, user_data: dict):
    """Cập nhật user - yêu cầu quyền update users"""
    return await user_controller.update(user_id, **user_data)


@app.delete("/users/{user_id}")
@require_permission("users", "delete")
async def delete_user(user_id: int):
    """Xóa user - yêu cầu quyền delete users"""
    return await user_controller.delete(user_id)


@app.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: int, current_user = Depends(get_current_user)):
    """Lấy permissions của user - chỉ admin hoặc chính user đó"""
    # Kiểm tra quyền: admin hoặc chính user đó
    if not (await permission_checker.is_admin(current_user.id) or current_user.id == user_id):
        raise HTTPException(status_code=403, detail="Không có quyền xem permissions")
    
    return await user_controller.get_permissions(user_id)


# ==================== GROUP ENDPOINTS ====================

@app.get("/groups")
@require_permission("groups", "read")
async def get_groups():
    """Lấy danh sách groups"""
    return await group_controller.list()


@app.post("/groups")
@require_admin()
async def create_group(group_data: dict):
    """Tạo group mới - chỉ admin"""
    return await group_controller.create(**group_data)


@app.get("/groups/{group_id}")
@require_permission("groups", "read")
async def get_group(group_id: int):
    """Lấy thông tin group"""
    return await group_controller.get(group_id)


@app.put("/groups/{group_id}")
@require_admin()
async def update_group(group_id: int, group_data: dict):
    """Cập nhật group - chỉ admin"""
    return await group_controller.update(group_id, **group_data)


@app.delete("/groups/{group_id}")
@require_admin()
async def delete_group(group_id: int):
    """Xóa group - chỉ admin"""
    return await group_controller.delete(group_id)


@app.post("/groups/{group_id}/users/{user_id}")
@require_admin()
async def add_user_to_group(group_id: int, user_id: int):
    """Thêm user vào group - chỉ admin"""
    return await group_controller.add_user(group_id, user_id)


@app.delete("/groups/{group_id}/users/{user_id}")
@require_admin()
async def remove_user_from_group(group_id: int, user_id: int):
    """Xóa user khỏi group - chỉ admin"""
    return await group_controller.remove_user(group_id, user_id)


@app.post("/groups/{group_id}/roles/{role_id}")
@require_admin()
async def assign_role_to_group(group_id: int, role_id: int):
    """Gán role cho group - chỉ admin"""
    return await group_controller.assign_role(group_id, role_id)


@app.delete("/groups/{group_id}/roles/{role_id}")
@require_admin()
async def remove_role_from_group(group_id: int, role_id: int):
    """Xóa role khỏi group - chỉ admin"""
    return await group_controller.remove_role(group_id, role_id)


# ==================== ROLE ENDPOINTS ====================

@app.get("/roles")
@require_permission("roles", "read")
async def get_roles():
    """Lấy danh sách roles"""
    return await role_controller.list()


@app.post("/roles")
@require_admin()
async def create_role(role_data: dict):
    """Tạo role mới - chỉ admin"""
    return await role_controller.create(**role_data)


@app.get("/roles/{role_id}")
@require_permission("roles", "read")
async def get_role(role_id: int):
    """Lấy thông tin role"""
    return await role_controller.get(role_id)


@app.put("/roles/{role_id}")
@require_admin()
async def update_role(role_id: int, role_data: dict):
    """Cập nhật role - chỉ admin"""
    return await role_controller.update(role_id, **role_data)


@app.delete("/roles/{role_id}")
@require_admin()
async def delete_role(role_id: int):
    """Xóa role - chỉ admin"""
    return await role_controller.delete(role_id)


@app.post("/roles/{role_id}/permissions/{permission_id}")
@require_admin()
async def assign_permission_to_role(role_id: int, permission_id: int):
    """Gán permission cho role - chỉ admin"""
    return await role_controller.assign_permission(role_id, permission_id)


@app.delete("/roles/{role_id}/permissions/{permission_id}")
@require_admin()
async def remove_permission_from_role(role_id: int, permission_id: int):
    """Xóa permission khỏi role - chỉ admin"""
    return await role_controller.remove_permission(role_id, permission_id)


# ==================== PERMISSION ENDPOINTS ====================

@app.get("/permissions")
@require_permission("permissions", "read")
async def get_permissions():
    """Lấy danh sách permissions"""
    return await permission_controller.list()


@app.post("/permissions")
@require_admin()
async def create_permission(permission_data: dict):
    """Tạo permission mới - chỉ admin"""
    return await permission_controller.create(**permission_data)


@app.get("/permissions/{permission_id}")
@require_permission("permissions", "read")
async def get_permission(permission_id: int):
    """Lấy thông tin permission"""
    return await permission_controller.get(permission_id)


@app.put("/permissions/{permission_id}")
@require_admin()
async def update_permission(permission_id: int, permission_data: dict):
    """Cập nhật permission - chỉ admin"""
    return await permission_controller.update(permission_id, **permission_data)


@app.delete("/permissions/{permission_id}")
@require_admin()
async def delete_permission(permission_id: int):
    """Xóa permission - chỉ admin"""
    return await permission_controller.delete(permission_id)


# ==================== USER PERMISSION CHECK ENDPOINTS ====================

@app.get("/me/permissions")
async def get_my_permissions(current_user = Depends(get_current_user)):
    """Lấy permissions của user hiện tại"""
    permissions = await permission_checker.get_user_permissions(current_user.id)
    return {"permissions": permissions}


@app.post("/me/check-permission")
async def check_my_permission(permission_data: dict, current_user = Depends(get_current_user)):
    """Kiểm tra permission cụ thể của user hiện tại"""
    has_permission = await permission_checker.check_permission(
        current_user.id, 
        permission_data["resource"], 
        permission_data["action"]
    )
    return {"has_permission": has_permission}


@app.get("/me/is-admin")
async def check_my_admin_status(current_user = Depends(get_current_user)):
    """Kiểm tra user hiện tại có phải admin không"""
    is_admin = await permission_checker.is_admin(current_user.id)
    return {"is_admin": is_admin}


# ==================== ADMIN DASHBOARD ====================

@app.get("/admin/dashboard")
@require_admin()
async def admin_dashboard():
    """Dashboard admin - chỉ admin mới truy cập được"""
    return {"message": "Chào mừng admin!", "data": "Dữ liệu admin"}


# ==================== EXAMPLE USAGE ====================

"""
Cách sử dụng RBAC trong ứng dụng:

1. Khởi tạo RBAC:
   - Chạy migration để tạo tables
   - Gọi setup_default_rbac() để tạo dữ liệu mặc định

2. Sử dụng decorators:
   - @require_permission("users", "read") - yêu cầu quyền read users
   - @require_admin() - chỉ admin mới truy cập được
   - @require_role("admin") - yêu cầu role admin

3. Kiểm tra quyền trong code:
   - permission_checker.check_permission(user_id, "users", "read")
   - permission_checker.is_admin(user_id)

4. Quản lý RBAC:
   - Tạo groups, roles, permissions
   - Gán users vào groups
   - Gán roles cho groups
   - Gán permissions cho roles

5. Cấu trúc quyền:
   - User -> Group -> Roles -> Permissions
   - Nếu user.isAdmin = True hoặc group.isAdmin = True thì có tất cả quyền
   - Permissions được định nghĩa theo resource + action (ví dụ: "users" + "read")

6. Sử dụng với controllers:
   - Mỗi controller có các method CRUD cơ bản
   - Có thể extend thêm các method đặc biệt cho RBAC
   - Sử dụng decorators để bảo vệ endpoints
"""
