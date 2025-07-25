from fastapi import APIRouter, Depends, HTTPException, status
from schemas.departments import DepartmentCreate, DepartmentUpdate, Department
from schemas.responses import HTTPResponse
from crud.departments import create_department, get_department_by_id, get_departments_by_college, get_all_departments, update_department, delete_department
from api.dependencies import get_current_admin
from uuid import UUID
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=HTTPResponse[Department], status_code=status.HTTP_201_CREATED)
async def create_new_department(department: DepartmentCreate, _=Depends(get_current_admin)):
    """Create a new department."""
    result = await create_department(department)
    return HTTPResponse(
        message="Department created successfully",
        status_code=status.HTTP_201_CREATED,
        count=1,
        data=[result]
    )

@router.get("/{department_id}", response_model=HTTPResponse[Department])
async def get_department(department_id: UUID, _=Depends(get_current_admin)):
    """Retrieve a department by ID."""
    result = await get_department_by_id(department_id)
    return HTTPResponse(
        message="Department retrieved successfully",
        status_code=status.HTTP_200_OK,
        count=1,
        data=[result]
    )

@router.get("/", response_model=HTTPResponse[Department])
async def list_departments(college_id: Optional[UUID] = None):
    """Retrieve all departments, optionally filtered by college."""
    if college_id:
        result = await get_departments_by_college(college_id)
        message = f"Departments for college {college_id} retrieved successfully"
    else:
        result = await get_all_departments()
        message = "All departments retrieved successfully"
    
    return HTTPResponse(
        message=message,
        status_code=status.HTTP_200_OK,
        count=len(result),
        data=result
    )

@router.put("/{department_id}", response_model=HTTPResponse[Department])
async def update_department_details(department_id: UUID, department: DepartmentUpdate, _=Depends(get_current_admin)):
    """Update a department's details."""
    result = await update_department(department_id, department)
    return HTTPResponse(
        message="Department updated successfully",
        status_code=status.HTTP_200_OK,
        count=1,
        data=[result]
    )

@router.delete("/{department_id}", response_model=HTTPResponse[None])
async def delete_department_record(department_id: UUID, _=Depends(get_current_admin)):
    """Delete a department by ID."""
    await delete_department(department_id)
    return HTTPResponse(
        message="Department deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
        count=0,
        data=None
    )