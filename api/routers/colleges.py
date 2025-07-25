from fastapi import APIRouter, Depends, HTTPException, status
from schemas.colleges import CollegeCreate, CollegeUpdate, College
from crud.colleges import create_college, get_college_by_id, get_all_colleges, update_college, delete_college
from api.dependencies import get_current_admin
import logging
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/colleges", tags=["Colleges"])

@router.post("/", response_model=College, status_code=status.HTTP_201_CREATED)
async def create_new_college(college: CollegeCreate, _=Depends(get_current_admin)):
    """Create a new college."""
    return await create_college(college)

@router.get("/{college_id}", response_model=College)
async def get_college(college_id: int, _=Depends(get_current_admin)):
    """Retrieve a college by ID."""
    college = await get_college_by_id(college_id)
    if not college:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="College not found")
    return college

@router.get("/", response_model=List[College])
async def list_colleges():
    """Retrieve all colleges."""
    return await get_all_colleges()

@router.put("/{college_id}", response_model=College)
async def update_college_details(college_id: int, college: CollegeUpdate, _=Depends(get_current_admin)):
    """Update a college's details."""
    return await update_college(college_id, college)

@router.delete("/{college_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_college_record(college_id: int, _=Depends(get_current_admin)):
    """Delete a college by ID."""
    await delete_college(college_id)
    return None