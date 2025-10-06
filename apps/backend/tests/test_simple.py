"""
Simple test để kiểm tra auth API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from interfaces.rest.server import app
from core.db import prisma
import asyncio

# Tạo client với database connection
client = TestClient(app)


def test_register_simple():
    """Test đơn giản cho register"""
    # Connect database trước khi test
    asyncio.run(prisma.connect())
    
    try:
        user_data = {
            "email": "test@example.com",
            "password": "Password123!",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Chỉ kiểm tra không có lỗi 500
        assert response.status_code != 500
    finally:
        # Disconnect sau khi test
        asyncio.run(prisma.disconnect())
