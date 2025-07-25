from models.database import supabase
from schemas.recognition_logs import RecognitionLogCreate, RecognitionLog
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

async def create_recognition_log(log: RecognitionLogCreate) -> RecognitionLog:
    """Create a new recognition log."""
    try:
        response = supabase.table("recognition_logs").insert(log.dict()).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create recognition log")
        logger.info(f"Created recognition log for student ID: {log.student_id}")
        return RecognitionLog(**response.data[0])
    except Exception as e:
        logger.error(f"Error creating recognition log: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_recognition_logs(student_id: Optional[UUID] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[RecognitionLog]:
    """Retrieve recognition logs with optional filters."""
    try:
        query = supabase.table("recognition_logs").select("*")
        if student_id:
            query = query.eq("student_id", str(student_id))
        if start_date:
            query = query.gte("timestamp", start_date)
        if end_date:
            query = query.lte("timestamp", end_date)
        response = query.execute()
        return [RecognitionLog(**log) for log in response.data]
    except Exception as e:
        logger.error(f"Error retrieving recognition logs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")