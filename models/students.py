from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date
import numpy as np

class Student(BaseModel):
    id: Optional[UUID] = None
    student_id: str
    index_number: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    program: Optional[str] = None
    level: Optional[str] = None
    college_id: UUID
    department_id: UUID
    face_image: Optional[str] = None  # Add face_image field
    face_embedding: Optional[List[float]] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True