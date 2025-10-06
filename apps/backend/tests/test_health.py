import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from fastapi.testclient import TestClient
from interfaces.rest.server import app

client = TestClient(app)


def test_health():
    r = client.get("/api/test/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
