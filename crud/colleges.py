from models.database import supabase
from schemas.colleges import CollegeCreate, CollegeUpdate, College
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
import logging
import json

logger = logging.getLogger(__name__)

async def create_college(college: CollegeCreate) -> College:
    """Create a new college."""
    try:
        response = supabase.table("colleges").insert(college.dict()).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create college")
        logger.info(f"Created college: {college.name}")
        return College(**response.data[0])
    except Exception as e:
        error_str = str(e)
        if "colleges_name_key" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A college with the name '{college.name}' already exists"
            )
        logger.error(f"Error creating college: {error_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def get_college_by_id(college_id: UUID) -> Optional[College]:
    """Retrieve a college by ID."""
    try:
        response = supabase.table("colleges").select("*").eq("id", str(college_id)).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"College with ID {college_id} not found"
            )
        return College(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving college {college_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve college"
        )

async def get_all_colleges() -> List[College]:
    """Retrieve all colleges."""
    try:
        response = supabase.table("colleges").select("*").execute()
        return [College(**college) for college in response.data]
    except Exception as e:
        logger.error(f"Error retrieving colleges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve colleges"
        )

async def update_college(college_id: UUID, college: CollegeUpdate) -> College:
    """Update a college's details."""
    try:
        response = supabase.table("colleges").update(college.dict(exclude_unset=True)).eq("id", str(college_id)).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"College with ID {college_id} not found"
            )
        logger.info(f"Updated college with ID: {college_id}")
        return College(**response.data[0])
    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e)
        if "colleges_name_key" in error_str:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A college with the provided name already exists"
            )
        logger.error(f"Error updating college {college_id}: {error_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update college"
        )

async def delete_college(college_id: UUID) -> None:
    """Delete a college by ID."""
    try:
        response = supabase.table("colleges").delete().eq("id", str(college_id)).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"College with ID {college_id} not found"
            )
        logger.info(f"Deleted college with ID: {college_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting college {college_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete college"
        )