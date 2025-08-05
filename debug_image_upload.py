#!/usr/bin/env python3
"""
Debug script to test image upload and identify HTTP 422 errors
"""
import requests
import base64
import json
from io import BytesIO
from PIL import Image
import sys

# Server URL
BASE_URL = "http://localhost:8000"

def create_test_image():
    """Create a simple test image in memory"""
    # Create a simple 200x200 RGB image
    img = Image.new('RGB', (200, 200), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

def test_student_registration_with_image():
    """Test student registration with base64 image"""
    print("🧪 Testing student registration with base64 image...")
    
    # Create test image
    image_data = create_test_image()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    # Test different image formats
    test_formats = [
        f"data:image/jpeg;base64,{base64_image}",  # With data URL prefix
        base64_image,  # Without prefix
        f"data:image/png;base64,{base64_image}",   # Wrong format in prefix
    ]
    
    for i, image_format in enumerate(test_formats):
        print(f"\n📋 Test {i+1}: {'With data URL prefix (JPEG)' if i == 0 else 'Without prefix' if i == 1 else 'Wrong format in prefix'}")
        
        # Student data
        student_data = {
            "student_id": f"2023000{i+1}",
            "index_number": f"123456{i}",  # 7 digits
            "first_name": "Test",
            "last_name": "Student",
            "email": f"test{i+1}@knust.edu.gh",
            "college_id": "550e8400-e29b-41d4-a716-446655440000",  # Placeholder UUID
            "department_id": "550e8400-e29b-41d4-a716-446655440001",  # Placeholder UUID
            "face_image": image_format
        }
        
        try:
            response = requests.post(f"{BASE_URL}/students/", json=student_data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 422:
                print("   ❌ HTTP 422 Error detected!")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"   Raw response: {response.text}")
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")

def test_face_recognition_upload():
    """Test face recognition with file upload"""
    print("\n🧪 Testing face recognition with file upload...")
    
    # Create test image
    image_data = create_test_image()
    
    try:
        files = {
            'image': ('test.jpg', image_data, 'image/jpeg')
        }
        
        response = requests.post(f"{BASE_URL}/students/recognize", files=files)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 422:
            print("   ❌ HTTP 422 Error detected!")
            try:
                error_detail = response.json()
                print(f"   Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Raw response: {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")

def test_face_detection_preview():
    """Test face detection preview endpoint"""
    print("\n🧪 Testing face detection preview...")
    
    # Create test image
    image_data = create_test_image()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    test_data = {
        "face_image": f"data:image/jpeg;base64,{base64_image}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/students/detect-face", json=test_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 422:
            print("   ❌ HTTP 422 Error detected!")
            try:
                error_detail = response.json()
                print(f"   Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Raw response: {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")

def test_invalid_scenarios():
    """Test common invalid scenarios that cause 422 errors"""
    print("\n🧪 Testing invalid scenarios...")
    
    invalid_tests = [
        {
            "name": "Empty image data",
            "data": {"face_image": ""}
        },
        {
            "name": "Invalid base64",
            "data": {"face_image": "invalid_base64_data!!!"}
        },
        {
            "name": "Missing required fields",
            "data": {
                "student_id": "20230001",
                "face_image": base64.b64encode(create_test_image()).decode('utf-8')
                # Missing required fields like first_name, last_name, etc.
            }
        }
    ]
    
    for test in invalid_tests:
        print(f"\n📋 Testing: {test['name']}")
        try:
            response = requests.post(f"{BASE_URL}/students/", json=test['data'])
            print(f"   Status: {response.status_code}")
            if response.status_code == 422:
                print("   ✅ Expected 422 error occurred")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {json.dumps(error_detail.get('detail', 'No detail'), indent=2)}")
                except:
                    print(f"   Raw response: {response.text[:200]}...")
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting image upload debugging...")
    print(f"📡 Server URL: {BASE_URL}")
    
    # Test server connectivity
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        sys.exit(1)
    
    # Run tests
    test_student_registration_with_image()
    test_face_recognition_upload()
    test_face_detection_preview()
    test_invalid_scenarios()
    
    print("\n✅ Debugging complete!")
