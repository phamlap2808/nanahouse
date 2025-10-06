"""
Test configuration and fixtures
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from prisma import Prisma
from core.db import prisma
from core.rbac import RBACManager
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from interfaces.rest.server import app


@pytest.fixture(scope="session")
async def test_db():
    """Setup test database"""
    # Connect to test database
    await prisma.connect()
    
    # Initialize RBAC
    rbac_manager = RBACManager()
    await rbac_manager.setup_default_rbac()
    
    yield prisma
    
    # Cleanup
    await prisma.disconnect()


@pytest.fixture(scope="function")
async def clean_db(test_db):
    """Clean database before each test"""
    # Delete all data in reverse order of dependencies
    await test_db.rolepermission.delete_many()
    await test_db.grouprole.delete_many()
    await test_db.permission.delete_many()
    await test_db.role.delete_many()
    await test_db.group.delete_many()
    await test_db.user.delete_many()
    
    # Reinitialize RBAC
    rbac_manager = RBACManager()
    await rbac_manager.setup_default_rbac()
    
    yield test_db


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def test_user(test_db):
    """Create a test user"""
    user = await test_db.user.create(data={
        "email": "test@example.com",
        "name": "Test User",
        "password": "hashed_password",
        "status": "active"
    })
    return user


@pytest.fixture
async def test_admin_user(test_db):
    """Create a test admin user"""
    user = await test_db.user.create(data={
        "email": "admin@example.com",
        "name": "Admin User",
        "password": "hashed_password",
        "status": "active",
        "isAdmin": True
    })
    return user


@pytest.fixture
async def test_group(test_db):
    """Create a test group"""
    group = await test_db.group.create(data={
        "name": "Test Group",
        "description": "Test group description",
        "isAdmin": False
    })
    return group


@pytest.fixture
async def test_role(test_db):
    """Create a test role"""
    role = await test_db.role.create(data={
        "name": "test_role",
        "description": "Test role description"
    })
    return role


@pytest.fixture
async def test_permission(test_db):
    """Create a test permission"""
    permission = await test_db.permission.create(data={
        "name": "test_permission",
        "resource": "test_resource",
        "action": "read",
        "description": "Test permission"
    })
    return permission


@pytest.fixture
def auth_headers():
    """Get auth headers for testing"""
    def _get_headers(token: str):
        return {"Authorization": f"Bearer {token}"}
    return _get_headers


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "newuser@example.com",
        "password": "Password123!",
        "name": "New User",
        "group_id": None,
        "is_admin": False
    }


@pytest.fixture
def sample_group_data():
    """Sample group data for testing"""
    return {
        "name": "New Group",
        "description": "New group description",
        "is_admin": False
    }


@pytest.fixture
def sample_role_data():
    """Sample role data for testing"""
    return {
        "name": "new_role",
        "description": "New role description"
    }


@pytest.fixture
def sample_permission_data():
    """Sample permission data for testing"""
    return {
        "name": "new_permission",
        "resource": "new_resource",
        "action": "create",
        "description": "New permission"
    }
