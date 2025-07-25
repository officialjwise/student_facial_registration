from crud.recognition_logs import create_recognition_log
from schemas.recognition_logs import RecognitionLogCreate
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

async def log_recognition(student_id: int, confidence: float, camera_source: str) -> None:
    """Log a facial recognition event."""
    try:
        log = RecognitionLogCreate(
            student_id=student_id,
            confidence_score=confidence,
            camera_source=camera_source
        )
        await create_recognition_log(log)
        logger.info(f"Logged recognition for student ID: {student_id} with confidence: {confidence}")
    except Exception as e:
        logger.error(f"Error logging recognition: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to log recognition")