from crud.students import create_student, get_student_by_id
from schemas.students import StudentCreate
from services.face_recognition import extract_face_embedding
from fastapi import HTTPException, status
import base64
import logging

logger = logging.getLogger(__name__)

async def register_student(student: StudentCreate) -> dict:
    """Register a student with facial embedding."""
    try:
        image_data = base64.b64decode(student.face_image)
        embedding = await extract_face_embedding(image_data)
        if not embedding:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No face detected in image")
        
        student_record = await create_student(student, embedding.tolist())
        logger.info(f"Registered student: {student_record.student_id}")
        return {"student": student_record, "message": "Student registered successfully"}
    except Exception as e:
        logger.error(f"Error registering student: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register student")