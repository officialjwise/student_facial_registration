from fastapi import APIRouter, Depends, HTTPException, status
from schemas.departments import DepartmentCreate, DepartmentUpdate, Department
from crud.departments import create_department, get_department_by_id, get_departments_by_college, get_all_departments, update_department, delete_department
from api.dependencies import get_current_admin
from uuid import UUID
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=Department, status_code=status.HTTP_201_CREATED)
async def create_new_department(department: DepartmentCreate, _=Depends(get_current_admin)):
    """Create a new department."""
    return await create_department(department)

@router.get("/{department_id}", response_model=Department)
async def get_department(department_id: UUID, _=Depends(get_current_admin)):
    """Retrieve a department by ID."""
    department = await get_department_by_id(department_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return department

@router.get("/", response_model=List[Department])
async def list_departments(college_id: Optional[UUID] = None):
    """Retrieve all departments, optionally filtered by college."""
    if college_id:
        return await get_departments_by_college(college_id)
    return await get_all_departments()

@router.put("/{department_id}", response_model=Department)
async def update_department_details(department_id: UUID, department: DepartmentUpdate, _=Depends(get_current_admin)):
    """Update a department's details."""
    return await update_department(department_id, department)

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department_record(department_id: UUID, _=Depends(get_current_admin)):
    """Delete a department by ID."""
    await delete_department(department_id)
    return None