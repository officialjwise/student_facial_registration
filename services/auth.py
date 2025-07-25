import logging
from fastapi import HTTPException, status
from pydantic import EmailStr
from ..core.config import settings
from ..core.security import get_password_hash
from ..core.supabase import supabase
from ..schemas.auth import AdminUserCreate
import pyotp
import aiosmtplib
from email.message import EmailMessage

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_admin_user_by_email(email: EmailStr):
    logger.debug(f"Checking if admin user exists with email: {email}")
    try:
        response = supabase.table("admin_users").select("*").eq("email", email).execute()
        logger.debug(f"Supabase response for get_admin_user_by_email: {response.data}")
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error querying admin user by email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")

async def create_admin_user(admin: AdminUserCreate):
    logger.debug(f"Creating admin user with email: {admin.email}")
    hashed_password = get_password_hash(admin.password)
    try:
        response = supabase.table("admin_users").insert({
            "email": admin.email,
            "hashed_password": hashed_password,
            "is_verified": False
        }).execute()
        logger.debug(f"Supabase response for create_admin_user: {response.data}")
        return response.data[0]
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create admin user")

def generate_otp():
    logger.debug("Generating OTP")
    otp = pyotp.random_base32()
    logger.debug(f"Generated OTP secret: {otp}")
    return otp

async def send_otp_email(email: EmailStr, otp: str):
    logger.debug(f"Preparing to send OTP email to: {email}")
    totp = pyotp.TOTP(otp)
    otp_code = totp.now()
    logger.debug(f"Generated OTP code: {otp_code}")
    
    message = EmailMessage()
    message.set_content(f"Your OTP for registration is: {otp_code}")
    message["Subject"] = "KNUST Registration OTP"
    message["From"] = settings.EMAIL_USER
    message["To"] = email

    try:
        logger.debug(f"Connecting to SMTP server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        async with aiosmtplib.SMTP(hostname=settings.EMAIL_HOST, port=settings.EMAIL_PORT, use_tls=False) as server:
            logger.debug("Starting TLS")
            await server.starttls()
            logger.debug(f"Logging in with user: {settings.EMAIL_USER}")
            await server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            logger.debug("Sending email")
            await server.send_message(message)
            logger.info(f"OTP email sent successfully to: {email}")
        return otp_code
    except Exception as e:
        logger.error(f"Failed to send OTP email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP email")

async def register_admin(admin: AdminUserCreate) -> dict:
    logger.debug(f"Starting admin registration for email: {admin.email}")
    try:
        logger.debug("Checking for existing admin")
        if await get_admin_user_by_email(admin.email):
            logger.warning(f"Email already registered: {admin.email}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        logger.debug("Creating admin user")
        admin_user = await create_admin_user(admin)
        
        logger.debug("Generating and storing OTP")
        otp = generate_otp()
        supabase.table("admin_users").update({"otp": otp}).eq("email", admin.email).execute()
        logger.debug(f"Stored OTP for email: {admin.email}")
        
        logger.debug("Sending OTP email")
        otp_code = await send_otp_email(admin.email, otp)
        logger.info(f"Admin registered successfully, OTP sent to: {admin.email}, OTP code: {otp_code}")
        return {"message": "Admin registered, OTP sent to email"}
    except HTTPException as he:
        logger.error(f"HTTP exception during registration: {str(he.detail)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register admin")