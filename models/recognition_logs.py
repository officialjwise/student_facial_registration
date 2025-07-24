from pydantic import BaseModel
from typing import Optional

class RecognitionLog(BaseModel):
    id: Optional[int]
    student_id: int
    confidence_score: float
    camera_source: Optional[str]
    timestamp: Optional[str]

    class Config:
        from_attributes = True