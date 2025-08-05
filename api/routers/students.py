from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from schemas.students import StudentCreate, StudentUpdate, Student, FaceDetectionRequest
from schemas.responses import HTTPResponse
from crud.students import create_student, get_student_by_id, get_all_students, update_student, delete_student
from services.face_recognition import extract_face_embedding, recognize_face, detect_faces_with_bounding_boxes
from services.recognition_logs import log_recognition
from api.dependencies import get_current_admin
from typing import List
from uuid import UUID
import base64
import binascii
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["🎓 Students"])

@router.post("/", response_model=HTTPResponse[Student], status_code=status.HTTP_201_CREATED)
async def register_student(student: StudentCreate):
    """Register a new student with optional facial embedding."""
    try:
        # Handle face image validation (now optional)
        embedding = None
        image_data = None
        
        if student.face_image:
            try:
                # Check if the base64 string has the proper prefix
                face_image_data = student.face_image
                if face_image_data.startswith('data:image/'):
                    # Remove data URL prefix if present
                    face_image_data = face_image_data.split(',', 1)[-1]
                
                image_data = base64.b64decode(face_image_data)
                
                if len(image_data) == 0:
                    logger.warning("Empty image data provided, proceeding without face embedding")
                else:
                    # Extract face embedding (allow registration without face detection)
                    try:
                        embedding = await extract_face_embedding(image_data)
                        if embedding is not None:
                            logger.info("Face detected and embedding extracted successfully")
                        else:
                            logger.warning("No face detected, but allowing registration to proceed")
                    except HTTPException as he:
                        # If face detection fails, log but allow registration to continue
                        logger.warning(f"Face detection failed: {he.detail}, but allowing registration to proceed")
                    except Exception as e:
                        logger.warning(f"Face recognition error: {str(e)}, but allowing registration to proceed")
                        
            except binascii.Error:
                logger.warning("Invalid base64 image format, proceeding without face embedding")
            except Exception as e:
                logger.warning(f"Error processing face image: {str(e)}, proceeding without face embedding")
        else:
            logger.info("No face image provided, registering student without face embedding")
        
        # Create student record (with or without embedding)
        embedding_list = embedding.tolist() if embedding is not None else None
        student_record = await create_student(student, embedding_list)
        return HTTPResponse(
            message="Student registered successfully" + (" with face recognition" if embedding_list else " without face recognition"),
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

@router.post("/admin/create", response_model=HTTPResponse[Student], status_code=status.HTTP_201_CREATED)
async def admin_create_student(student: StudentCreate, _=Depends(get_current_admin)):
    """Admin endpoint to register a new student with facial embedding."""
    try:
        # Validate face image
        try:
            if not student.face_image:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Face image is required."
                )
            
            # Check if the base64 string has the proper prefix
            face_image_data = student.face_image
            if face_image_data.startswith('data:image/'):
                # Remove data URL prefix if present
                face_image_data = face_image_data.split(',', 1)[-1]
            
            image_data = base64.b64decode(face_image_data)
            
            if len(image_data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Empty image data provided."
                )
                
        except binascii.Error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid base64 image format. Please ensure the image is properly base64 encoded."
            )
        except Exception as e:
            logger.error(f"Error processing face image: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid face image format. Image must be base64 encoded."
            )

        # Extract face embedding (allow creation without face detection)
        embedding = None
        try:
            embedding = await extract_face_embedding(image_data)
            if embedding is not None:
                logger.info("Face detected and embedding extracted successfully")
            else:
                logger.warning("No face detected, but allowing creation to proceed")
        except HTTPException as he:
            # If face detection fails, log but allow creation to continue
            logger.warning(f"Face detection failed: {he.detail}, but allowing creation to proceed")
        except Exception as e:
            logger.warning(f"Face recognition error: {str(e)}, but allowing creation to proceed")
        
        # Create student record (with or without embedding)
        embedding_list = embedding.tolist() if embedding is not None else None
        student_record = await create_student(student, embedding_list)
        return HTTPResponse(
            message="Student created successfully by admin",
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
        
        logger.error(f"Error creating student: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create student. Please try again."
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
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid file type. Please upload an image file (JPEG or PNG)"
            )
            
        # Validate file size (max 10MB)
        if hasattr(image, 'size') and image.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File too large. Maximum size is 10MB"
            )
            
        # Read image contents
        try:
            contents = await image.read()
            if not contents or len(contents) == 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Empty image file provided"
                )
        except Exception as e:
            logger.error(f"Error reading image file: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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

@router.post("/detect-face")
async def detect_face_preview(request: dict):
    """
    Detect faces in an image and return bounding box coordinates for preview.
    Useful for showing face detection overlay before registration.
    """
    try:
        face_image = request.get("face_image", "")
        logger.info(f"Face detection request received. Image length: {len(face_image) if face_image else 0}")
        
        # Validate and decode image
        if not face_image:
            logger.warning("No face image provided")
            return {
                "message": "No face image provided",
                "status_code": 422,
                "count": 1,
                "data": [{
                    "faces_detected": 0,
                    "face_locations": [],
                    "image_dimensions": (0, 0),
                    "face_encodings": [],
                    "error": "Face image is required"
                }]
            }
        
        # Handle data URL prefix
        face_image_data = face_image
        if face_image_data.startswith('data:image/'):
            face_image_data = face_image_data.split(',', 1)[-1]
            logger.info("Removed data URL prefix from image")
        
        try:
            image_data = base64.b64decode(face_image_data)
            logger.info(f"Successfully decoded base64 image. Size: {len(image_data)} bytes")
        except binascii.Error as e:
            logger.error(f"Base64 decode error: {str(e)}")
            return {
                "message": "Invalid base64 image format",
                "status_code": 422,
                "count": 1,
                "data": [{
                    "faces_detected": 0,
                    "face_locations": [],
                    "image_dimensions": (0, 0),
                    "face_encodings": [],
                    "error": "Invalid base64 image format"
                }]
            }
        
        # For now, return mock data to test the endpoint
        # Later we can integrate with actual face detection
        mock_result = {
            "faces_detected": 1,
            "face_locations": [[50, 200, 150, 100]],  # [top, right, bottom, left]
            "image_dimensions": (640, 480),
            "face_encodings": []
        }
        
        return {
            "message": f"Face detection complete. Found {mock_result['faces_detected']} face(s).",
            "status_code": 200,
            "count": 1,
            "data": [mock_result]
        }
        
    except Exception as e:
        logger.error(f"Face detection preview error: {str(e)}")
        return {
            "message": f"Face detection failed: {str(e)}",
            "status_code": 500,
            "count": 1,
            "data": [{
                "faces_detected": 0,
                "face_locations": [],
                "image_dimensions": (0, 0),
                "face_encodings": [],
                "error": str(e)
            }]
        }

@router.post("/test-detect", response_model=HTTPResponse, status_code=status.HTTP_200_OK)
async def test_detect_face(request: FaceDetectionRequest):
    """
    Test endpoint for face detection debugging.
    """
    try:
        logger.info(f"Received face detection request with image length: {len(request.face_image) if request.face_image else 0}")
        
        # Just return a test response without calling face recognition
        test_result = {
            "faces_detected": 1,
            "face_locations": [[50, 200, 150, 100]],
            "image_dimensions": (640, 480),
            "face_encodings": []
        }
        
        return HTTPResponse(
            message="Test face detection complete.",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[test_result]
        )
        
    except Exception as e:
        logger.error(f"Test face detection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}"
        )