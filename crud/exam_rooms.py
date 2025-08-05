from models.database import supabase
from schemas.exam_rooms import ExamRoomCreate, ExamRoomUpdate, ExamRoom
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

async def check_room_code_exists(room_code: str, exclude_id: Optional[str] = None) -> bool:
    """Check if a room code already exists."""
    query = supabase.table("exam_rooms").select("*").eq("room_code", room_code)
    if exclude_id:
        query = query.neq("id", exclude_id)
    response = query.execute()
    return len(response.data) > 0

async def check_index_range_overlap(index_start: str, index_end: str, exclude_id: Optional[str] = None) -> bool:
    """Check if index range overlaps with existing assignments."""
    try:
        # Get all existing room assignments
        query = supabase.table("exam_rooms").select("index_start, index_end")
        if exclude_id:
            query = query.neq("id", exclude_id)
        response = query.execute()
        
        # Check for overlaps
        for room in response.data:
            existing_start = room['index_start']
            existing_end = room['index_end']
            
            # Check if ranges overlap
            if (index_start <= existing_end and index_end >= existing_start):
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error checking index range overlap: {str(e)}")
        return False

async def create_exam_room(room: ExamRoomCreate) -> ExamRoom:
    """Create a new exam room assignment."""
    try:
        # Check if room code already exists
        if await check_room_code_exists(room.room_code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Room code '{room.room_code}' already exists"
            )
        
        # Check for index range overlap
        if await check_index_range_overlap(room.index_start, room.index_end):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Index range {room.index_start}-{room.index_end} overlaps with existing assignment"
            )
        
        # Validate index range
        if room.index_start > room.index_end:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Start index must be less than or equal to end index"
            )
        
        room_data = room.dict()
        response = supabase.table("exam_rooms").insert(room_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create exam room assignment"
            )
        
        logger.info(f"Created exam room assignment: {room.room_code}")
        return ExamRoom(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating exam room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def get_exam_room_by_id(room_id: UUID) -> Optional[ExamRoom]:
    """Retrieve an exam room by ID."""
    try:
        response = supabase.table("exam_rooms").select("*").eq("id", str(room_id)).execute()
        if response.data:
            return ExamRoom(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error retrieving exam room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def get_exam_room_by_code(room_code: str) -> Optional[ExamRoom]:
    """Retrieve an exam room by room code."""
    try:
        response = supabase.table("exam_rooms").select("*").eq("room_code", room_code).execute()
        if response.data:
            return ExamRoom(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error retrieving exam room by code {room_code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def get_all_exam_rooms() -> List[ExamRoom]:
    """Retrieve all exam room assignments with student counts."""
    try:
        response = supabase.table("exam_rooms").select("*").order("room_code").execute()
        
        rooms_with_counts = []
        for room_data in response.data:
            # Count students in this room's index range
            student_count = await count_students_in_room(
                room_data['room_code'],
                room_data['index_start'], 
                room_data['index_end']
            )
            
            # Create room object with student count
            room_dict = room_data.copy()
            room_dict['assigned_students_count'] = student_count
            
            rooms_with_counts.append(ExamRoom(**room_dict))
        
        return rooms_with_counts
    except Exception as e:
        logger.error(f"Error retrieving exam rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def update_exam_room(room_id: UUID, room: ExamRoomUpdate) -> ExamRoom:
    """Update an exam room assignment."""
    try:
        # Get current room data
        current_room = await get_exam_room_by_id(room_id)
        if not current_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam room not found"
            )
        
        update_data = room.dict(exclude_unset=True)
        
        # Check room code uniqueness if being updated
        if 'room_code' in update_data:
            if await check_room_code_exists(update_data['room_code'], str(room_id)):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Room code '{update_data['room_code']}' already exists"
                )
        
        # Check index range overlap if being updated
        if 'index_start' in update_data or 'index_end' in update_data:
            index_start = update_data.get('index_start', current_room.index_start)
            index_end = update_data.get('index_end', current_room.index_end)
            
            if index_start > index_end:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Start index must be less than or equal to end index"
                )
            
            if await check_index_range_overlap(index_start, index_end, str(room_id)):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Index range {index_start}-{index_end} overlaps with existing assignment"
                )
        
        response = supabase.table("exam_rooms").update(update_data).eq("id", str(room_id)).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam room not found"
            )
        
        logger.info(f"Updated exam room: {room_id}")
        return ExamRoom(**response.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating exam room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def delete_exam_room(room_id: UUID) -> None:
    """Delete an exam room assignment."""
    try:
        response = supabase.table("exam_rooms").delete().eq("id", str(room_id)).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam room not found"
            )
        logger.info(f"Deleted exam room: {room_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting exam room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def validate_student_in_room(index_number: str, room_code: str) -> tuple[bool, str]:
    """
    Validate if a student's index number is assigned to the given room.
    Returns (is_valid, message).
    """
    try:
        room = await get_exam_room_by_code(room_code)
        if not room:
            return False, f"Room '{room_code}' not found"
        
        # Check if index number falls within the room's assigned range
        if room.index_start <= index_number <= room.index_end:
            return True, f"Student {index_number} is correctly assigned to {room.room_name}"
        else:
            return False, f"Student {index_number} is not assigned to {room.room_name}. Assigned range: {room.index_start}-{room.index_end}"
    
    except Exception as e:
        logger.error(f"Error validating student in room: {str(e)}")
        return False, "Validation error occurred"

async def log_room_recognition(student_id: Optional[UUID], room_code: str, status: str, 
                              beep_type: str, index_number: Optional[str], message: str) -> None:
    """Log a room recognition attempt."""
    try:
        log_data = {
            "student_id": str(student_id) if student_id else None,
            "room_code": room_code,
            "status": status,
            "beep_type": beep_type,
            "index_number": index_number,
            "message": message
        }
        
        supabase.table("room_recognition_logs").insert(log_data).execute()
        logger.info(f"Logged room recognition: {status} for {index_number or 'unknown'} in {room_code}")
        
    except Exception as e:
        logger.error(f"Error logging room recognition: {str(e)}")
        # Don't raise exception here as logging failure shouldn't stop the main process

async def get_students_in_index_range(index_start: str, index_end: str) -> List[dict]:
    """Get all students within the specified index number range."""
    try:
        # Query students within the index range
        response = supabase.table("students").select(
            "id, name, index_number, email, phone, college, department"
        ).gte("index_number", index_start).lte("index_number", index_end).execute()
        
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"Error retrieving students in range {index_start}-{index_end}: {str(e)}")
        return []

