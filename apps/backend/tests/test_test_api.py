"""
Tests for Test API endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestTestAPI:
    """Test cases for Test API"""

    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint"""
        response = client.get("/api/test/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint_no_auth_required(self, client: TestClient):
        """Test that health endpoint doesn't require authentication"""
        # This endpoint should be accessible without authentication
        response = client.get("/api/test/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint_methods(self, client: TestClient):
        """Test health endpoint with different HTTP methods"""
        # Test GET method (should work)
        response = client.get("/api/test/health")
        assert response.status_code == 200
        
        # Test POST method (should not work)
        response = client.post("/api/test/health")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test PUT method (should not work)
        response = client.put("/api/test/health")
        assert response.status_code == 405  # Method Not Allowed
        
        # Test DELETE method (should not work)
        response = client.delete("/api/test/health")
        assert response.status_code == 405  # Method Not Allowed

    def test_health_endpoint_response_format(self, client: TestClient):
        """Test health endpoint response format"""
        response = client.get("/api/test/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] == "ok"
        
        # Check that it's a simple response (not wrapped in success/data structure)
        assert "success" not in data
        assert "data" not in data
        assert "error" not in data

    def test_health_endpoint_multiple_calls(self, client: TestClient):
        """Test health endpoint with multiple calls"""
        for i in range(5):
            response = client.get("/api/test/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"

    def test_health_endpoint_with_headers(self, client: TestClient):
        """Test health endpoint with various headers"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "test-client"
        }
        
        response = client.get("/api/test/health", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_endpoint_with_query_params(self, client: TestClient):
        """Test health endpoint with query parameters"""
        response = client.get("/api/test/health?param1=value1&param2=value2")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
