#!/usr/bin/env python3
"""
Script to discover the actual database table structure and test minimal student creation
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_minimal_student_creation():
    """Test with only the absolutely essential fields"""
    print("🔍 Testing minimal student creation to discover database schema...")
    
    # Start with the bare minimum fields
    minimal_tests = [
        {
            "name": "Only required API fields",
            "data": {
                "student_id": "20240003",
                "index_number": "1234569",
                "first_name": "Test",
                "last_name": "User",
                "email": "test.user@knust.edu.gh",
                "college_id": "83bfdd76-a625-45b4-9298-d799e419f6ea",
                "department_id": "ea4fdb2f-0731-4af1-bd05-596edcf0090d"
            }
        },
        {
            "name": "Even more minimal - no UUIDs",
            "data": {
                "student_id": "20240004",
                "index_number": "1234570",
                "first_name": "Test2",
                "last_name": "User2",
                "email": "test2.user@knust.edu.gh"
            }
        }
    ]
    
    for test in minimal_tests:
        print(f"\n📋 Testing: {test['name']}")
        try:
            response = requests.post(f"{BASE_URL}/students/", json=test['data'])
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("   ✅ SUCCESS!")
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
    
    return False

def check_existing_students():
    """Check if we can get existing students to see the actual schema"""
    print("\n🔍 Checking existing students to see actual database schema...")
    try:
        response = requests.get(f"{BASE_URL}/students/")
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                print("✅ Found existing students!")
                print("📋 Actual database fields:")
                student = data['data'][0]
                for key, value in student.items():
                    print(f"   - {key}: {type(value).__name__} = {value}")
                return student.keys()
            else:
                print("⚠️  No existing students found")
        else:
            print(f"❌ Failed to get students: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking students: {str(e)}")
    
    return None

if __name__ == "__main__":
    print("🚀 Database Schema Discovery Tool")
    print("=" * 50)
    
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
    
    # Check existing students first
    actual_fields = check_existing_students()
    
    # Test minimal creation
    success = test_minimal_student_creation()
    
    if not success:
        print("\n🔧 RECOMMENDATIONS:")
        print("1. Check the database table structure in Supabase")
        print("2. Ensure all required database columns exist")
        print("3. Check foreign key constraints")
        if actual_fields:
            print(f"4. Database expects these fields: {list(actual_fields)}")
    
    print("\n✅ Discovery complete!")
