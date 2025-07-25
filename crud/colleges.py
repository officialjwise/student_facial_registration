from models.database import supabase
from schemas.colleges import CollegeCreate, CollegeUpdate, College
from fastapi import HTTPException, status
from typing import List, Optional
import logging

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
        logger.error(f"Error creating college: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_college_by_id(college_id: int) -> Optional[College]:
    """Retrieve a college by ID."""
    try:
        response = supabase.table("colleges").select("*").eq("id", college_id).execute()
        if response.data:
            return College(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Error retrieving college {college_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def get_all_colleges() -> List[College]:
    """Retrieve all colleges."""
    try:
        response = supabase.table("colleges").select("*").execute()
        return [College(**college) for college in response.data]
    except Exception as e:
        logger.error(f"Error retrieving colleges: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def update_college(college_id: int, college: CollegeUpdate) -> College:
    """Update a college's details."""
    try:
        response = supabase.table("colleges").update(college.dict(exclude_unset=True)).eq("id", college_id).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="College not found")
        logger.info(f"Updated college with ID: {college_id}")
        return College(**response.data[0])
    except Exception as e:
        logger.error(f"Error updating college {college_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

async def delete_college(college_id: int) -> None:
    """Delete a college by ID."""
    try:
        response = supabase.table("colleges").delete().eq("id", college_id).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="College not found")
        logger.info(f"Deleted college with ID: {college_id}")
    except Exception as e:
        logger.error(f"Error deleting college {college_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")