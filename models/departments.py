from pydantic import BaseModel
from typing import Optional

class Department(BaseModel):
    id: Optional[int]
    name: str
    college_id: int
    created_at: Optional[str]

    class Config:
        from_attributes = True