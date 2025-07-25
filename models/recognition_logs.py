from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RecognitionLog(BaseModel):
    id: Optional[UUID]
    student_id: UUID
    confidence_score: float
    camera_source: Optional[str]
    timestamp: Optional[str]

    class Config:
        from_attributes = True