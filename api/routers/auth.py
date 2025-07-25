from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import AdminCreate, OTPVerify, Token, AdminLoginOTP, LoginOTPVerify, RefreshTokenRequest
from core.security import verify_password, create_access_token, create_refresh_token, validate_refresh_token
from services.auth import register_admin, generate_login_otp, verify_login_otp
from models.database import supabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED,
             summary="Register Admin", description="Register a new admin account and send OTP verification")
async def register_admin_endpoint(admin: AdminCreate):
    """Register a new admin and send OTP for verification."""
    return await register_admin(admin)

@router.post("/verify-otp", summary="Verify Registration OTP", 
             description="Verify OTP code to activate admin account")
async def verify_otp(otp_data: OTPVerify):
    """Verify OTP for admin account activation."""
    try:
        response = supabase.table("admin_users").select("*").eq("email", otp_data.email).eq("otp_code", otp_data.otp).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP or email")
        
        supabase.table("admin_users").update({"is_verified": True, "otp_code": None}).eq("email", otp_data.email).execute()
        logger.info(f"Admin verified: {otp_data.email}")
        return {"message": "Account verified successfully"}
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="OTP verification failed")

@router.post("/login", response_model=Token, summary="Legacy Login", 
             description="Direct login with username/password (returns tokens immediately)")
async def login_admin(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate admin and issue JWT token (legacy endpoint)."""
    try:
        response = supabase.table("admin_users").select("*").eq("email", form_data.username).eq("is_verified", True).execute()
        if not response.data or not verify_password(form_data.password, response.data[0]["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": form_data.username})
        refresh_token = create_refresh_token(data={"sub": form_data.username})
        logger.info(f"Admin logged in: {form_data.username}")
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error logging in admin: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.post("/login-otp", summary="Request Login OTP", 
             description="Send OTP to email after password verification (recommended)")
async def request_login_otp(login_data: AdminLoginOTP):
    """Request OTP for admin login."""
    return await generate_login_otp(login_data.email, login_data.password)

@router.post("/verify-login-otp", response_model=Token, summary="Verify Login OTP",
             description="Verify login OTP and receive access + refresh tokens")
async def verify_login_otp_endpoint(otp_data: LoginOTPVerify):
    """Verify login OTP and get tokens."""
    return await verify_login_otp(otp_data.email, otp_data.otp)

@router.post("/refresh", response_model=Token, summary="Refresh Access Token",
             description="Get new access token using refresh token")
async def refresh_access_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        payload = validate_refresh_token(refresh_data.refresh_token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # Generate new tokens
        access_token = create_access_token(data={"sub": email})
        refresh_token = create_refresh_token(data={"sub": email})
        
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")