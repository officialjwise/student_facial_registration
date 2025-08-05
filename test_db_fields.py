#!/usr/bin/env python3
"""
Systematic field testing to discover which database columns exist
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.supabase import supabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_fields():
    """Test what fields actually exist in the students table"""
    print("🔍 Testing database fields systematically...")
    
    # Test data with all possible fields
    base_data = {
        "student_id": "99999999",
        "index_number": "9999999",
        "first_name": "Test",
        "last_name": "User",
        "email": "test99999@knust.edu.gh",
        "college_id": "83bfdd76-a625-45b4-9298-d799e419f6ea",
        "department_id": "ea4fdb2f-0731-4af1-bd05-596edcf0090d"
    }
    
    optional_fields = [
        "middle_name",
        "phone_number", 
        "date_of_birth",
        "gender",
        "program", 
        "level",
        "face_embedding"
    ]
    
    # First test with just base required fields
    print("\n📋 Testing base required fields...")
    try:
        response = supabase.table("students").insert(base_data).execute()
        if response.data:
            print("✅ Base fields work!")
            created_id = response.data[0]['id']
            
            # Clean up
            supabase.table("students").delete().eq("id", created_id).execute()
            
            # Now test each optional field
            print("\n📋 Testing optional fields...")
            for field in optional_fields:
                test_data = base_data.copy()
                test_data["student_id"] = f"9999999{len(field)}"  # Make unique
                test_data["index_number"] = f"999999{len(field)}"  # Make unique
                test_data["email"] = f"test{len(field)}@knust.edu.gh"  # Make unique
                
                if field == "face_embedding":
                    test_data[field] = [0.1, 0.2, 0.3]  # Sample embedding
                elif field == "date_of_birth":
                    test_data[field] = "1990-01-01"
                else:
                    test_data[field] = f"test_{field}"
                
                try:
                    response = supabase.table("students").insert(test_data).execute()
                    if response.data:
                        print(f"   ✅ {field}: EXISTS")
                        # Clean up
                        supabase.table("students").delete().eq("id", response.data[0]['id']).execute()
                    else:
                        print(f"   ❌ {field}: FAILED - {response}")
                except Exception as e:
                    print(f"   ❌ {field}: ERROR - {str(e)}")
            
        else:
            print(f"❌ Base fields failed: {response}")
            
    except Exception as e:
        print(f"❌ Base test failed: {str(e)}")
        
        # If base test fails, let's see what the error is about
        if "column" in str(e).lower():
            missing_column = str(e).split("'")[1] if "'" in str(e) else "unknown"
            print(f"🔍 Missing column detected: {missing_column}")
            
            # Try with even more minimal data
            minimal_data = {
                "student_id": "88888888",
                "index_number": "8888888", 
                "first_name": "Test",
                "last_name": "User",
                "email": "test88888@knust.edu.gh"
            }
            
            print("\n📋 Testing ultra-minimal fields...")
            try:
                response = supabase.table("students").insert(minimal_data).execute()
                if response.data:
                    print("✅ Ultra-minimal works!")
                    supabase.table("students").delete().eq("id", response.data[0]['id']).execute()
                else:
                    print(f"❌ Ultra-minimal failed: {response}")
            except Exception as e2:
                print(f"❌ Ultra-minimal error: {str(e2)}")

if __name__ == "__main__":
    print("🚀 Direct Database Field Testing")
    print("=" * 50)
    
    try:
        # Test the database connection first
        print("🔗 Testing database connection...")
        response = supabase.table("colleges").select("id, name").limit(1).execute()
        if response.data:
            print("✅ Database connection works!")
            asyncio.run(test_database_fields())
        else:
            print("❌ Database connection failed")
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        print("Check your .env file and Supabase configuration")
