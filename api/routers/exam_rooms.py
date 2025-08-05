from fastapi import APIRouter, HTTPException, status, Depends
from schemas.exam_rooms import (
    ExamRoomCreate, ExamRoomUpdate, ExamRoom, 
    RoomRecognitionRequest, RecognitionValidationResponse
)
from schemas.responses import HTTPResponse
from crud.exam_rooms import (
    create_exam_room, get_exam_room_by_id, get_all_exam_rooms,
    update_exam_room, delete_exam_room, validate_student_in_room,
    log_room_recognition, get_exam_room_by_code, get_exam_room_with_students,
    get_students_in_index_range
)
from crud.students import get_student_by_index_number
from services.face_recognition import recognize_face_from_base64
from api.dependencies import get_current_admin
from uuid import UUID
from datetime import datetime
import logging
import base64
import binascii

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exam-room", tags=["🏛️ Exam Room Management"])

@router.post("/assign", response_model=HTTPResponse[ExamRoom], status_code=status.HTTP_201_CREATED)
async def assign_room(room: ExamRoomCreate, _=Depends(get_current_admin)):
    """
    Assign an index number range to a specific exam room.
    Admin authentication required.
    """
    try:
        result = await create_exam_room(room)
        return HTTPResponse(
            message=f"Exam room '{room.room_code}' assigned successfully",
            status_code=status.HTTP_201_CREATED,
            count=1,
            data=[result]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning exam room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign exam room"
        )

@router.get("/mappings", response_model=HTTPResponse[ExamRoom])
async def get_room_mappings():
    """
    Retrieve all current exam room mappings.
    Public endpoint for viewing room assignments.
    """
    try:
        result = await get_all_exam_rooms()
        return HTTPResponse(
            message="Exam room mappings retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=len(result),
            data=result
        )
    except Exception as e:
        logger.error(f"Error retrieving room mappings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve room mappings"
        )

@router.get("/mappings/{room_id}", response_model=HTTPResponse[ExamRoom])
async def get_room_mapping(room_id: UUID, _=Depends(get_current_admin)):
    """
    Retrieve a specific exam room mapping by ID.
    Admin authentication required.
    """
    try:
        result = await get_exam_room_by_id(room_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam room mapping not found"
            )
        
        return HTTPResponse(
            message="Exam room mapping retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[result]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving room mapping: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve room mapping"
        )

@router.put("/assign/{room_id}", response_model=HTTPResponse[ExamRoom])
async def update_room_assignment(room_id: UUID, room: ExamRoomUpdate, _=Depends(get_current_admin)):
    """
    Update an existing exam room assignment.
    Admin authentication required.
    """
    try:
        result = await update_exam_room(room_id, room)
        return HTTPResponse(
            message="Exam room assignment updated successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[result]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating room assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update room assignment"
        )

@router.delete("/assign/{room_id}", response_model=HTTPResponse[None])
async def delete_room_assignment(room_id: UUID, _=Depends(get_current_admin)):
    """
    Delete an exam room assignment.
    Admin authentication required.
    """
    try:
        await delete_exam_room(room_id)
        return HTTPResponse(
            message="Exam room assignment deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
            count=0,
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting room assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete room assignment"
        )

