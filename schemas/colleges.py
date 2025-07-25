from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class CollegeBase(BaseModel):
    """Base schema for college data."""
    name: str

class CollegeCreate(CollegeBase):
    """Schema for creating a college."""
    pass

class CollegeUpdate(BaseModel):
    """Schema for updating a college."""
    name: Optional[str]

class College(CollegeBase):
    """Schema for returning college data."""
    id: UUID
    created_at: str

    class Config:
        from_attributes = True