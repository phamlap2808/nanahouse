"""
Tests for Users API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from core.security import create_access_token
from core.db import prisma


class TestUsersAPI:
    """Test cases for Users API"""

    def test_list_users_success(self, client: TestClient, clean_db, test_user, test_admin_user):
        """Test listing users successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/users/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 2  # At least test_user and test_admin_user

    def test_list_users_no_auth(self, client: TestClient, clean_db):
        """Test listing users without authentication"""
        response = client.get("/api/users/")
        
        assert response.status_code == 401

    def test_create_user_success(self, client: TestClient, clean_db, test_admin_user, sample_user_data):
        """Test creating user successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/api/users/", json=sample_user_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == sample_user_data["email"]
        assert data["data"]["name"] == sample_user_data["name"]
        assert "id" in data["data"]

    def test_create_user_duplicate_email(self, client: TestClient, clean_db, test_user, test_admin_user):
        """Test creating user with duplicate email"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        user_data = {
            "email": test_user.email,
            "password": "Password123!",
            "name": "Duplicate User"
        }
        
        response = client.post("/api/users/", json=user_data, headers=headers)
        
        assert response.status_code == 409
        assert "email already exists" in response.json()["detail"]

    def test_create_user_invalid_data(self, client: TestClient, clean_db, test_admin_user):
        """Test creating user with invalid data"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        invalid_data = {
            "email": "invalid-email",
            "password": "123",  # Too short
            "name": "Test User"
        }
        
        response = client.post("/api/users/", json=invalid_data, headers=headers)
        
        assert response.status_code == 422

    def test_create_user_no_auth(self, client: TestClient, clean_db, sample_user_data):
        """Test creating user without authentication"""
        response = client.post("/api/users/", json=sample_user_data)
        
        assert response.status_code == 401

    def test_get_user_success(self, client: TestClient, clean_db, test_user, test_admin_user):
        """Test getting user successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/users/{test_user.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_user.id
        assert data["data"]["email"] == test_user.email

    def test_get_user_not_found(self, client: TestClient, clean_db, test_admin_user):
        """Test getting non-existent user"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/users/99999", headers=headers)
        
        assert response.status_code == 404
        assert "user not found" in response.json()["detail"]

    def test_get_user_no_auth(self, client: TestClient, clean_db, test_user):
        """Test getting user without authentication"""
        response = client.get(f"/api/users/{test_user.id}")
        
        assert response.status_code == 401

    def test_delete_user_success(self, client: TestClient, clean_db, test_user, test_admin_user):
        """Test deleting user successfully"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/api/users/{test_user.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == test_user.id

    def test_delete_user_not_found(self, client: TestClient, clean_db, test_admin_user):
        """Test deleting non-existent user"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete("/api/users/99999", headers=headers)
        
        assert response.status_code == 404
        assert "user not found" in response.json()["detail"]

    def test_delete_user_no_auth(self, client: TestClient, clean_db, test_user):
        """Test deleting user without authentication"""
        response = client.delete(f"/api/users/{test_user.id}")
        
        assert response.status_code == 401

    def test_users_with_rbac_data(self, client: TestClient, clean_db, test_group, test_admin_user):
        """Test users API with RBAC data (group, is_admin)"""
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create user with group and admin status
        user_data = {
            "email": "rbacuser@example.com",
            "password": "Password123!",
            "name": "RBAC User",
            "group_id": test_group.id,
            "is_admin": False
        }
        
        response = client.post("/api/users/", json=user_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == user_data["email"]
        assert data["data"]["group_id"] == test_group.id
        assert data["data"]["is_admin"] is False

    def test_get_user_with_group_info(self, client: TestClient, clean_db, test_group, test_admin_user):
        """Test getting user with group information"""
        # Create user with group
        import asyncio
        user = asyncio.run(prisma.user.create(data={
            "email": "groupuser@example.com",
            "name": "Group User",
            "password": "hashed_password",
            "status": "active",
            "groupId": test_group.id
        }))
        
        # Create access token for admin user
        token = create_access_token(data={"sub": test_admin_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/users/{user.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["group_id"] == test_group.id
        # Group information should be included in the response
        assert "group" in data["data"] or data["data"]["group_id"] is not None
