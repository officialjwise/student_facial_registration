from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from schemas.students import StudentCreate, StudentUpdate, Student
from crud.students import create_student, get_student_by_id, get_all_students, update_student, delete_student
from services.face_recognition import extract_face_embedding, recognize_face
from services.recognition_logs import log_recognition
from api.dependencies import get_current_admin
from typing import List
from uuid import UUID
import base64
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=Student, status_code=status.HTTP_201_CREATED)
async def register_student(student: StudentCreate, _=Depends(get_current_admin)):
    """Register a new student with facial embedding."""
    try:
        image_data = base64.b64decode(student.face_image)
        embedding = await extract_face_embedding(image_data)
        if not embedding:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No face detected in image")
        
        student_record = await create_student(student, embedding.tolist())
        return student_record
    except Exception as e:
        logger.error(f"Error registering student: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register student")

@router.get("/{student_id}", response_model=Student)
async def get_student(student_id: UUID, _=Depends(get_current_admin)):
    """Retrieve a student by ID."""
    student = await get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student

@router.get("/", response_model=List[Student])
async def list_students(_=Depends(get_current_admin)):
    """Retrieve all students."""
    return await get_all_students()

@router.put("/{student_id}", response_model=Student)
async def update_student_details(student_id: UUID, student: StudentUpdate, _=Depends(get_current_admin)):
    """Update a student's details."""
    updated_student = await update_student(student_id, student)
    return updated_student

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_record(student_id: UUID, _=Depends(get_current_admin)):
    """Delete a student by ID."""
    await delete_student(student_id)
    return None

@router.post("/recognize")
async def recognize_student(file: UploadFile = File(...), _=Depends(get_current_admin)):
    """Recognize a student from an uploaded image."""
    try:
        image_data = await file.read()
        result = await recognize_face(image_data)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching student found")
        
        student_id, confidence = result
        student = await get_student_by_id(student_id)
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        
        await log_recognition(student_id, 1 - confidence, file.filename)
        return {"student": student, "confidence": 1 - confidence}
    except Exception as e:
        logger.error(f"Error recognizing student: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Face recognition failed")