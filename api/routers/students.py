from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from schemas.students import StudentCreate, StudentUpdate, Student
from schemas.responses import HTTPResponse
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

@router.post("/", response_model=HTTPResponse[Student], status_code=status.HTTP_201_CREATED)
async def register_student(student: StudentCreate, _=Depends(get_current_admin)):
    """Register a new student with facial embedding."""
    try:
        # Validate face image
        try:
            image_data = base64.b64decode(student.face_image)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid face image format. Image must be base64 encoded."
            )

        # Extract face embedding
        embedding = await extract_face_embedding(image_data)
        if not embedding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the uploaded image. Please provide a clear photo with a face."
            )
        
        # Create student record
        student_record = await create_student(student, embedding.tolist())
        return HTTPResponse(
            message="Student registered successfully",
            status_code=status.HTTP_201_CREATED,
            count=1,
            data=[student_record]
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower():
            if "students_student_id_key" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A student with ID {student.student_id} already exists"
                )
            elif "students_index_number_key" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A student with index number {student.index_number} already exists"
                )
            elif "students_email_key" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A student with email {student.email} already exists"
                )
        
        logger.error(f"Error registering student: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register student. Please try again."
        )

@router.get("/{student_id}", response_model=HTTPResponse[Student])
async def get_student(student_id: UUID, _=Depends(get_current_admin)):
    """Retrieve a student by ID."""
    result = await get_student_by_id(student_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return HTTPResponse(
        message="Student retrieved successfully",
        status_code=status.HTTP_200_OK,
        count=1,
        data=[result]
    )

@router.get("/", response_model=HTTPResponse[Student])
async def list_students(_=Depends(get_current_admin)):
    """Retrieve all students."""
    result = await get_all_students()
    return HTTPResponse(
        message="Students retrieved successfully",
        status_code=status.HTTP_200_OK,
        count=len(result),
        data=result
    )

@router.put("/{student_id}", response_model=HTTPResponse[Student])
async def update_student_details(student_id: UUID, student: StudentUpdate, _=Depends(get_current_admin)):
    """Update a student's details."""
    result = await update_student(student_id, student)
    return HTTPResponse(
        message="Student updated successfully",
        status_code=status.HTTP_200_OK,
        count=1,
        data=[result]
    )

@router.delete("/{student_id}", response_model=HTTPResponse[None])
async def delete_student_record(student_id: UUID, _=Depends(get_current_admin)):
    """Delete a student by ID."""
    await delete_student(student_id)
    return HTTPResponse(
        message="Student deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
        count=0,
        data=None
    )

@router.post("/recognize", response_model=HTTPResponse[Student])
async def recognize_student(image: UploadFile = File(...)):
    """Recognize a student from an uploaded face image."""
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an image file"
            )
            
        # Read image contents
        try:
            contents = await image.read()
            if not contents:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Empty image file provided"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading image file: {str(e)}"
            )

        # Recognize face
        student = await recognize_face(contents)
        if student:
            await log_recognition(student.id, True)
            return HTTPResponse(
                message="Student recognized successfully",
                status_code=status.HTTP_200_OK,
                count=1,
                data=[student]
            )
            
        # Log failed recognition attempt
        await log_recognition(None, False)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching student found. Please try again with a clearer photo"
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in face recognition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process face recognition. Please try again"
        )