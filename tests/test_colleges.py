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

def test_create_college(auth_headers):
    """Test college creation endpoint."""
    response = client.post("/colleges/", json={"name": "College of Science"}, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "College of Science"

def test_list_colleges():
    """Test listing all colleges."""
    response = client.get("/colleges/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)