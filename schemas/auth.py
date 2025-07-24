from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class AdminCreate(BaseModel):
    """Schema for admin registration."""
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class AdminLogin(BaseModel):
    """Schema for admin login."""
    email: EmailStr
    password: str

class OTPVerify(BaseModel):
    """Schema for OTP verification."""
    email: EmailStr
    otp: str

    @validator("otp")
    def validate_otp(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be a 6-digit number")
        return v

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str