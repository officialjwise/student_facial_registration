from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminUserBase(BaseModel):
    """Base schema for admin user data."""
    email: EmailStr

class AdminUserCreate(AdminUserBase):
    """Schema for creating an admin user."""
    password: str

class AdminUserUpdate(BaseModel):
    """Schema for updating an admin user."""
    email: Optional[EmailStr]
    password: Optional[str]

class AdminUser(AdminUserBase):
    """Schema for returning admin user data."""
    id: int
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True