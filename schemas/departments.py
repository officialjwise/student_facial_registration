from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class DepartmentBase(BaseModel):
    """Base schema for department data."""
    name: str
    college_id: UUID
    department_head: Optional[str] = None
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    """Schema for creating a department."""
    pass

class DepartmentUpdate(BaseModel):
    """Schema for updating a department."""
    name: Optional[str] = None
    college_id: Optional[UUID] = None
    department_head: Optional[str] = None
    description: Optional[str] = None

class Department(DepartmentBase):
    """Schema for returning department data."""
    id: UUID
    created_at: str
    college_name: Optional[str] = None  # For frontend table display

    class Config:
        from_attributes = True