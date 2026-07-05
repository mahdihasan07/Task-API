from fastapi.testclient import TestClient as TestClient
from app.main import app

client = TestClient(app)

def test_register_add_login():
    response = client.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
    assert response.status_code == 200

    login_resp = client.post("/auth/login", json={"email": "test@example.com", "password": "secret123"})
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

