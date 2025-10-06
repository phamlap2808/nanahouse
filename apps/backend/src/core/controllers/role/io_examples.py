from core.controllers.role.io import RoleCreateInput, RoleUpdateInput, RoleOutput, RoleResponse, RolesResponse

# Examples for RoleCreateInput
role_create_examples = {
    "admin_role": RoleCreateInput(
        name="Administrator",
        description="Role for system administrators"
    ),
    "user_role": RoleCreateInput(
        name="User",
        description="Role for regular users"
    ),
    "moderator_role": RoleCreateInput(
        name="Moderator",
        description="Role for content moderators"
    )
}

# Examples for RoleUpdateInput
role_update_examples = {
    "update_name": RoleUpdateInput(
        name="Updated Role Name",
        description="Updated description"
    ),
    "update_description": RoleUpdateInput(
        description="New description for the role"
    )
}

# Examples for RoleOutput
role_output_examples = {
    "admin_role": RoleOutput(
        id=1,
        name="Administrator",
        description="Role for system administrators",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        role_permissions=[],
        group_roles=[]
    ),
    "user_role": RoleOutput(
        id=2,
        name="User",
        description="Role for regular users",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        role_permissions=[],
        group_roles=[]
    )
}
