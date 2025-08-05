#!/usr/bin/env python3
"""
Complete test script with proper student data and image upload
This script demonstrates how to properly send student registration requests
"""
import requests
import base64
import json
from io import BytesIO
from PIL import Image

# Server URL
BASE_URL = "http://localhost:8000"

# Valid college and department IDs from your system
VALID_COLLEGE_ID = "2f290067-0e63-4aba-802f-dab77780dd07"  # College of Sciences
VALID_DEPARTMENT_ID = "d827be2f-6b7f-440a-9699-b2f9144a55de"  # Computer Science

def create_test_image():
    """Create a simple test image in memory"""
    # Create a simple 200x200 RGB image
    img = Image.new('RGB', (200, 200), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

def test_correct_student_registration():
    """Test student registration with all required fields and valid image"""
    print("🧪 Testing CORRECT student registration with all required fields...")
    
    # Create test image
    image_data = create_test_image()
    base64_image = base64.b64encode(image_data).decode('utf-8')
    
    # Complete student data with all required fields
    student_data = {
        "student_id": "20250001",  # Exactly 8 digits as required
        "index_number": "2234567",  # Exactly 7 digits as required
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe.test@knust.edu.gh",
        "college_id": VALID_COLLEGE_ID,
        "department_id": VALID_DEPARTMENT_ID,
        "face_image": f"data:image/jpeg;base64,{base64_image}",  # With proper data URL prefix
        # Optional fields
        "middle_name": "Smith",
        "phone_number": "+233241234567",
        "gender": "Male",
        "program": "Computer Science",
        "level": "Level 100"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/students/", json=student_data)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 201:
            print("🎉 SUCCESS! Student registered successfully")
            response_data = response.json()
            print(f"📋 Response: {json.dumps(response_data, indent=2)}")
        elif response.status_code == 422:
            print("❌ HTTP 422 - Validation Error")
            error_detail = response.json()
            print(f"📋 Error details: {json.dumps(error_detail, indent=2)}")
        elif response.status_code == 409:
            print("⚠️  HTTP 409 - Student already exists (duplicate)")
            error_detail = response.json()
            print(f"📋 Details: {error_detail.get('detail', 'No details')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"📋 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_missing_fields_scenarios():
    """Test various missing field scenarios that cause 422 errors"""
    print("\n🧪 Testing scenarios that cause HTTP 422 errors...")
    
    base_image = base64.b64encode(create_test_image()).decode('utf-8')
    
    # Test scenarios that will cause 422 errors
    test_scenarios = [
        {
            "name": "Missing student_id",
            "data": {
                "index_number": "1234568",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@knust.edu.gh",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID,
                "face_image": f"data:image/jpeg;base64,{base_image}"
            }
        },
        {
            "name": "Invalid student_id format (not 8 digits)",
            "data": {
                "student_id": "123",  # Too short
                "index_number": "1234569",
                "first_name": "Bob",
                "last_name": "Smith",
                "email": "bob.smith@knust.edu.gh",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID,
                "face_image": f"data:image/jpeg;base64,{base_image}"
            }
        },
        {
            "name": "Invalid index_number format (not 7 digits)",
            "data": {
                "student_id": "20240003",
                "index_number": "123",  # Too short
                "first_name": "Alice",
                "last_name": "Johnson",
                "email": "alice.johnson@knust.edu.gh",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID,
                "face_image": f"data:image/jpeg;base64,{base_image}"
            }
        },
        {
            "name": "Invalid email format",
            "data": {
                "student_id": "20240004",
                "index_number": "1234570",
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "invalid-email",  # Invalid email
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID,
                "face_image": f"data:image/jpeg;base64,{base_image}"
            }
        },
        {
            "name": "Invalid college_id format",
            "data": {
                "student_id": "20240005",
                "index_number": "1234571",
                "first_name": "David",
                "last_name": "Wilson",
                "email": "david.wilson@knust.edu.gh",
                "college_id": "invalid-uuid",  # Invalid UUID
                "department_id": VALID_DEPARTMENT_ID,
                "face_image": f"data:image/jpeg;base64,{base_image}"
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n📋 Test {i+1}: {scenario['name']}")
        try:
            response = requests.post(f"{BASE_URL}/students/", json=scenario['data'])
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                print("   ✅ Expected 422 error occurred")
                try:
                    error_detail = response.json()
                    # Show only the relevant error messages
                    if 'detail' in error_detail:
                        for error in error_detail['detail'][:2]:  # Show first 2 errors
                            field = error.get('loc', ['unknown'])[-1]
                            msg = error.get('msg', 'Unknown error')
                            print(f"   ❌ {field}: {msg}")
                        if len(error_detail['detail']) > 2:
                            print(f"   ... and {len(error_detail['detail']) - 2} more errors")
                except:
                    print(f"   Raw response: {response.text[:100]}...")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")

def show_frontend_integration_guide():
    """Show how to properly integrate this in the frontend"""
    print("\n" + "="*60)
    print("🌐 FRONTEND INTEGRATION GUIDE")
    print("="*60)
    
    print("""
📋 To avoid HTTP 422 errors in your frontend, ensure you send:

✅ REQUIRED FIELDS (all must be present):
- student_id: exactly 8 digits (e.g., "20240001")  
- index_number: exactly 7 digits (e.g., "1234567")
- first_name: string (e.g., "John")
- last_name: string (e.g., "Doe")  
- email: valid email (e.g., "john.doe@knust.edu.gh")
- college_id: valid UUID from /colleges/ endpoint
- department_id: valid UUID from /departments/ endpoint

✅ OPTIONAL FIELDS:
- face_image: base64 string with data URL prefix (optional)
  Format: "data:image/jpeg;base64,{base64_data}"
- middle_name, phone_number, date_of_birth, gender, program, level

📡 EXAMPLE JAVASCRIPT FETCH REQUEST:
""")
    
    javascript_example = """
const studentData = {
    student_id: "20240001",
    index_number: "1234567", 
    first_name: "John",
    last_name: "Doe",
    email: "john.doe@knust.edu.gh",
    college_id: "2f290067-0e63-4aba-802f-dab77780dd07",
    department_id: "d827be2f-6b7f-440a-9699-b2f9144a55de",
    face_image: `data:image/jpeg;base64,${base64ImageData}` // Optional
};

fetch('http://localhost:8000/students/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(studentData)
})
.then(response => {
    if (response.status === 422) {
        return response.json().then(err => {
            console.error('Validation errors:', err.detail);
            // Handle validation errors in UI
        });
    }
    return response.json();
})
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
"""
    
    print(javascript_example)
    
    print("""
🔧 COMMON FIXES FOR HTTP 422:
1. Validate all required fields are present before sending
2. Ensure student_id is exactly 8 digits  
3. Ensure index_number is exactly 7 digits
4. Validate email format
5. Get valid college_id and department_id from respective endpoints
6. Format face_image with proper data URL prefix if provided

🎯 VALIDATION IN YOUR FRONTEND:
- Check all required fields are filled
- Validate field formats (8 digits for student_id, 7 digits for index_number)
- Validate email format with proper regex
- Ensure UUIDs are valid format
""")

if __name__ == "__main__":
    print("🚀 Complete HTTP 422 Error Testing and Resolution Guide")
    print("=" * 60)
    
    # Test server connectivity
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status {response.status_code}")
            exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        exit(1)
    
    # Run comprehensive tests
    test_correct_student_registration()
    test_missing_fields_scenarios()
    show_frontend_integration_guide()
    
    print("\n✅ Testing complete! Use the integration guide above to fix your frontend.")
