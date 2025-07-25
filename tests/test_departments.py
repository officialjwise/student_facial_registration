import pytest
from fastapi.testclient import TestClient
from main import app
from core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Generate valid JWT token for tests."""
    token = create_access_token(data={"sub": "test_admin@example.com"})
    return {"Authorization": f"Bearer {token}"}

def test_create_department(auth_headers):
    """Test department creation endpoint."""
    response = client.post("/departments/", json={"name": "Computer Science", "college_id": 1}, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Computer Science"

def test_list_departments():
    """Test listing all departments."""
    response = client.get("/departments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)