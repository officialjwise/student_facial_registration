from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class College(BaseModel):
    id: Optional[UUID]
    name: str
    created_at: Optional[str]

    class Config:
        from_attributes = True