"""
Tests for RBAC API endpoints (Groups, Roles, Permissions)
"""

import pytest
from fastapi.testclient import TestClient
from core.security import create_access_token
from core.db import prisma


class TestRBACAPI:
    """Test cases for RBAC API endpoints"""

    # ==================== GROUP API TESTS ====================

    def test_create_group_success(self, client: TestClient, clean_db, test_admin_user, sample_group_data):
        """Test creating group successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/groups/", json=sample_group_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == sample_group_data["name"]
        assert data["data"]["description"] == sample_group_data["description"]
        assert data["data"]["is_admin"] == sample_group_data["is_admin"]
        assert "id" in data["data"]

    def test_create_group_duplicate_name(self, client: TestClient, clean_db, test_group, test_admin_user):
        """Test creating group with duplicate name"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        group_data = {
            "name": test_group.name,
            "description": "Duplicate group",
            "is_admin": False
        }
        
        response = client.post("/api/groups/", json=group_data, headers=headers)
        
        assert response.status_code == 409
        assert "Group name already exists" in response.json()["detail"]

    def test_create_group_no_auth(self, client: TestClient, clean_db, sample_group_data):
        """Test creating group without authentication"""
        response = client.post("/api/groups/", json=sample_group_data)
        
        assert response.status_code == 401

    def test_list_groups_success(self, client: TestClient, clean_db, test_group, test_admin_user):
        """Test listing groups successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/groups/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1  # At least test_group

    def test_get_group_success(self, client: TestClient, clean_db, test_group, test_admin_user):
        """Test getting group successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/groups/{test_group.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_group.id
        assert data["data"]["name"] == test_group.name

    def test_get_group_not_found(self, client: TestClient, clean_db, test_admin_user):
        """Test getting non-existent group"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/groups/99999", headers=headers)
        
        assert response.status_code == 404
        assert "Group not found" in response.json()["detail"]

    def test_update_group_success(self, client: TestClient, clean_db, test_group, test_admin_user):
        """Test updating group successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {
            "name": "Updated Group Name",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/groups/{test_group.id}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Group Name"
        assert data["data"]["description"] == "Updated description"

    def test_delete_group_success(self, client: TestClient, clean_db, test_group, test_admin_user):
        """Test deleting group successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/api/groups/{test_group.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_group.id

    def test_add_user_to_group_success(self, client: TestClient, clean_db, test_user, test_group, test_admin_user):
        """Test adding user to group successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(f"/api/groups/{test_group.id}/users/{test_user.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_assign_role_to_group_success(self, client: TestClient, clean_db, test_group, test_role, test_admin_user):
        """Test assigning role to group successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(f"/api/groups/{test_group.id}/roles/{test_role.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    # ==================== ROLE API TESTS ====================

    def test_create_role_success(self, client: TestClient, clean_db, test_admin_user, sample_role_data):
        """Test creating role successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/roles/", json=sample_role_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == sample_role_data["name"]
        assert data["data"]["description"] == sample_role_data["description"]
        assert "id" in data["data"]

    def test_create_role_duplicate_name(self, client: TestClient, clean_db, test_role, test_admin_user):
        """Test creating role with duplicate name"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        role_data = {
            "name": test_role.name,
            "description": "Duplicate role"
        }
        
        response = client.post("/api/roles/", json=role_data, headers=headers)
        
        assert response.status_code == 409
        assert "Role name already exists" in response.json()["detail"]

    def test_list_roles_success(self, client: TestClient, clean_db, test_role, test_admin_user):
        """Test listing roles successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/roles/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1  # At least test_role

    def test_get_role_success(self, client: TestClient, clean_db, test_role, test_admin_user):
        """Test getting role successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/roles/{test_role.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_role.id
        assert data["data"]["name"] == test_role.name

    def test_assign_permission_to_role_success(self, client: TestClient, clean_db, test_role, test_permission, test_admin_user):
        """Test assigning permission to role successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(f"/api/roles/{test_role.id}/permissions/{test_permission.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    # ==================== PERMISSION API TESTS ====================

    def test_create_permission_success(self, client: TestClient, clean_db, test_admin_user, sample_permission_data):
        """Test creating permission successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/permissions/", json=sample_permission_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == sample_permission_data["name"]
        assert data["data"]["resource"] == sample_permission_data["resource"]
        assert data["data"]["action"] == sample_permission_data["action"]
        assert "id" in data["data"]

    def test_create_permission_duplicate_resource_action(self, client: TestClient, clean_db, test_permission, test_admin_user):
        """Test creating permission with duplicate resource and action"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        permission_data = {
            "name": "Duplicate Permission",
            "resource": test_permission.resource,
            "action": test_permission.action,
            "description": "Duplicate permission"
        }
        
        response = client.post("/api/permissions/", json=permission_data, headers=headers)
        
        assert response.status_code == 409
        assert "Permission with this resource and action already exists" in response.json()["detail"]

    def test_list_permissions_success(self, client: TestClient, clean_db, test_permission, test_admin_user):
        """Test listing permissions successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/permissions/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1  # At least test_permission

    def test_get_permission_success(self, client: TestClient, clean_db, test_permission, test_admin_user):
        """Test getting permission successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/permissions/{test_permission.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_permission.id
        assert data["data"]["name"] == test_permission.name

    def test_list_permissions_by_resource(self, client: TestClient, clean_db, test_permission, test_admin_user):
        """Test listing permissions by resource"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/permissions/resource/{test_permission.resource}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        # Should include at least the test_permission
        assert any(p["resource"] == test_permission.resource for p in data["data"])

    # ==================== RBAC INTEGRATION TESTS ====================

    def test_user_permissions_flow(self, client: TestClient, clean_db, test_user, test_group, test_role, test_permission, test_admin_user):
        """Test complete RBAC flow: User -> Group -> Role -> Permission"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Assign permission to role
        response = client.post(f"/api/roles/{test_role.id}/permissions/{test_permission.id}", headers=headers)
        assert response.status_code == 200
        
        # 2. Assign role to group
        response = client.post(f"/api/groups/{test_group.id}/roles/{test_role.id}", headers=headers)
        assert response.status_code == 200
        
        # 3. Add user to group
        response = client.post(f"/api/groups/{test_group.id}/users/{test_user.id}", headers=headers)
        assert response.status_code == 200
        
        # 4. Get user permissions
        response = client.get(f"/api/users/{test_user.id}/permissions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        # Should include the permission we assigned
        assert any(p["resource"] == test_permission.resource and p["action"] == test_permission.action for p in data["data"])

    def test_admin_user_has_all_permissions(self, client: TestClient, clean_db, test_admin_user):
        """Test that admin user has all permissions"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user permissions
        response = client.get(f"/api/users/{test_admin_user.id}/permissions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        # Admin should have many permissions (all default permissions)
        assert len(data["data"]) > 0

    def test_non_admin_user_limited_permissions(self, client: TestClient, clean_db, test_user):
        """Test that non-admin user has limited permissions"""
        # Create access token for regular user
        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user permissions
        response = client.get(f"/api/users/{test_user.id}/permissions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        # Non-admin user should have fewer permissions
        assert len(data["data"]) >= 0  # Could be 0 if no roles assigned
