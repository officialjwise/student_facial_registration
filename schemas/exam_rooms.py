from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ExamRoomBase(BaseModel):
    """Base schema for exam room data."""
    room_code: str
    room_name: str
    index_start: str
    index_end: str
    capacity: Optional[int] = None
    description: Optional[str] = None

class ExamRoomCreate(ExamRoomBase):
    """Schema for creating an exam room assignment."""
    pass

class ExamRoomUpdate(BaseModel):
    """Schema for updating an exam room assignment."""
    room_code: Optional[str] = None
    room_name: Optional[str] = None
    index_start: Optional[str] = None
    index_end: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None

class ExamRoom(ExamRoomBase):
    """Schema for returning exam room data."""
    id: UUID
    created_at: str
    updated_at: Optional[str] = None
    assigned_students_count: Optional[int] = 0
    assigned_students: Optional[list] = []

    class Config:
        from_attributes = True

class ExamRoomWithStudents(ExamRoom):
    """Schema for exam room data with detailed student information."""
    students_in_range: list = []
    students_registered: list = []
    capacity_utilization: Optional[float] = 0.0

class RoomRecognitionRequest(BaseModel):
    """Schema for room-based face recognition request."""
    face_image: str  # Base64 encoded image
    room_code: str   # Room identifier

class RecognitionValidationResponse(BaseModel):
    """Schema for recognition validation response."""
    status: str  # "valid" or "invalid"
    beep_type: str  # "confirmation" or "warning"
    student_id: Optional[UUID] = None
    student_name: Optional[str] = None
    index_number: Optional[str] = None
    room_code: str
    room_name: Optional[str] = None
    message: str
    timestamp: datetime
