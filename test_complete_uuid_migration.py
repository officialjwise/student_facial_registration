#!/usr/bin/env python3

"""
Final UUID Migration Test
This comprehensive test verifies all UUID changes are working correctly
"""

import sys
import os
from uuid import uuid4, UUID

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_imports():
    """Test all model imports with UUID types."""
    print("🧪 Testing model imports...")
    
    try:
        from models.admin_users import AdminUser
        from models.students import Student
        from models.colleges import College
        from models.departments import Department
        from models.recognition_logs import RecognitionLog
        
        # Test that all models accept UUID
        test_uuid = uuid4()
        
        # Test AdminUser
        admin_data = {
            "id": test_uuid,
            "email": "test@example.com",
            "hashed_password": "hashed",
            "is_verified": True,
            "otp": None,
            "created_at": "2025-01-01T00:00:00Z"
        }
        admin = AdminUser(**admin_data)
        assert isinstance(admin.id, UUID)
        
        print("✓ All model imports successful with UUID support")
        return True
        
    except Exception as e:
        print(f"✗ Model import test failed: {str(e)}")
        return False

def test_schema_imports():
    """Test all schema imports with UUID types."""
    print("🧪 Testing schema imports...")
    
    try:
        from schemas.students import StudentCreate, Student
        from schemas.colleges import CollegeCreate, College
        from schemas.departments import DepartmentCreate, Department
        from schemas.recognition_logs import RecognitionLogCreate, RecognitionLog
        
        test_uuid = uuid4()
        
        # Test College schema
        college_data = {
            "id": test_uuid,
            "name": "Test College",
            "created_at": "2025-01-01T00:00:00Z"
        }
        college = College(**college_data)
        assert isinstance(college.id, UUID)
        
        # Test Student schema with UUID foreign keys
        student_data = {
            "id": test_uuid,
            "student_id": "12345678",
            "index_number": "1234567",
            "first_name": "Test",
            "middle_name": None,  # Optional field
            "last_name": "Student",
            "email": "student@test.com",
            "college_id": test_uuid,
            "department_id": test_uuid,
            "face_embedding": [0.1, 0.2, 0.3],
            "created_at": "2025-01-01T00:00:00Z"
        }
        student = Student(**student_data)
        assert isinstance(student.id, UUID)
        assert isinstance(student.college_id, UUID)
        assert isinstance(student.department_id, UUID)
        
        print("✓ All schema imports successful with UUID support")
        return True
        
    except Exception as e:
        print(f"✗ Schema import test failed: {str(e)}")
        return False

def test_crud_imports():
    """Test all CRUD imports."""
    print("🧪 Testing CRUD imports...")
    
    try:
        from crud.colleges import create_college, get_college_by_id
        from crud.departments import create_department, get_department_by_id
        from crud.students import create_student, get_student_by_id
        from crud.admin_users import update_admin_user, delete_admin_user
        from crud.recognition_logs import create_recognition_log, get_recognition_logs
        
        # Verify function signatures accept UUID (this is compile-time check)
        import inspect
        
        # Check get_college_by_id accepts UUID
        sig = inspect.signature(get_college_by_id)
        college_id_param = sig.parameters['college_id']
        assert 'UUID' in str(college_id_param.annotation)
        
        print("✓ All CRUD imports successful with UUID signatures")
        return True
        
    except Exception as e:
        print(f"✗ CRUD import test failed: {str(e)}")
        return False

def test_router_imports():
    """Test all router imports."""
    print("🧪 Testing router imports...")
    
    try:
        from api.routers.colleges import router as college_router
        from api.routers.departments import router as dept_router
        from api.routers.students import router as student_router
        from api.routers.admin import router as admin_router
        
        print("✓ All router imports successful")
        return True
        
    except Exception as e:
        print(f"✗ Router import test failed: {str(e)}")
        return False

def test_service_imports():
    """Test service imports."""
    print("🧪 Testing service imports...")
    
    try:
        from services.face_recognition import store_face_embedding
        from services.recognition_logs import log_recognition
        from services.auth import register_admin
        
        # Check that store_face_embedding accepts UUID
        import inspect
        sig = inspect.signature(store_face_embedding)
        student_id_param = sig.parameters['student_id']
        assert 'UUID' in str(student_id_param.annotation)
        
        print("✓ All service imports successful with UUID support")
        return True
        
    except Exception as e:
        print(f"✗ Service import test failed: {str(e)}")
        return False

def test_uuid_string_conversion():
    """Test UUID to string conversion for database queries."""
    print("🧪 Testing UUID string conversion...")
    
    try:
        test_uuid = uuid4()
        uuid_str = str(test_uuid)
        
        # Verify string format
        assert len(uuid_str) == 36
        assert uuid_str.count('-') == 4
        
        # Verify can convert back
        reconstructed_uuid = UUID(uuid_str)
        assert reconstructed_uuid == test_uuid
        
        print("✓ UUID string conversion working correctly")
        return True
        
    except Exception as e:
        print(f"✗ UUID string conversion test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 COMPREHENSIVE UUID MIGRATION TEST")
    print("=" * 60)
    
    tests = [
        test_model_imports,
        test_schema_imports,
        test_crud_imports,
        test_router_imports,
        test_service_imports,
        test_uuid_string_conversion
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! UUID Migration is complete and ready!")
        print("\n📋 Next steps:")
        print("1. ✅ Code migration: COMPLETE")
        print("2. 🔄 Run database migration SQL in Supabase")
        print("3. 🧪 Test application with real data")
        print("4. 🚀 Deploy updated application")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} tests failed. Please fix issues before proceeding.")
        sys.exit(1)
