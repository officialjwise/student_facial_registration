import requests
import base64
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_student_registration(image_path: str):
    """Test student registration with a base64 encoded image."""
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Student data
    student_data = {
        "student_id": "12345678",
        "index_number": "1234567",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "college_id": "YOUR-COLLEGE-UUID",  # Replace with actual UUID
        "department_id": "YOUR-DEPARTMENT-UUID",  # Replace with actual UUID
        "face_image": encoded_image
    }
    
    # Make the request
    response = requests.post(f"{BASE_URL}/students/", json=student_data)
    print(f"Registration Status Code: {response.status_code}")
    print(f"Registration Response: {response.json()}")

def test_face_recognition(image_path: str):
    """Test face recognition with image file upload."""
    with open(image_path, "rb") as image_file:
        files = {"image": ("image.jpg", image_file, "image/jpeg")}
        response = requests.post(f"{BASE_URL}/students/recognize", files=files)
        print(f"Recognition Status Code: {response.status_code}")
        print(f"Recognition Response: {response.json()}")

if __name__ == "__main__":
    # Replace with path to your test image
    image_path = "path/to/your/image.jpg"
    
    print("Testing student registration...")
    test_student_registration(image_path)
    
    print("\nTesting face recognition...")
    test_face_recognition(image_path)
