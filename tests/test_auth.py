import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_admin():
    """Test admin registration endpoint."""
    response = client.post("/auth/register", json={
        "email": "test_admin@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "Admin registered, OTP sent to email"

def test_login_admin_invalid_credentials():
    """Test admin login with invalid credentials."""
    response = client.post("/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"