from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import AdminCreate, OTPVerify, Token
from core.security import verify_password, get_password_hash, create_access_token
from core.email import send_otp_email, generate_otp
from models.database import supabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_admin(admin: AdminCreate):
    """Register a new admin and send OTP for verification."""
    try:
        # Check if email already exists
        if supabase.table("admin_users").select("email").eq("email", admin.email).execute().data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        hashed_password = get_password_hash(admin.password)
        otp = generate_otp()
        
        response = supabase.table("admin_users").insert({
            "email": admin.email,
            "hashed_password": hashed_password,
            "is_verified": False,
            "otp": otp
        }).execute()
        
        await send_otp_email(admin.email, otp)
        logger.info(f"Admin registered: {admin.email}, OTP sent")
        return {"message": "Admin registered, OTP sent to email"}
    except Exception as e:
        logger.error(f"Error registering admin: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register admin")

@router.post("/verify-otp")
async def verify_otp(otp_data: OTPVerify):
    """Verify OTP for admin account activation."""
    try:
        response = supabase.table("admin_users").select("*").eq("email", otp_data.email).eq("otp", otp_data.otp).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP or email")
        
        supabase.table("admin_users").update({"is_verified": True, "otp": None}).eq("email", otp_data.email).execute()
        logger.info(f"Admin verified: {otp_data.email}")
        return {"message": "Account verified successfully"}
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OTP verification failed")

@router.post("/login", response_model=Token)
async def login_admin(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate admin and issue JWT token."""
    try:
        response = supabase.table("admin_users").select("*").eq("email", form_data.username).eq("is_verified", True).execute()
        if not response.data or not verify_password(form_data.password, response.data[0]["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": form_data.username})
        logger.info(f"Admin logged in: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error logging in admin: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")