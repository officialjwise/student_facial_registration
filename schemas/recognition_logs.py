from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RecognitionLogBase(BaseModel):
    """Base schema for recognition log data."""
    student_id: UUID
    confidence_score: float
    camera_source: Optional[str]

class RecognitionLogCreate(RecognitionLogBase):
    """Schema for creating a recognition log."""
    pass

class RecognitionLog(RecognitionLogBase):
    """Schema for returning recognition log data."""
    id: UUID
    timestamp: str

    class Config:
        from_attributes = True