from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from schemas.students import StudentCreate, Student
from crud.students import create_student, get_student_by_id
from services.face_recognition import extract_face_embedding, recognize_face
from models.database import supabase
from api.dependencies import get_current_admin
import base64
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=Student, status_code=status.HTTP_201_CREATED)
async def register_student(student: StudentCreate, _=Depends(get_current_admin)):
    """Register a new student with facial embedding."""
    try:
        # Decode base64 image
        image_data = base64.b64decode(student.face_image)
        embedding = await extract_face_embedding(image_data)
        if not embedding:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No face detected in image")
        
        student_record = await create_student(student, embedding.tolist())
        logger.info(f"Registered student: {student_record.student_id}")
        return student_record
    except Exception as e:
        logger.error(f"Error registering student: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register student")

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
        
        # Log recognition event
        supabase.table("recognition_logs").insert({
            "student_id": student_id,
            "confidence_score": float(confidence),
            "camera_source": file.filename,
            "timestamp": "now()"
        }).execute()
        
        logger.info(f"Recognized student: {student.student_id} with confidence: {1 - confidence}")
        return {"student": student, "confidence": 1 - confidence}
    except Exception as e:
        logger.error(f"Error recognizing student: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Face recognition failed")