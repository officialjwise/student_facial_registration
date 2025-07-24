from models.database import supabase
from schemas.students import StudentCreate, Student
from fastapi import HTTPException, status
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

async def create_student(student: StudentCreate, face_embedding: List[float]) -> Student:
    """Create a new student in the database."""
    try:
        data = student.dict(exclude={"face_image"})
        data["face_embedding"] = face_embedding
        response = supabase.table("students").insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create student")
        logger.info(f"Created student with ID: {response.data[0]['id']}")
        return Student(**response.data[0])
    except Exception as e:
        logger.error(f"Error creating student: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_student_by_id(student_id: int) -> Optional[Student]:
    """Retrieve a student by ID."""
    try:
        response = supabase.table("students").select("*").eq("id", student_id).execute()
        if response.data:
            return Student(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error retrieving student {student_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_all_students() -> List[Student]:
    """Retrieve all students."""
    try:
        response = supabase.table("students").select("*").execute()
        return [Student(**student) for student in response.data]
    except Exception as e:
        logger.error(f"Error retrieving students: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")