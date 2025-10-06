"""
Integration and End-to-End tests
"""

import pytest
from fastapi.testclient import TestClient
from core.security import create_access_token
from core.db import prisma
from test_utils import TestUtils, TestDataFactory


class TestIntegration:
    """Integration tests for the entire system"""

    def test_complete_user_lifecycle(self, client: TestClient, clean_db, test_admin_user):
        """Test complete user lifecycle: create -> read -> update -> delete"""
        # Create auth headers
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Create user
        user_data = TestDataFactory.get_sample_user_data()
        response = client.post("/api/users/", json=user_data, headers=headers)
        assert response.status_code == 200
        created_user = response.json()["data"]
        
        # 2. Read user
        response = client.get(f"/api/users/{created_user['id']}", headers=headers)
        assert response.status_code == 200
        read_user = response.json()["data"]
        assert read_user["email"] == user_data["email"]
        
        # 3. Update user
        update_data = {"name": "Updated Name"}
        response = client.put(f"/api/users/{created_user['id']}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_user = response.json()["data"]
        assert updated_user["name"] == "Updated Name"
        
        # 4. Delete user
        response = client.delete(f"/api/users/{created_user['id']}", headers=headers)
        assert response.status_code == 200
        
        # 5. Verify user is deleted
        response = client.get(f"/api/users/{created_user['id']}", headers=headers)
        assert response.status_code == 404

    def test_complete_rbac_lifecycle(self, client: TestClient, clean_db, test_admin_user):
        """Test complete RBAC lifecycle: create entities -> assign relationships -> test permissions"""
        # Create auth headers
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Create group
        group_data = TestDataFactory.get_sample_group_data()
        response = client.post("/api/groups/", json=group_data, headers=headers)
        assert response.status_code == 200
        group = response.json()["data"]
        
        # 2. Create role
        role_data = TestDataFactory.get_sample_role_data()
        response = client.post("/api/roles/", json=role_data, headers=headers)
        assert response.status_code == 200
        role = response.json()["data"]
        
        # 3. Create permission
        permission_data = TestDataFactory.get_sample_permission_data()
        response = client.post("/api/permissions/", json=permission_data, headers=headers)
        assert response.status_code == 200
        permission = response.json()["data"]
        
        # 4. Create user
        user_data = TestDataFactory.get_sample_user_data()
        response = client.post("/api/users/", json=user_data, headers=headers)
        assert response.status_code == 200
        user = response.json()["data"]
        
        # 5. Assign permission to role
        response = client.post(f"/api/roles/{role['id']}/permissions/{permission['id']}", headers=headers)
        assert response.status_code == 200
        
        # 6. Assign role to group
        response = client.post(f"/api/groups/{group['id']}/roles/{role['id']}", headers=headers)
        assert response.status_code == 200
        
        # 7. Add user to group
        response = client.post(f"/api/groups/{group['id']}/users/{user['id']}", headers=headers)
        assert response.status_code == 200
        
        # 8. Test user permissions
        response = client.get(f"/api/users/{user['id']}/permissions", headers=headers)
        assert response.status_code == 200
        permissions = response.json()["data"]
        assert any(p["resource"] == permission["resource"] and p["action"] == permission["action"] for p in permissions)
        
        # 9. Clean up - remove relationships
        response = client.delete(f"/api/groups/{group['id']}/users/{user['id']}", headers=headers)
        assert response.status_code == 200
        
        response = client.delete(f"/api/groups/{group['id']}/roles/{role['id']}", headers=headers)
        assert response.status_code == 200
        
        response = client.delete(f"/api/roles/{role['id']}/permissions/{permission['id']}", headers=headers)
        assert response.status_code == 200
        
        # 10. Delete entities
        response = client.delete(f"/api/users/{user['id']}", headers=headers)
        assert response.status_code == 200
        
        response = client.delete(f"/api/permissions/{permission['id']}", headers=headers)
        assert response.status_code == 200
        
        response = client.delete(f"/api/roles/{role['id']}", headers=headers)
        assert response.status_code == 200
        
        response = client.delete(f"/api/groups/{group['id']}", headers=headers)
        assert response.status_code == 200

    def test_auth_flow_integration(self, client: TestClient, clean_db):
        """Test complete authentication flow"""
        # 1. Register user
        register_data = {
            "email": "integration@example.com",
            "password": "Password123!",
            "name": "Integration User"
        }
        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 200
        user = response.json()["data"]
        
        # 2. Activate user (simulate admin activation)
        import asyncio
        asyncio.run(prisma.user.update(
            where={"id": user["id"]},
            data={"status": "active"}
        ))
        
        # 3. Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        token_data = response.json()["data"]
        token = token_data["access_token"]
        
        # 4. Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        assert response.status_code == 200
        me_data = response.json()["data"]
        assert me_data["email"] == register_data["email"]
        
        # 5. Update profile
        update_data = {"name": "Updated Integration User"}
        response = client.put("/api/auth/me", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_data = response.json()["data"]
        assert updated_data["name"] == "Updated Integration User"

    def test_error_handling_integration(self, client: TestClient, clean_db, test_admin_user):
        """Test error handling across different scenarios"""
        # Create auth headers
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Test 404 errors
        response = client.get("/api/users/99999", headers=headers)
        assert response.status_code == 404
        
        response = client.get("/api/groups/99999", headers=headers)
        assert response.status_code == 404
        
        # 2. Test 409 errors (duplicates)
        user_data = TestDataFactory.get_sample_user_data()
        response = client.post("/api/users/", json=user_data, headers=headers)
        assert response.status_code == 200
        
        # Try to create duplicate
        response = client.post("/api/users/", json=user_data, headers=headers)
        assert response.status_code == 409
        
        # 3. Test 422 errors (validation)
        invalid_data = TestDataFactory.get_invalid_user_data()
        response = client.post("/api/users/", json=invalid_data, headers=headers)
        assert response.status_code == 422
        
        # 4. Test 401 errors (unauthorized)
        response = client.get("/api/users/", headers={})  # No auth header
        assert response.status_code == 401

    def test_data_consistency_integration(self, client: TestClient, clean_db, test_admin_user):
        """Test data consistency across related entities"""
        # Create auth headers
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Create group
        group_data = TestDataFactory.get_sample_group_data()
        response = client.post("/api/groups/", json=group_data, headers=headers)
        group = response.json()["data"]
        
        # 2. Create user and assign to group
        user_data = TestDataFactory.get_sample_user_data()
        user_data["group_id"] = group["id"]
        response = client.post("/api/users/", json=user_data, headers=headers)
        user = response.json()["data"]
        
        # 3. Verify user is in group
        response = client.get(f"/api/users/{user['id']}", headers=headers)
        user_data_check = response.json()["data"]
        assert user_data_check["group_id"] == group["id"]
        
        # 4. Verify group contains user
        response = client.get(f"/api/groups/{group['id']}", headers=headers)
        group_data_check = response.json()["data"]
        assert any(u["id"] == user["id"] for u in group_data_check.get("users", []))
        
        # 5. Delete group and verify cascade
        response = client.delete(f"/api/groups/{group['id']}", headers=headers)
        assert response.status_code == 200
        
        # User should still exist but group_id should be None
        response = client.get(f"/api/users/{user['id']}", headers=headers)
        user_data_after = response.json()["data"]
        assert user_data_after["group_id"] is None

    def test_performance_integration(self, client: TestClient, clean_db, test_admin_user):
        """Test performance with multiple operations"""
        # Create auth headers
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create multiple users
        users = []
        for i in range(10):
            user_data = TestDataFactory.get_sample_user_data(
                email=f"perfuser{i}@example.com",
                name=f"Performance User {i}"
            )
            response = client.post("/api/users/", json=user_data, headers=headers)
            assert response.status_code == 200
            users.append(response.json()["data"])
        
        # List all users
        response = client.get("/api/users/", headers=headers)
        assert response.status_code == 200
        all_users = response.json()["data"]
        assert len(all_users) >= 10
        
        # Create multiple groups
        groups = []
        for i in range(5):
            group_data = TestDataFactory.get_sample_group_data(
                name=f"Performance Group {i}"
            )
            response = client.post("/api/groups/", json=group_data, headers=headers)
            assert response.status_code == 200
            groups.append(response.json()["data"])
        
        # Assign users to groups
        for i, user in enumerate(users):
            group = groups[i % len(groups)]
            response = client.post(f"/api/groups/{group['id']}/users/{user['id']}", headers=headers)
            assert response.status_code == 200
        
        # Verify assignments
        for group in groups:
            response = client.get(f"/api/groups/{group['id']}", headers=headers)
            assert response.status_code == 200
            group_data = response.json()["data"]
            assert len(group_data.get("users", [])) > 0

    def test_security_integration(self, client: TestClient, clean_db, test_user, test_admin_user):
        """Test security across different user types"""
        # Regular user token
        regular_token = create_access_token(data={"sub": test_user.email})
        regular_headers = {"Authorization": f"Bearer {regular_token}"}
        
        # Admin user token
        admin_token = create_access_token(data={"sub": test_admin_user.email})
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 1. Regular user should not be able to create users
        user_data = TestDataFactory.get_sample_user_data()
        response = client.post("/api/users/", json=user_data, headers=regular_headers)
        assert response.status_code == 403  # Should be forbidden
        
        # 2. Admin user should be able to create users
        response = client.post("/api/users/", json=user_data, headers=admin_headers)
        assert response.status_code == 200
        
        # 3. Regular user should not be able to create groups
        group_data = TestDataFactory.get_sample_group_data()
        response = client.post("/api/groups/", json=group_data, headers=regular_headers)
        assert response.status_code == 403  # Should be forbidden
        
        # 4. Admin user should be able to create groups
        response = client.post("/api/groups/", json=group_data, headers=admin_headers)
        assert response.status_code == 200
        
        # 5. Regular user should be able to access their own data
        response = client.get("/api/auth/me", headers=regular_headers)
        assert response.status_code == 200
        
        # 6. Regular user should not be able to access other users' data
        response = client.get(f"/api/users/{test_admin_user.id}", headers=regular_headers)
        assert response.status_code == 403  # Should be forbidden
