from models.database import supabase
from schemas.departments import DepartmentCreate, DepartmentUpdate, Department
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

async def create_department(department: DepartmentCreate) -> Department:
    """Create a new department."""
    try:
        response = supabase.table("departments").insert(department.dict()).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create department")
        logger.info(f"Created department: {department.name}")
        return Department(**response.data[0])
    except Exception as e:
        logger.error(f"Error creating department: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_department_by_id(department_id: UUID) -> Optional[Department]:
    """Retrieve a department by ID."""
    try:
        response = supabase.table("departments").select("*").eq("id", str(department_id)).execute()
        if response.data:
            return Department(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error retrieving department {department_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_departments_by_college(college_id: UUID) -> List[Department]:
    """Retrieve all departments for a college."""
    try:
        response = supabase.table("departments").select("*").eq("college_id", str(college_id)).execute()
        return [Department(**department) for department in response.data]
    except Exception as e:
        logger.error(f"Error retrieving departments for college {college_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_all_departments() -> List[Department]:
    """Retrieve all departments."""
    try:
        response = supabase.table("departments").select("*").execute()
        return [Department(**department) for department in response.data]
    except Exception as e:
        logger.error(f"Error retrieving departments: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def update_department(department_id: UUID, department: DepartmentUpdate) -> Department:
    """Update a department's details."""
    try:
        response = supabase.table("departments").update(department.dict(exclude_unset=True)).eq("id", str(department_id)).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        logger.info(f"Updated department with ID: {department_id}")
        return Department(**response.data[0])
    except Exception as e:
        logger.error(f"Error updating department {department_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def delete_department(department_id: UUID) -> None:
    """Delete a department by ID."""
    try:
        response = supabase.table("departments").delete().eq("id", str(department_id)).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        logger.info(f"Deleted department with ID: {department_id}")
    except Exception as e:
        logger.error(f"Error deleting department {department_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")