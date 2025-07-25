from fastapi import APIRouter, Depends, HTTPException, status
from schemas.students import Student
from schemas.recognition_logs import RecognitionLog
from schemas.admin_users import AdminUser, AdminUserUpdate
from crud.students import get_all_students
from crud.recognition_logs import get_recognition_logs
from crud.admin_users import update_admin_user, delete_admin_user
from api.dependencies import get_current_admin
from models.database import supabase
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
async def get_admin_stats(_=Depends(get_current_admin)):
    """Retrieve admin dashboard statistics."""
    try:
        student_count = len(await get_all_students())
        log_count = len(await get_recognition_logs())
        recent_logs = await get_recognition_logs(start_date="now() - interval '7 days'")
        
        logger.info("Admin stats retrieved")
        return {
            "total_students": student_count,
            "total_recognitions": log_count,
            "recent_recognitions": len(recent_logs)
        }
    except Exception as e:
        logger.error(f"Error retrieving admin stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve stats")

@router.get("/students", response_model=List[Student])
async def list_all_students(_=Depends(get_current_admin)):
    """Retrieve all students for admin."""
    return await get_all_students()

@router.get("/recognition-logs", response_model=List[RecognitionLog])
async def list_recognition_logs(
    student_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    _=Depends(get_current_admin)
):
    """Retrieve recognition logs with optional filters."""
    return await get_recognition_logs(student_id, start_date, end_date)

@router.put("/profile/{admin_id}", response_model=AdminUser)
async def update_admin_profile(admin_id: UUID, admin: AdminUserUpdate, current_admin=Depends(get_current_admin)):
    """Update admin profile."""
    if current_admin["id"] != str(admin_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update other admin's profile")
    return await update_admin_user(admin_id, admin)

@router.delete("/profile/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_profile(admin_id: UUID, current_admin=Depends(get_current_admin)):
    """Delete admin profile."""
    if current_admin["id"] != str(admin_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete other admin's profile")
    await delete_admin_user(admin_id)
    return None