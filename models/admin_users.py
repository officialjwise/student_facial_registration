from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class AdminUser(BaseModel):
    id: Optional[UUID]
    email: str
    hashed_password: str
    is_verified: bool
    otp: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True