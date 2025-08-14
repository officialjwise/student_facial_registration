from models.database import supabase
from schemas.students import StudentCreate, StudentUpdate, Student
from fastapi import HTTPException, status
from typing import Optional, List
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

async def create_student(student: StudentCreate, face_embedding: Optional[List[float]] = None) -> Student:
    """Create a new student in the database."""
    try:
        # Get all data from the student object (include face_image now)
        data = student.dict()
        
        # Remove fields that don't exist in the database table
        # Based on the error, these fields are not in the actual database schema
        fields_to_remove = ["date_of_birth", "gender", "program", "level", "phone_number", "middle_name"]
        for field in fields_to_remove:
            data.pop(field, None)
        
        # Convert UUID fields to strings for JSON serialization
        if "college_id" in data and data["college_id"]:
            data["college_id"] = str(data["college_id"])
        if "department_id" in data and data["department_id"]:
            data["department_id"] = str(data["department_id"])
            
        # CRITICAL: face_embedding is NOT NULL in database
        # If no face embedding provided, use an empty array instead of None
        if face_embedding is None:
            data["face_embedding"] = []  # Empty array instead of None
            logger.info("No face embedding provided, using empty array")
        else:
            data["face_embedding"] = face_embedding
            logger.info("Face embedding provided, using actual embedding")
        
        logger.info(f"Creating student with data: {data}")
        response = supabase.table("students").insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create student")
        logger.info(f"Created student with ID: {response.data[0]['id']} {'with' if face_embedding else 'without'} face embedding")
        return Student(**response.data[0])
    except Exception as e:
        error_str = str(e)
        logger.error(f"Error creating student: {error_str}")
        logger.error(f"Exception type: {type(e)}")
        
        # Check for database constraint violations (more comprehensive check)
        if ("duplicate key" in error_str.lower() or 
            "23505" in error_str or
            "unique constraint" in error_str.lower() or
            "foreign key constraint" in error_str.lower() or
            "23503" in error_str):
            # Let the router handle the specific database constraint error
            logger.info(f"Database constraint violation detected, re-raising: {error_str}")
            raise e
        
        # For other errors, return generic 500
        logger.error(f"Generic error occurred, returning 500: {error_str}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_student_by_id(student_id: UUID) -> Optional[Student]:
    """Retrieve a student by ID."""
    try:
        response = supabase.table("students").select("*").eq("id", str(student_id)).execute()
        if response.data:
            return Student(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error retrieving student {student_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_student_by_index_number(index_number: str) -> Optional[Student]:
    """Retrieve a student by their index number."""
    try:
        response = supabase.table("students").select("*").eq("index_number", index_number).execute()
        if response.data:
            return Student(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error retrieving student with index number {index_number}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_all_students() -> List[Student]:
    """Retrieve all students."""
    try:
        response = supabase.table("students").select("*").execute()
        return [Student(**student) for student in response.data]
    except Exception as e:
        logger.error(f"Error retrieving students: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def update_student(student_id: UUID, student: StudentUpdate) -> Student:
    """Update a student's details."""
    try:
        data = student.dict(exclude_unset=True)
        # Face image updates are now allowed
        
        # Remove fields that don't exist in the database table
        fields_to_remove = ["date_of_birth", "gender", "program", "level", "phone_number", "middle_name"]
        for field in fields_to_remove:
            data.pop(field, None)
        
        # Convert UUID fields to strings for JSON serialization
        if "college_id" in data and data["college_id"]:
            data["college_id"] = str(data["college_id"])
        if "department_id" in data and data["department_id"]:
            data["department_id"] = str(data["department_id"])
            
        response = supabase.table("students").update(data).eq("id", str(student_id)).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        logger.info(f"Updated student with ID: {student_id}")
        return Student(**response.data[0])
    except Exception as e:
        logger.error(f"Error updating student {student_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def delete_student(student_id: UUID) -> None:
    """Delete a student by ID."""
    try:
        response = supabase.table("students").delete().eq("id", str(student_id)).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        logger.info(f"Deleted student with ID: {student_id}")
    except Exception as e:
        logger.error(f"Error deleting student {student_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")