async def count_students_in_room(room_code: str, index_start: str, index_end: str) -> int:
    """Count students assigned to a specific room based on index range."""
    try:
        response = supabase.table("students").select("id", count="exact").gte(
            "index_number", index_start
        ).lte("index_number", index_end).execute()
        
        return response.count if response.count else 0
    except Exception as e:
        logger.error(f"Error counting students for room {room_code}: {str(e)}")
        return 0

async def get_exam_room_with_students(room_id: UUID) -> Optional[dict]:
    """Retrieve an exam room with detailed student assignment information."""
    try:
        # Get room data
        room_response = supabase.table("exam_rooms").select("*").eq("id", str(room_id)).execute()
        if not room_response.data:
            return None
        
        room_data = room_response.data[0]
        
        # Get students in the index range
        students_in_range = await get_students_in_index_range(
            room_data['index_start'],
            room_data['index_end']
        )
        
        # Calculate capacity utilization
        capacity = room_data.get('capacity', 0)
        student_count = len(students_in_range)
        capacity_utilization = (student_count / capacity * 100) if capacity > 0 else 0
        
        return {
            **room_data,
            'assigned_students_count': student_count,
            'students_in_range': students_in_range,
            'capacity_utilization': round(capacity_utilization, 2),
            'is_overcapacity': student_count > capacity if capacity else False
        }
        
    except Exception as e:
        logger.error(f"Error retrieving exam room with students {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
