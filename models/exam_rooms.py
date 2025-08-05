from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ExamRoom(BaseModel):
    """Model for exam room assignments."""
    id: Optional[UUID]
    room_code: str
    room_name: str
    index_start: str
    index_end: str
    capacity: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True

class RoomRecognitionLog(BaseModel):
    """Model for room recognition attempts."""
    id: Optional[UUID]
    student_id: Optional[UUID]
    room_code: str
    status: str  # "valid" or "invalid"
    beep_type: str  # "confirmation" or "warning"
    index_number: Optional[str]
    message: str
    timestamp: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True
