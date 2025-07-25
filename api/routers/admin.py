from fastapi import APIRouter, Depends, HTTPException, status
from schemas.students import Student
from schemas.recognition_logs import RecognitionLog
from schemas.admin_users import AdminUser, AdminUserUpdate
from schemas.responses import HTTPResponse
from crud.students import get_all_students
from crud.recognition_logs import get_recognition_logs
from crud.admin_users import update_admin_user, delete_admin_user
from api.dependencies import get_current_admin
from models.database import supabase
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats", response_model=HTTPResponse[Dict])
async def get_admin_stats(_=Depends(get_current_admin)):
    """Retrieve admin dashboard statistics."""
    try:
        student_count = len(await get_all_students())
        log_count = len(await get_recognition_logs())
        
        # Calculate date 7 days ago
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        recent_logs = await get_recognition_logs(start_date=seven_days_ago)
        
        stats = {
            "total_students": student_count,
            "total_recognitions": log_count,
            "recent_recognitions": len(recent_logs)
        }
        
        logger.info("Admin stats retrieved")
        return HTTPResponse(
            message="Admin statistics retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[stats]
        )
    except Exception as e:
        logger.error(f"Error retrieving admin stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve stats")

@router.get("/students", response_model=HTTPResponse[Student])
async def list_all_students(_=Depends(get_current_admin)):
    """Retrieve all students for admin."""
    result = await get_all_students()
    return HTTPResponse(
        message="All students retrieved successfully",
        status_code=status.HTTP_200_OK,
        count=len(result),
        data=result
    )

@router.get("/recognition-logs", response_model=HTTPResponse[RecognitionLog])
async def list_recognition_logs(
    student_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    _=Depends(get_current_admin)
):
    """Retrieve recognition logs with optional filters."""
    result = await get_recognition_logs(student_id, start_date, end_date)
    message = "Recognition logs retrieved successfully"
    if student_id:
        message = f"Recognition logs for student {student_id} retrieved successfully"
    
    return HTTPResponse(
        message=message,
        status_code=status.HTTP_200_OK,
        count=len(result),
        data=result
    )

@router.put("/{admin_id}", response_model=HTTPResponse[AdminUser])
async def update_admin_details(admin_id: UUID, admin: AdminUserUpdate, _=Depends(get_current_admin)):
    """Update an admin user's details."""
    result = await update_admin_user(admin_id, admin)
    return HTTPResponse(
        message="Admin user updated successfully",
        status_code=status.HTTP_200_OK,
        count=1,
        data=[result]
    )

@router.delete("/{admin_id}", response_model=HTTPResponse[None])
async def delete_admin_user_record(admin_id: UUID, _=Depends(get_current_admin)):
    """Delete an admin user by ID."""
    await delete_admin_user(admin_id)
    return HTTPResponse(
        message="Admin user deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
        count=0,
        data=None
    )