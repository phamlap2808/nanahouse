"""
Test RBAC Middleware
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from interfaces.rest.server import app
from core.security import create_access_token

client = TestClient(app)


class TestRBACMiddleware:
    """Test cases for RBAC Middleware"""


    def test_rbac_middleware_no_auth(self, client: TestClient):
        """Test RBAC middleware trả về 401 khi không có auth"""
        response = client.get("/api/users/")
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Nên trả về 401 vì không có authentication
        assert response.status_code == 401

    def test_rbac_middleware_invalid_token(self, client: TestClient):
        """Test RBAC middleware trả về 401 khi token không hợp lệ"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/users/", headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Nên trả về 401 vì token không hợp lệ
        assert response.status_code == 401

    def test_rbac_middleware_excluded_paths(self, client: TestClient):
        """Test RBAC middleware không áp dụng cho excluded paths"""
        response = client.get("/api/test/health")
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Health endpoint nên hoạt động bình thường
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_rbac_middleware_with_valid_token(self, client: TestClient):
        """Test RBAC middleware với token hợp lệ (simplified)"""
        # Tạo token với email giả
        token = create_access_token(data={"sub": "admin@example.com"})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test endpoint - sẽ fail vì user không tồn tại trong DB
        response = client.get("/api/users/", headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Sẽ trả về 401 vì user không tồn tại trong DB
        assert response.status_code == 401
