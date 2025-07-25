from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class Department(BaseModel):
    id: Optional[UUID]
    name: str
    college_id: UUID
    created_at: Optional[str]

    class Config:
        from_attributes = True