@router.post("/recognize", response_model=HTTPResponse[RecognitionValidationResponse])
async def recognize_in_room(request: RoomRecognitionRequest):
    """
    Perform facial recognition with room validation.
    
    Process:
    1. Recognize the student from face image
    2. Validate if student's index number is assigned to the specified room
    3. Return validation result with beep feedback type
    4. Log the recognition attempt
    """
    try:
        # Validate face image format
        if not request.face_image:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Face image is required"
            )
        
        # Process base64 image
        try:
            face_image_data = request.face_image
            if face_image_data.startswith('data:image/'):
                face_image_data = face_image_data.split(',', 1)[-1]
            
            image_data = base64.b64decode(face_image_data)
            if len(image_data) == 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Empty image data provided"
                )
                
        except binascii.Error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid base64 image format"
            )
        
        # Perform face recognition
        try:
            recognized_student = await recognize_face_from_base64(image_data)
        except Exception as e:
            logger.error(f"Face recognition failed: {str(e)}")
            # Log failed recognition attempt
            await log_room_recognition(
                student_id=None,
                room_code=request.room_code,
                status="invalid",
                beep_type="warning",
                index_number=None,
                message="Face recognition failed - no match found"
            )
            
            response = RecognitionValidationResponse(
                status="invalid",
                beep_type="warning",
                room_code=request.room_code,
                message="Face recognition failed - no student match found",
                timestamp=datetime.utcnow()
            )
            
            return HTTPResponse(
                message="Recognition failed",
                status_code=status.HTTP_200_OK,
                count=1,
                data=[response]
            )
        
        if not recognized_student:
            # Log unrecognized face
            await log_room_recognition(
                student_id=None,
                room_code=request.room_code,
                status="invalid",
                beep_type="warning",
                index_number=None,
                message="Unrecognized face - student not found in database"
            )
            
            response = RecognitionValidationResponse(
                status="invalid",
                beep_type="warning",
                room_code=request.room_code,
                message="Student not recognized - face not found in database",
                timestamp=datetime.utcnow()
            )
            
            return HTTPResponse(
                message="Student not recognized",
                status_code=status.HTTP_200_OK,
                count=1,
                data=[response]
            )
        
        # Validate room assignment
        is_valid, validation_message = await validate_student_in_room(
            recognized_student.index_number, 
            request.room_code
        )
        
        # Get room details for response
        room = await get_exam_room_by_code(request.room_code)
        room_name = room.room_name if room else "Unknown Room"
        
        # Determine status and beep type
        if is_valid:
            status_result = "valid"
            beep_type = "confirmation"
            message = f"✅ {recognized_student.name} verified in {room_name}"
        else:
            status_result = "invalid"
            beep_type = "warning"
            message = f"⚠️ {recognized_student.name} not assigned to {room_name}"
        
        # Log the recognition attempt
        await log_room_recognition(
            student_id=recognized_student.id,
            room_code=request.room_code,
            status=status_result,
            beep_type=beep_type,
            index_number=recognized_student.index_number,
            message=validation_message
        )
        
        # Create response
        response = RecognitionValidationResponse(
            status=status_result,
            beep_type=beep_type,
            student_id=recognized_student.id,
            student_name=recognized_student.name,
            index_number=recognized_student.index_number,
            room_code=request.room_code,
            room_name=room_name,
            message=message,
            timestamp=datetime.utcnow()
        )
        
        return HTTPResponse(
            message="Recognition completed",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[response]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in room recognition: {str(e)}")
        
        # Log system error
        await log_room_recognition(
            student_id=None,
            room_code=request.room_code,
            status="invalid",
            beep_type="warning",
            index_number=None,
            message=f"System error: {str(e)}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Recognition system error"
        )

@router.get("/validate/{room_code}/{index_number}")
async def validate_student_assignment(room_code: str, index_number: str):
    """
    Validate if a student's index number is assigned to a specific room.
    Utility endpoint for testing room assignments.
    """
    try:
        is_valid, message = await validate_student_in_room(index_number, room_code)
        
        return HTTPResponse(
            message=message,
            status_code=status.HTTP_200_OK,
            count=1,
            data=[{
                "index_number": index_number,
                "room_code": room_code,
                "is_valid": is_valid,
                "validation_message": message
            }]
        )
        
    except Exception as e:
        logger.error(f"Error validating student assignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation error"
        )

@router.get("/mappings/{room_id}/students", response_model=HTTPResponse[dict])
async def get_room_with_students(room_id: UUID, _=Depends(get_current_admin)):
    """
    Retrieve a specific exam room with detailed student assignment information.
    Shows all students assigned to this room based on index number range.
    Admin authentication required.
    """
    try:
        result = await get_exam_room_with_students(room_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam room mapping not found"
            )
        
        return HTTPResponse(
            message=f"Room {result['room_code']} details with {result['assigned_students_count']} assigned students",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[result]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving room with students: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve room details"
        )

@router.get("/assignments/preview")
async def preview_room_assignments(index_start: str, index_end: str, _=Depends(get_current_admin)):
    """
    Preview how many students would be assigned to a room with the given index range.
    Helps admin validate room capacity before creating assignment.
    """
    try:
        students_in_range = await get_students_in_index_range(index_start, index_end)
        
        preview_data = {
            "index_start": index_start,
            "index_end": index_end,
            "total_students": len(students_in_range),
            "students_preview": students_in_range[:10],
            "has_more": len(students_in_range) > 10
        }
        
        return HTTPResponse(
            message=f"Found {len(students_in_range)} students in range {index_start}-{index_end}",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[preview_data]
        )
        
    except Exception as e:
        logger.error(f"Error previewing assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview assignments"
        )
