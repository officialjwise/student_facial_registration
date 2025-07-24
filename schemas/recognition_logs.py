from pydantic import BaseModel
from typing import Optional

class RecognitionLogBase(BaseModel):
    """Base schema for recognition log data."""
    student_id: int
    confidence_score: float
    camera_source: Optional[str]

class RecognitionLogCreate(RecognitionLogBase):
    """Schema for creating a recognition log."""
    pass

class RecognitionLog(RecognitionLogBase):
    """Schema for returning recognition log data."""
    id: int
    timestamp: str

    class Config:
        from_attributes = True