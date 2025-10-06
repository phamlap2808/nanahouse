from core.controllers.permission.io import PermissionCreateInput, PermissionUpdateInput, PermissionOutput, PermissionResponse, PermissionsResponse

# Examples for PermissionCreateInput
permission_create_examples = {
    "user_read": PermissionCreateInput(
        name="User Read",
        resource="users",
        action="read",
        description="Permission to read user information"
    ),
    "user_create": PermissionCreateInput(
        name="User Create",
        resource="users",
        action="create",
        description="Permission to create new users"
    ),
    "group_manage": PermissionCreateInput(
        name="Group Manage",
        resource="groups",
        action="manage",
        description="Permission to manage groups"
    )
}

# Examples for PermissionUpdateInput
permission_update_examples = {
    "update_name": PermissionUpdateInput(
        name="Updated Permission Name",
        description="Updated description"
    ),
    "update_description": PermissionUpdateInput(
        description="New description for the permission"
    )
}

# Examples for PermissionOutput
permission_output_examples = {
    "user_read": PermissionOutput(
        id=1,
        name="User Read",
        resource="users",
        action="read",
        description="Permission to read user information",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        role_permissions=[]
    ),
    "user_create": PermissionOutput(
        id=2,
        name="User Create",
        resource="users",
        action="create",
        description="Permission to create new users",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        role_permissions=[]
    )
}
