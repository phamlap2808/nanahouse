# RBAC Implementation - Role-Based Access Control

Hệ thống RBAC (Role-Based Access Control) được tích hợp vào cấu trúc controller hiện tại của ứng dụng FastAPI với Prisma.

## Cấu trúc

```
src/
├── core/
│   ├── controllers/
│   │   ├── user/           # User controller với RBAC
│   │   ├── group/          # Group controller
│   │   ├── role/           # Role controller  
│   │   └── permission/      # Permission controller
│   ├── rbac.py             # RBAC utilities
│   └── decorators.py       # RBAC decorators
├── rbac_example.py         # Ví dụ sử dụng
└── prisma/
    └── schema.prisma       # Database schema với RBAC
```

## Schema Database

Module này sử dụng các bảng sau:

- **User**: Người dùng với liên kết đến Group và isAdmin flag
- **Group**: Nhóm người dùng, có thể có isAdmin = True
- **Role**: Vai trò định nghĩa các quyền
- **Permission**: Quyền cụ thể theo resource + action
- **GroupRole**: Liên kết nhiều-nhiều giữa Group và Role
- **RolePermission**: Liên kết nhiều-nhiều giữa Role và Permission

## Controllers

### UserController
- `create()` - Tạo user với group_id và is_admin
- `get()` - Lấy user với thông tin group và roles
- `list()` - Lấy danh sách users với group info
- `update()` - Cập nhật user, group_id, is_admin
- `delete()` - Xóa user
- `get_permissions()` - Lấy tất cả permissions của user
- `check_permission()` - Kiểm tra permission cụ thể
- `is_admin()` - Kiểm tra user có phải admin

### GroupController
- `create()` - Tạo group mới
- `get()` - Lấy group với users và roles
- `list()` - Lấy danh sách groups
- `update()` - Cập nhật group
- `delete()` - Xóa group
- `add_user()` - Thêm user vào group
- `remove_user()` - Xóa user khỏi group
- `assign_role()` - Gán role cho group
- `remove_role()` - Xóa role khỏi group

### RoleController
- `create()` - Tạo role mới
- `get()` - Lấy role với permissions và groups
- `list()` - Lấy danh sách roles
- `update()` - Cập nhật role
- `delete()` - Xóa role
- `assign_permission()` - Gán permission cho role
- `remove_permission()` - Xóa permission khỏi role

### PermissionController
- `create()` - Tạo permission mới
- `get()` - Lấy permission với roles
- `list()` - Lấy danh sách permissions
- `list_by_resource()` - Lấy permissions theo resource
- `update()` - Cập nhật permission
- `delete()` - Xóa permission

## RBAC Utilities

### RBACManager
- `initialize_default_permissions()` - Tạo permissions mặc định
- `create_default_roles()` - Tạo roles mặc định
- `create_default_groups()` - Tạo groups mặc định
- `assign_permissions_to_role()` - Gán permissions cho role
- `assign_roles_to_group()` - Gán roles cho group
- `setup_default_rbac()` - Thiết lập RBAC hoàn chỉnh

### PermissionChecker
- `check_permission()` - Kiểm tra permission cụ thể
- `check_multiple_permissions()` - Kiểm tra nhiều permissions
- `is_admin()` - Kiểm tra admin status
- `get_user_permissions()` - Lấy tất cả permissions của user

## Decorators

### @require_permission(resource, action)
Yêu cầu permission cụ thể để truy cập endpoint.

```python
@app.get("/users")
@require_permission("users", "read")
async def get_users():
    return await user_controller.list()
```

### @require_admin()
Chỉ admin mới có thể truy cập endpoint.

```python
@app.post("/groups")
@require_admin()
async def create_group(group_data: dict):
    return await group_controller.create(**group_data)
```

### @require_role(role_name)
Yêu cầu role cụ thể để truy cập endpoint.

```python
@app.get("/admin/users")
@require_role("admin")
async def admin_users():
    return await user_controller.list()
```

### @require_any_permission(permissions)
Yêu cầu ít nhất một trong các permissions.

### @require_all_permissions(permissions)
Yêu cầu tất cả các permissions.

## Cách sử dụng

### 1. Khởi tạo

```python
from core.rbac import RBACManager
from core.db import prisma

# Khởi tạo RBAC Manager
rbac_manager = RBACManager()

# Thiết lập RBAC mặc định
await rbac_manager.setup_default_rbac()
```

### 2. Sử dụng Controllers

```python
from core.controllers.user import UserController
from core.controllers.group import GroupController

user_controller = UserController()
group_controller = GroupController()

# Tạo user với group
user = await user_controller.create(
    email="user@example.com",
    password="password123",
    name="John Doe",
    group_id=1,
    is_admin=False
)

# Tạo group
group = await group_controller.create(
    name="Admins",
    description="Administrator group",
    is_admin=True
)
```

### 3. Kiểm tra quyền

```python
from core.rbac import PermissionChecker

permission_checker = PermissionChecker()

# Kiểm tra permission
has_permission = await permission_checker.check_permission(
    user_id, "users", "read"
)

# Kiểm tra admin
is_admin = await permission_checker.is_admin(user_id)

# Lấy tất cả permissions
permissions = await permission_checker.get_user_permissions(user_id)
```

### 4. Sử dụng Decorators

```python
from core.decorators import require_permission, require_admin

@app.get("/users")
@require_permission("users", "read")
async def get_users():
    return await user_controller.list()

@app.post("/groups")
@require_admin()
async def create_group(group_data: dict):
    return await group_controller.create(**group_data)
```

## Permissions mặc định

Module tự động tạo các permissions mặc định:

- **users**: create, read, update, delete
- **groups**: create, read, update, delete  
- **roles**: create, read, update, delete
- **permissions**: create, read, update, delete

## Roles mặc định

- **super_admin**: Có tất cả quyền
- **admin**: Quản lý users và groups
- **moderator**: Quản lý nội dung
- **user**: Người dùng thông thường

## Groups mặc định

- **super_admins**: Nhóm quản trị viên cấp cao (isAdmin = True)
- **admins**: Nhóm quản trị viên
- **users**: Nhóm người dùng thông thường

## Migration

Chạy migration để tạo các bảng RBAC:

```bash
prisma migrate dev --name add_rbac
```

## Cấu trúc quyền

1. **User** thuộc về một **Group**
2. **Group** có thể có nhiều **Roles**
3. **Role** có thể có nhiều **Permissions**
4. **Permission** được định nghĩa theo `resource` + `action`
5. Nếu `user.isAdmin = True` hoặc `group.isAdmin = True` thì có tất cả quyền

## Lưu ý

1. Decorators tự động lấy user từ JWT token trong Authorization header
2. Tất cả các thao tác RBAC đều có error handling
3. Sử dụng cascade delete để đảm bảo tính toàn vẹn dữ liệu
4. Controllers tuân theo pattern hiện tại với `controller.py`, `io.py`, `io_examples.py`
5. RBAC utilities được đặt trong `core/rbac.py` và `core/decorators.py`

## Ví dụ hoàn chỉnh

Xem file `rbac_example.py` để có ví dụ đầy đủ về cách sử dụng RBAC với FastAPI endpoints.
