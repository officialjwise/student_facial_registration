from models.database import supabase
from schemas.departments import DepartmentCreate, DepartmentUpdate, Department
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

async def check_department_exists(name: str, college_id: str, exclude_id: Optional[str] = None) -> bool:
    """Check if a department with the given name exists in the college."""
    query = supabase.table("departments").select("*").eq("name", name).eq("college_id", college_id)
    if exclude_id:
        query = query.neq("id", exclude_id)
    response = query.execute()
    return len(response.data) > 0

async def create_department(department: DepartmentCreate) -> Department:
    """Create a new department."""
    try:
        # Convert the department data to dict and ensure UUID is converted to string
        department_data = department.dict()
        department_data['college_id'] = str(department_data['college_id'])
        
        # Check if department with same name exists in the college
        if await check_department_exists(department.name, department_data['college_id']):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A department with the name '{department.name}' already exists in this college"
            )
        
        response = supabase.table("departments").insert(department_data).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create department")
        logger.info(f"Created department: {department.name}")
        return Department(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e)
        if "departments_name_college_id_key" in error_str or "duplicate key" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A department with the name '{department.name}' already exists in this college"
            )
        logger.error(f"Error creating department: {error_str}")
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
        # If name is being updated, check for duplicates
        update_data = department.dict(exclude_unset=True)
        if 'name' in update_data:
            # Get current department to check college_id
            current_dept = await get_department_by_id(department_id)
            if not current_dept:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
            
            # Use provided college_id or current one
            college_id = str(update_data.get('college_id', current_dept.college_id))
            
            # Check for duplicates, excluding current department
            if await check_department_exists(update_data['name'], college_id, str(department_id)):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A department with the name '{update_data['name']}' already exists in this college"
                )

        # Convert UUID to string if present
        if 'college_id' in update_data:
            update_data['college_id'] = str(update_data['college_id'])

        response = supabase.table("departments").update(update_data).eq("id", str(department_id)).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        logger.info(f"Updated department with ID: {department_id}")
        return Department(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e)
        if "departments_name_college_id_key" in error_str or "duplicate key" in error_str.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A department with this name already exists in this college"
            )
        logger.error(f"Error updating department {department_id}: {error_str}")
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