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

def test_get_admin_stats(auth_headers):
    """Test admin stats endpoint."""
    response = client.get("/admin/stats", headers=auth_headers)
    assert response.status_code == 200
    assert "total_students" in response.json()
    assert "total_recognitions" in response.json()
    assert "recent_recognitions" in response.json()