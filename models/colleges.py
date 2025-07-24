from pydantic import BaseModel
from typing import Optional

class College(BaseModel):
    id: Optional[int]
    name: str
    created_at: Optional[str]

    class Config:
        from_attributes = True