"""
Test utilities and helper functions
"""

import pytest
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient
from core.security import create_access_token
from core.db import prisma


class TestUtils:
    """Utility functions for testing"""

    @staticmethod
    def create_auth_headers(email: str) -> Dict[str, str]:
        """Create authorization headers for a user"""
        token = create_access_token(data={"sub": email})
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    async def create_test_user(email: str = "test@example.com", name: str = "Test User", 
                             password: str = "hashed_password", status: str = "active",
                             group_id: Optional[int] = None, is_admin: bool = False) -> Dict[str, Any]:
        """Create a test user"""
        user_data = {
            "email": email,
            "name": name,
            "password": password,
            "status": status
        }
        if group_id is not None:
            user_data["groupId"] = group_id
        if is_admin:
            user_data["isAdmin"] = is_admin
            
        user = await prisma.user.create(data=user_data)
        return user.model_dump()

    @staticmethod
    async def create_test_group(name: str = "Test Group", description: str = "Test group description",
                              is_admin: bool = False) -> Dict[str, Any]:
        """Create a test group"""
        group = await prisma.group.create(data={
            "name": name,
            "description": description,
            "isAdmin": is_admin
        })
        return group.model_dump()

    @staticmethod
    async def create_test_role(name: str = "test_role", description: str = "Test role description") -> Dict[str, Any]:
        """Create a test role"""
        role = await prisma.role.create(data={
            "name": name,
            "description": description
        })
        return role.model_dump()

    @staticmethod
    async def create_test_permission(name: str = "test_permission", resource: str = "test_resource",
                                   action: str = "read", description: str = "Test permission") -> Dict[str, Any]:
        """Create a test permission"""
        permission = await prisma.permission.create(data={
            "name": name,
            "resource": resource,
            "action": action,
            "description": description
        })
        return permission.model_dump()

    @staticmethod
    async def assign_user_to_group(user_id: int, group_id: int) -> bool:
        """Assign user to group"""
        try:
            await prisma.user.update(
                where={"id": user_id},
                data={"groupId": group_id}
            )
            return True
        except Exception:
            return False

    @staticmethod
    async def assign_role_to_group(group_id: int, role_id: int) -> bool:
        """Assign role to group"""
        try:
            await prisma.grouprole.create(data={
                "groupId": group_id,
                "roleId": role_id
            })
            return True
        except Exception:
            return False

    @staticmethod
    async def assign_permission_to_role(role_id: int, permission_id: int) -> bool:
        """Assign permission to role"""
        try:
            await prisma.rolepermission.create(data={
                "roleId": role_id,
                "permissionId": permission_id
            })
            return True
        except Exception:
            return False

    @staticmethod
    async def setup_rbac_chain(user_id: int, group_id: int, role_id: int, permission_id: int) -> bool:
        """Setup complete RBAC chain: User -> Group -> Role -> Permission"""
        try:
            # Assign user to group
            await TestUtils.assign_user_to_group(user_id, group_id)
            
            # Assign role to group
            await TestUtils.assign_role_to_group(group_id, role_id)
            
            # Assign permission to role
            await TestUtils.assign_permission_to_role(role_id, permission_id)
            
            return True
        except Exception:
            return False

    @staticmethod
    def assert_success_response(response_data: Dict[str, Any], expected_data_keys: Optional[list] = None):
        """Assert that response is a success response"""
        assert response_data.get("success") is True
        assert "data" in response_data
        assert response_data.get("error") is None
        
        if expected_data_keys:
            for key in expected_data_keys:
                assert key in response_data["data"]

    @staticmethod
    def assert_error_response(response_data: Dict[str, Any], expected_status_code: int = None):
        """Assert that response is an error response"""
        if expected_status_code:
            assert response_data.get("status_code") == expected_status_code
        assert response_data.get("success") is False or "detail" in response_data

    @staticmethod
    def assert_user_data(user_data: Dict[str, Any], expected_email: str, expected_name: str = None):
        """Assert user data structure"""
        assert user_data["email"] == expected_email
        if expected_name:
            assert user_data["name"] == expected_name
        assert "id" in user_data
        assert "status" in user_data
        assert "created_at" in user_data
        assert "updated_at" in user_data

    @staticmethod
    def assert_group_data(group_data: Dict[str, Any], expected_name: str, expected_description: str = None):
        """Assert group data structure"""
        assert group_data["name"] == expected_name
        if expected_description:
            assert group_data["description"] == expected_description
        assert "id" in group_data
        assert "is_admin" in group_data
        assert "created_at" in group_data
        assert "updated_at" in group_data

    @staticmethod
    def assert_role_data(role_data: Dict[str, Any], expected_name: str, expected_description: str = None):
        """Assert role data structure"""
        assert role_data["name"] == expected_name
        if expected_description:
            assert role_data["description"] == expected_description
        assert "id" in role_data
        assert "created_at" in role_data
        assert "updated_at" in role_data

    @staticmethod
    def assert_permission_data(permission_data: Dict[str, Any], expected_name: str, 
                             expected_resource: str, expected_action: str):
        """Assert permission data structure"""
        assert permission_data["name"] == expected_name
        assert permission_data["resource"] == expected_resource
        assert permission_data["action"] == expected_action
        assert "id" in permission_data
        assert "created_at" in permission_data
        assert "updated_at" in permission_data


