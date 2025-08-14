#!/usr/bin/env python3
"""
Test the updated validation rules for student_id (8 characters) and index_number (7 digits)
"""

import requests
import json

# API configuration
API_BASE = "http://localhost:8000"

# Valid college and department IDs
VALID_COLLEGE_ID = "d06f7381-0d3a-4c90-a43d-6ff2c1887fb6"  # College of Engineering
VALID_DEPARTMENT_ID = "263c1aaa-d85e-4f92-a236-090edcc4d825"  # Computer Engineering

def test_validation_rules():
    """Test the new validation rules"""
    
    print("=" * 60)
    print("TESTING VALIDATION RULES")
    print("=" * 60)
    print("Required: student_id = exactly 8 characters")
    print("Required: index_number = exactly 7 digits")
    print()
    
    test_cases = [
        {
            "name": "Valid Data (8 char student_id, 7 digit index)",
            "data": {
                "student_id": "12345678",  # 8 characters
                "index_number": "1234567",  # 7 digits
                "first_name": "Valid",
                "last_name": "Student",
                "email": "valid@test.com",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID
            },
            "expected": "success or 409 conflict"
        },
        {
            "name": "Invalid student_id (7 characters)",
            "data": {
                "student_id": "1234567",  # 7 characters - too short
                "index_number": "1234567",
                "first_name": "Invalid",
                "last_name": "Student",
                "email": "invalid1@test.com",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID
            },
            "expected": "422 validation error"
        },
        {
            "name": "Invalid student_id (9 characters)",
            "data": {
                "student_id": "123456789",  # 9 characters - too long
                "index_number": "1234567",
                "first_name": "Invalid",
                "last_name": "Student",
                "email": "invalid2@test.com",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID
            },
            "expected": "422 validation error"
        },
        {
            "name": "Invalid index_number (6 digits)",
            "data": {
                "student_id": "12345678",
                "index_number": "123456",  # 6 digits - too short
                "first_name": "Invalid",
                "last_name": "Student",
                "email": "invalid3@test.com",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID
            },
            "expected": "422 validation error"
        },
        {
            "name": "Invalid index_number (8 digits)",
            "data": {
                "student_id": "12345678",
                "index_number": "12345678",  # 8 digits - too long
                "first_name": "Invalid",
                "last_name": "Student",
                "email": "invalid4@test.com",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID
            },
            "expected": "422 validation error"
        },
        {
            "name": "Invalid student_id (contains letters)",
            "data": {
                "student_id": "1234567A",  # Contains letter
                "index_number": "1234567",
                "first_name": "Invalid",
                "last_name": "Student",
                "email": "invalid5@test.com",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID
            },
            "expected": "422 validation error"
        },
        {
            "name": "Invalid index_number (contains letters)",
            "data": {
                "student_id": "12345678",
                "index_number": "123456A",  # Contains letter
                "first_name": "Invalid",
                "last_name": "Student",
                "email": "invalid6@test.com",
                "college_id": VALID_COLLEGE_ID,
                "department_id": VALID_DEPARTMENT_ID
            },
            "expected": "422 validation error"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Expected: {test_case['expected']}")
        print(f"student_id: '{test_case['data']['student_id']}' (length: {len(test_case['data']['student_id'])})")
        print(f"index_number: '{test_case['data']['index_number']}' (length: {len(test_case['data']['index_number'])})")
        
        try:
            response = requests.post(
                f"{API_BASE}/students/",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"Response: {response.status_code}")
            
            if response.status_code == 201:
                print("✅ SUCCESS: Registration successful")
                
            elif response.status_code == 409:
                result = response.json()
                print("✅ SUCCESS: Duplicate detected (expected for valid format)")
                print(f"Message: {result.get('detail')}")
                
            elif response.status_code == 422:
                result = response.json()
                print("✅ SUCCESS: Validation error (as expected)")
                if 'detail' in result:
                    for error in result['detail']:
                        field = '.'.join(map(str, error.get('loc', [])))
                        message = error.get('msg', 'Unknown error')
                        print(f"  - {field}: {message}")
                        
            elif response.status_code == 400:
                result = response.json()
                print("✅ SUCCESS: Bad request (as expected)")
                print(f"Message: {result.get('detail')}")
                
            else:
                print(f"❌ UNEXPECTED: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ NETWORK ERROR: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_validation_rules()
    print("\n" + "=" * 60)
    print("VALIDATION TESTING COMPLETE")
    print("=" * 60)
