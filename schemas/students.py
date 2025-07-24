from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
import re

class StudentBase(BaseModel):
    """Base schema for student data."""
    student_id: str
    index_number: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    email: EmailStr
    college_id: int
    department_id: int

    @validator("student_id")
    def validate_student_id(cls, v):
        if not re.match(r"^\d{8}$", v):
            raise ValueError("Student ID must be exactly 8 digits")
        return v

    @validator("index_number")
    def validate_index_number(cls, v):
        if not re.match(r"^\d{7}$", v):
            raise ValueError("Index Number must be exactly 7 digits")
        return v

class StudentCreate(StudentBase):
    """Schema for creating a new student with an image."""
    face_image: str  # Base64-encoded image string

class StudentUpdate(BaseModel):
    """Schema for updating student data."""
    student_id: Optional[str]
    index_number: Optional[str]
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    college_id: Optional[int]
    department_id: Optional[int]
    face_image: Optional[str]

    @validator("student_id")
    def validate_student_id(cls, v):
        if v and not re.match(r"^\d{8}$", v):
            raise ValueError("Student ID must be exactly 8 digits")
        return v

    @validator("index_number")
    def validate_index_number(cls, v):
        if v and not re.match(r"^\d{7}$", v):
            raise ValueError("Index Number must be exactly 7 digits")
        return v

class Student(StudentBase):
    """Schema for returning student data."""
    id: int
    face_embedding: List[float]
    created_at: str

    class Config:
        from_attributes = True