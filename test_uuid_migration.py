#!/usr/bin/env python3

"""
Test script to check if the application can start with UUID changes
This will test the imports and basic application structure without hitting the database
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        # Test basic imports
        from uuid import UUID
        print("✓ UUID import successful")
        
        # Test model imports
        from models.admin_users import AdminUser
        from models.students import Student
        from models.colleges import College
        from models.departments import Department
        from models.recognition_logs import RecognitionLog
        print("✓ Model imports successful")
        
        # Test schema imports
        from schemas.auth import AdminCreate
        from schemas.students import StudentCreate
        from schemas.colleges import CollegeCreate
        from schemas.departments import DepartmentCreate
        print("✓ Schema imports successful")
        
        # Test CRUD imports
        from crud.colleges import create_college
        from crud.departments import create_department
        print("✓ CRUD imports successful")
        
        # Test router imports
        from api.routers.colleges import router as college_router
        from api.routers.departments import router as dept_router
        print("✓ Router imports successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {str(e)}")
        return False

def test_uuid_handling():
    """Test UUID handling in schemas."""
    print("\nTesting UUID handling...")
    
    try:
        from uuid import uuid4
        from schemas.colleges import College
        
        # Test creating a schema with UUID
        test_uuid = uuid4()
        college_data = {
            "id": test_uuid,
            "name": "Test College",
            "created_at": "2025-01-01T00:00:00Z"
        }
        
        college = College(**college_data)
        print(f"✓ UUID schema validation successful: {college.id}")
        
        return True
        
    except Exception as e:
        print(f"✗ UUID handling failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("UUID Migration Test")
    print("=" * 40)
    
    import_success = test_imports()
    uuid_success = test_uuid_handling()
    
    if import_success and uuid_success:
        print("\n✓ All tests passed! UUID migration code is ready.")
        print("Next steps:")
        print("1. Run the database migration SQL in Supabase")
        print("2. Test the application with real data")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please fix the issues before proceeding.")
        sys.exit(1)
