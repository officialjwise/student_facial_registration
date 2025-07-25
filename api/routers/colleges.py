from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from schemas.colleges import CollegeCreate, CollegeUpdate, College
from schemas.responses import HTTPResponse
from crud.colleges import create_college, get_college_by_id, get_all_colleges, update_college, delete_college
from api.dependencies import get_current_admin
from uuid import UUID
import logging
from typing import List

logger = logging.getLogger(__name__)

security = HTTPBearer()
router = APIRouter(prefix="/colleges", tags=["🏫 Colleges"])

@router.post("/", response_model=HTTPResponse[College], status_code=status.HTTP_201_CREATED, 
             summary="Create College", description="Create a new college (Admin only)")
async def create_new_college(college: CollegeCreate, _=Depends(get_current_admin)):
    """Create a new college."""
    result = await create_college(college)
    return HTTPResponse(
        message="College created successfully",
        status_code=status.HTTP_201_CREATED,
        count=1,
        data=[result]
    )

@router.get("/{college_id}", response_model=HTTPResponse[College],
            summary="Get College by ID", description="Retrieve a specific college by ID (Admin only)")
async def get_college(college_id: UUID, _=Depends(get_current_admin)):
    """Retrieve a college by ID."""
    result = await get_college_by_id(college_id)
    return HTTPResponse(
        message="College retrieved successfully",
        status_code=status.HTTP_200_OK,
        count=1,
        data=[result]
    )

@router.get("/", response_model=HTTPResponse[College],
            summary="List All Colleges", description="Get all colleges (Public endpoint)")
async def list_colleges():
    """Retrieve all colleges."""
    result = await get_all_colleges()
    return HTTPResponse(
        message="Colleges retrieved successfully",
        status_code=status.HTTP_200_OK,
        count=len(result),
        data=result
    )

@router.put("/{college_id}", response_model=HTTPResponse[College],
            summary="Update College", description="Update college details (Admin only)")
async def update_college_details(college_id: UUID, college: CollegeUpdate, _=Depends(get_current_admin)):
    """Update a college's details."""
    result = await update_college(college_id, college)
    return HTTPResponse(
        message="College updated successfully",
        status_code=status.HTTP_200_OK,
        count=1,
        data=[result]
    )

@router.delete("/{college_id}", response_model=HTTPResponse[None],
               summary="Delete College", description="Delete a college (Admin only)")
async def delete_college_record(college_id: UUID, _=Depends(get_current_admin)):
    """Delete a college by ID."""
    await delete_college(college_id)
    return HTTPResponse(
        message="College deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
        count=0,
        data=None
    )