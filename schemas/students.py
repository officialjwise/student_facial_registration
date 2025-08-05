from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import date
import re

class StudentBase(BaseModel):
    """Base schema for student data."""
    student_id: str
    index_number: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    program: Optional[str] = None
    level: Optional[str] = None
    college_id: UUID
    department_id: UUID

    @validator("student_id")
    def validate_student_id(cls, v):
        if not re.match(r"^\d{8}$", v):
            raise ValueError("Student ID must be exactly 8 digits")
        return v

    @validator("index_number")
    def validate_index_number(cls, v):
        if not re.match(r"^\d{7}$", v):  # 7 digits for index number
            raise ValueError("Index Number must be exactly 7 digits")
        return v

class StudentCreate(StudentBase):
    """Schema for creating a new student with an optional image."""
    face_image: Optional[str] = None  # Base64-encoded image string (optional)

class StudentUpdate(BaseModel):
    """Schema for updating student data."""
    student_id: Optional[str] = None
    index_number: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    program: Optional[str] = None
    level: Optional[str] = None
    college_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    face_image: Optional[str] = None

    @validator("student_id")
    def validate_student_id(cls, v):
        if v and not re.match(r"^\d{8}$", v):
            raise ValueError("Student ID must be exactly 8 digits")
        return v

    @validator("index_number")
    def validate_index_number(cls, v):
        if v and not re.match(r"^\d{10}$", v):  # Updated to match frontend
            raise ValueError("Index Number must be exactly 10 digits")
        return v

class Student(StudentBase):
    """Schema for returning student data."""
    id: UUID
    face_embedding: Optional[List[float]] = None
    created_at: str

    class Config:
        from_attributes = True

class FaceDetectionRequest(BaseModel):
    """Schema for face detection requests."""
    face_image: str  # Base64-encoded image string

class FaceDetectionResponse(BaseModel):
    """Schema for face detection response."""
    faces_detected: int
    face_locations: List[List[int]]  # [(top, right, bottom, left), ...]
    image_dimensions: Tuple[int, int]  # (width, height)
    face_encodings: Optional[List[List[float]]] = None
    error: Optional[str] = None