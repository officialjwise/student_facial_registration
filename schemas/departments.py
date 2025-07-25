from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class DepartmentBase(BaseModel):
    """Base schema for department data."""
    name: str
    college_id: UUID

class DepartmentCreate(DepartmentBase):
    """Schema for creating a department."""
    pass

class DepartmentUpdate(BaseModel):
    """Schema for updating a department."""
    name: Optional[str]
    college_id: Optional[UUID]

class Department(DepartmentBase):
    """Schema for returning department data."""
    id: UUID
    created_at: str

    class Config:
        from_attributes = True