class TestDataFactory:
    """Factory for creating test data"""

    @staticmethod
    def get_sample_user_data(email: str = "sample@example.com", name: str = "Sample User") -> Dict[str, Any]:
        """Get sample user data"""
        return {
            "email": email,
            "password": "Password123!",
            "name": name,
            "group_id": None,
            "is_admin": False
        }

    @staticmethod
    def get_sample_group_data(name: str = "Sample Group", description: str = "Sample group description") -> Dict[str, Any]:
        """Get sample group data"""
        return {
            "name": name,
            "description": description,
            "is_admin": False
        }

    @staticmethod
    def get_sample_role_data(name: str = "sample_role", description: str = "Sample role description") -> Dict[str, Any]:
        """Get sample role data"""
        return {
            "name": name,
            "description": description
        }

    @staticmethod
    def get_sample_permission_data(name: str = "sample_permission", resource: str = "sample_resource",
                                 action: str = "read", description: str = "Sample permission") -> Dict[str, Any]:
        """Get sample permission data"""
        return {
            "name": name,
            "resource": resource,
            "action": action,
            "description": description
        }

    @staticmethod
    def get_invalid_user_data() -> Dict[str, Any]:
        """Get invalid user data for testing validation"""
        return {
            "email": "invalid-email",
            "password": "123",  # Too short
            "name": "Test User"
        }

    @staticmethod
    def get_invalid_group_data() -> Dict[str, Any]:
        """Get invalid group data for testing validation"""
        return {
            "name": "",  # Empty name
            "description": "Test description"
        }

    @staticmethod
    def get_invalid_role_data() -> Dict[str, Any]:
        """Get invalid role data for testing validation"""
        return {
            "name": "",  # Empty name
            "description": "Test description"
        }

    @staticmethod
    def get_invalid_permission_data() -> Dict[str, Any]:
        """Get invalid permission data for testing validation"""
        return {
            "name": "test_permission",
            "resource": "test_resource",
            "action": "invalid_action",  # Invalid action
            "description": "Test permission"
        }


# Pytest fixtures for common test scenarios
@pytest.fixture
def test_utils():
    """Provide TestUtils class"""
    return TestUtils


@pytest.fixture
def test_data_factory():
    """Provide TestDataFactory class"""
    return TestDataFactory


@pytest.fixture
async def complete_rbac_setup(test_db):
    """Create a complete RBAC setup for testing"""
    # Create user
    user = await TestUtils.create_test_user(email="rbacuser@example.com")
    
    # Create group
    group = await TestUtils.create_test_group(name="RBAC Test Group")
    
    # Create role
    role = await TestUtils.create_test_role(name="rbac_test_role")
    
    # Create permission
    permission = await TestUtils.create_test_permission(
        name="rbac_test_permission",
        resource="rbac_test_resource",
        action="read"
    )
    
    # Setup RBAC chain
    await TestUtils.setup_rbac_chain(
        user["id"], group["id"], role["id"], permission["id"]
    )
    
    return {
        "user": user,
        "group": group,
        "role": role,
        "permission": permission
    }


@pytest.fixture
async def admin_user_setup(test_db):
    """Create admin user setup for testing"""
    # Create admin group
    admin_group = await TestUtils.create_test_group(
        name="Admin Group",
        is_admin=True
    )
    
    # Create admin user
    admin_user = await TestUtils.create_test_user(
        email="admin@example.com",
        name="Admin User",
        is_admin=True
    )
    
    # Assign user to admin group
    await TestUtils.assign_user_to_group(admin_user["id"], admin_group["id"])
    
    return {
        "user": admin_user,
        "group": admin_group
    }
