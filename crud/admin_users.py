from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID, uuid4
from models.database import supabase
from core.security import get_password_hash
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class AdminUserBase(BaseModel):
    """Base schema for admin user data."""
    email: EmailStr

class AdminUserCreate(AdminUserBase):
    """Schema for creating an admin user."""
    password: str

class AdminUserUpdate(BaseModel):
    """Schema for updating an admin user."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AdminUser(AdminUserBase):
    """Schema for returning admin user data."""
    id: UUID
    is_verified: bool
    otp: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

async def create_admin_user(admin: AdminUserCreate) -> AdminUser:
    """Create a new admin user with UUID."""
    try:
        data = admin.model_dump()
        data["id"] = str(uuid4())  # Explicitly generate UUID
        data["hashed_password"] = get_password_hash(data.pop("password"))
        data["is_verified"] = False
        response = supabase.table("admin_users").insert(data).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create admin user")
        logger.info(f"Created admin user: {admin.email}")
        return AdminUser(**response.data[0])
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_admin_user_by_email(email: str) -> Optional[AdminUser]:
    """Retrieve an admin user by email."""
    try:
        response = supabase.table("admin_users").select("*").eq("email", email).execute()
        if response.data:
            return AdminUser(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error retrieving admin user {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def update_admin_user(admin_id: UUID, admin: AdminUserUpdate) -> AdminUser:
    """Update an admin user's details."""
    try:
        data = admin.model_dump(exclude_unset=True)
        if "password" in data:
            data["hashed_password"] = get_password_hash(data.pop("password"))
        response = supabase.table("admin_users").update(data).eq("id", str(admin_id)).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
        logger.info(f"Updated admin user with ID: {admin_id}")
        return AdminUser(**response.data[0])
    except Exception as e:
        logger.error(f"Error updating admin user {admin_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def delete_admin_user(admin_id: UUID) -> None:
    """Delete an admin user by ID."""
    try:
        response = supabase.table("admin_users").delete().eq("id", str(admin_id)).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
        logger.info(f"Deleted admin user with ID: {admin_id}")
    except Exception as e:
        logger.error(f"Error deleting admin user {admin_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")