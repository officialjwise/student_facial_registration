from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import numpy as np

class Student(BaseModel):
    id: Optional[UUID]
    student_id: str
    index_number: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    email: str
    college_id: UUID
    department_id: UUID
    face_embedding: List[float]
    created_at: Optional[str]

    class Config:
        from_attributes = True