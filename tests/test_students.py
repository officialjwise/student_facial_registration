import pytest
from fastapi.testclient import TestClient
from main import app
import base64
from core.security import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Generate valid JWT token for tests."""
    token = create_access_token(data={"sub": "test_admin@example.com"})
    return {"Authorization": f"Bearer {token}"}

def test_register_student(auth_headers):
    """Test student registration endpoint."""
    student_data = {
        "student_id": "12345678",
        "index_number": "1234567",
        "first_name": "John",
        "middle_name": "Kwame",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "college_id": 1,
        "department_id": 1,
        "face_image": base64.b64encode(b"dummy_image_data").decode("utf-8")
    }
    
    response = client.post("/students/", json=student_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["student_id"] == "12345678"

def test_register_student_invalid_id(auth_headers):
    """Test student registration with invalid student ID."""
    student_data = {
        "student_id": "12345", 
        "index_number": "1234567",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "college_id": 1,
        "department_id": 1,
        "face_image": base64.b64encode(b"dummy_image_data").decode("utf-8")
    }
    
    response = client.post("/students/", json=student_data, headers=auth_headers)
    assert response.status_code == 422  # Unprocessable Entity
    assert "Student ID must be exactly 8 digits" in response.json()["detail"][0]["msg"]