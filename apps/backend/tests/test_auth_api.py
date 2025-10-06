"""
Tests for Auth API endpoints
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from core.security import create_access_token
from core.db import prisma


class TestAuthAPI:
    """Test cases for Auth API"""

    def test_register_success(self, client: TestClient, clean_db, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == sample_user_data["email"]
        assert data["data"]["name"] == sample_user_data["name"]
        assert data["data"]["status"] == "inactive"
        assert "id" in data["data"]

    def test_register_duplicate_email(self, client: TestClient, clean_db, test_user, sample_user_data):
        """Test registration with duplicate email"""
        # Update sample data to use existing email
        sample_user_data["email"] = test_user.email
        
        response = client.post("/api/auth/register", json=sample_user_data)
        
        assert response.status_code == 409
        assert "email already exists" in response.json()["detail"]

    def test_register_invalid_password(self, client: TestClient, clean_db):
        """Test registration with invalid password"""
        invalid_data = {
            "email": "test@example.com",
            "password": "123",  # Too short
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422
        assert "password must be at least 8 characters" in str(response.json())

    def test_register_invalid_email(self, client: TestClient, clean_db):
        """Test registration with invalid email"""
        invalid_data = {
            "email": "invalid-email",
            "password": "Password123!",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=invalid_data)
        
        assert response.status_code == 422
        assert "email" in str(response.json())

    def test_login_success(self, client: TestClient, clean_db, test_user):
        """Test successful login"""
        # Update user status to active
        asyncio.run(prisma.user.update(
            where={"id": test_user.id},
            data={"status": "active"}
        ))
        
        login_data = {
            "email": test_user.email,
            "password": "password123"  # Assuming this is the original password
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, clean_db, test_user):
        """Test login with invalid credentials"""
        login_data = {
            "email": test_user.email,
            "password": "wrong_password"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient, clean_db):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_inactive_user(self, client: TestClient, clean_db, test_user):
        """Test login with inactive user"""
        login_data = {
            "email": test_user.email,
            "password": "password123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 400
        assert "Inactive user" in response.json()["detail"]

    def test_me_success(self, client: TestClient, clean_db, test_user):
        """Test getting current user info"""
        # Create access token
        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == test_user.email
        assert data["data"]["id"] == test_user.id

    def test_me_invalid_token(self, client: TestClient, clean_db):
        """Test getting current user info with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_me_no_token(self, client: TestClient, clean_db):
        """Test getting current user info without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401

    def test_update_me_success(self, client: TestClient, clean_db, test_user):
        """Test updating current user info"""
        # Create access token
        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {
            "name": "Updated Name"
        }
        
        response = client.put("/api/auth/me", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["email"] == test_user.email

    def test_update_me_no_changes(self, client: TestClient, clean_db, test_user):
        """Test updating current user info with no changes"""
        # Create access token
        token = create_access_token(data={"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {}  # No changes
        
        response = client.put("/api/auth/me", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == test_user.name

    def test_update_me_invalid_token(self, client: TestClient, clean_db):
        """Test updating current user info with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        update_data = {
            "name": "Updated Name"
        }
        
        response = client.put("/api/auth/me", json=update_data, headers=headers)
        
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_update_me_no_token(self, client: TestClient, clean_db):
        """Test updating current user info without token"""
        update_data = {
            "name": "Updated Name"
        }
        
        response = client.put("/api/auth/me", json=update_data)
        
        assert response.status_code == 401
