from pydantic import BaseModel
from typing import Optional

class DepartmentBase(BaseModel):
    """Base schema for department data."""
    name: str
    college_id: int

class DepartmentCreate(DepartmentBase):
    """Schema for creating a department."""
    pass

class DepartmentUpdate(BaseModel):
    """Schema for updating a department."""
    name: Optional[str]
    college_id: Optional[int]

class Department(DepartmentBase):
    """Schema for returning department data."""
    id: int
    created_at: str

    class Config:
        from_attributes = True