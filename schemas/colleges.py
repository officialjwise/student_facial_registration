from pydantic import BaseModel
from typing import Optional

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
    id: int
    created_at: str

    class Config:
        from_attributes = True