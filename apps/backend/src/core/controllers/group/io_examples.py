from core.controllers.group.io import GroupCreateInput, GroupUpdateInput, GroupOutput, GroupResponse, GroupsResponse

# Examples for GroupCreateInput
group_create_examples = {
    "admin_group": GroupCreateInput(
        name="Administrators",
        description="Group for system administrators",
        is_admin=True
    ),
    "user_group": GroupCreateInput(
        name="Regular Users",
        description="Group for regular users",
        is_admin=False
    ),
    "moderator_group": GroupCreateInput(
        name="Moderators",
        description="Group for content moderators",
        is_admin=False
    )
}

# Examples for GroupUpdateInput
group_update_examples = {
    "update_name": GroupUpdateInput(
        name="Updated Group Name",
        description="Updated description"
    ),
    "update_admin": GroupUpdateInput(
        is_admin=True
    ),
    "update_description": GroupUpdateInput(
        description="New description for the group"
    )
}

# Examples for GroupOutput
group_output_examples = {
    "admin_group": GroupOutput(
        id=1,
        name="Administrators",
        description="Group for system administrators",
        is_admin=True,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        users=[],
        group_roles=[]
    ),
    "user_group": GroupOutput(
        id=2,
        name="Regular Users",
        description="Group for regular users",
        is_admin=False,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        users=[],
        group_roles=[]
    )
}
