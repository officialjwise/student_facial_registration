#!/usr/bin/env python3
"""
Test student registration with valid data and proper error handling
"""

import requests
import json
import base64
import random

# API configuration
API_BASE = "http://localhost:8000"

# Valid college and department IDs from the database
VALID_COLLEGE_ID = "d06f7381-0d3a-4c90-a43d-6ff2c1887fb6"  # College of Engineering
VALID_DEPARTMENT_ID = "263c1aaa-d85e-4f92-a236-090edcc4d825"  # Computer Engineering

# Generate unique test data
random_id = random.randint(10000000, 99999999)
random_index = random.randint(1000000, 9999999)

def test_student_registration():
    """Test student registration with valid data"""
    
    # Test data with valid foreign keys
    student_data = {
        "student_id": str(random_id),
        "index_number": str(random_index),
        "first_name": "Test",
        "last_name": "Student",
        "email": f"test{random_id}@knust.edu.gh",
        "college_id": VALID_COLLEGE_ID,
        "department_id": VALID_DEPARTMENT_ID
        # No face_image to avoid encoding issues
    }
    
    print("Testing student registration with valid data:")
    print(f"Student ID: {student_data['student_id']}")
    print(f"Index Number: {student_data['index_number']}")
    print(f"Email: {student_data['email']}")
    print(f"College ID: {student_data['college_id']}")
    print(f"Department ID: {student_data['department_id']}")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE}/students/",
            json=student_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ SUCCESS: Student registered successfully!")
            print(f"Message: {result.get('message')}")
            print(f"Student Data: {json.dumps(result.get('data', [{}])[0], indent=2)}")
            
        elif response.status_code == 409:
            result = response.json()
            print("⚠️  CONFLICT: Student already exists")
            print(f"Error: {result.get('detail')}")
            
        elif response.status_code == 400:
            result = response.json()
            print("❌ BAD REQUEST: Invalid data")
            print(f"Error: {result.get('detail')}")
            
        elif response.status_code == 422:
            result = response.json()
            print("❌ VALIDATION ERROR:")
            if 'detail' in result:
                for error in result['detail']:
                    print(f"  - {error.get('msg', 'Unknown error')} at {error.get('loc', [])}")
        else:
            print(f"❌ UNEXPECTED ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ NETWORK ERROR: {e}")

def test_duplicate_registration():
    """Test duplicate student registration"""
    
    # Use the same data as before to test duplicate handling
    student_data = {
        "student_id": "12345678",
        "index_number": "1234567",  # This should already exist
        "first_name": "Duplicate",
        "last_name": "Student",
        "email": "duplicate@knust.edu.gh",
        "college_id": VALID_COLLEGE_ID,
        "department_id": VALID_DEPARTMENT_ID
    }
    
    print("\nTesting duplicate student registration:")
    print(f"Using existing index number: {student_data['index_number']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/students/",
            json=student_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 409:
            result = response.json()
            print("✅ SUCCESS: Properly detected duplicate and returned 409")
            print(f"Error Message: {result.get('detail')}")
        else:
            print(f"❌ UNEXPECTED: Expected 409, got {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ NETWORK ERROR: {e}")

def test_invalid_foreign_keys():
    """Test registration with invalid college/department IDs"""
    
    student_data = {
        "student_id": str(random.randint(10000000, 99999999)),
        "index_number": str(random.randint(1000000, 9999999)),
        "first_name": "Invalid",
        "last_name": "Keys",
        "email": f"invalid{random.randint(1000, 9999)}@knust.edu.gh",
        "college_id": "550e8400-e29b-41d4-a716-446655440000",  # Invalid UUID
        "department_id": "550e8400-e29b-41d4-a716-446655440001"  # Invalid UUID
    }
    
    print("\nTesting registration with invalid foreign keys:")
    print(f"Invalid College ID: {student_data['college_id']}")
    print(f"Invalid Department ID: {student_data['department_id']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/students/",
            json=student_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 400:
            result = response.json()
            print("✅ SUCCESS: Properly detected invalid foreign keys and returned 400")
            print(f"Error Message: {result.get('detail')}")
        else:
            print(f"❌ UNEXPECTED: Expected 400, got {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ NETWORK ERROR: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("STUDENT REGISTRATION API TESTING")
    print("=" * 60)
    
    # Test 1: Valid registration
    test_student_registration()
    
    # Test 2: Duplicate registration
    test_duplicate_registration()
    
    # Test 3: Invalid foreign keys
    test_invalid_foreign_keys()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
