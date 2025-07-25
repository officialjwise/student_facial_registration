import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException, status
from pydantic import EmailStr
from email.message import EmailMessage
import pyotp
import aiosmtplib

from core.config import settings
from core.security import get_password_hash
from core.supabase import supabase
from schemas.auth import AdminCreate

# Configure logging
logger = logging.getLogger(__name__)

# Thread pool for CPU-intensive operations
auth_executor = ThreadPoolExecutor(max_workers=2)

async def get_admin_user_by_email(email: EmailStr):
    """Get admin user by email with async database operation."""
    logger.debug(f"Checking if admin user exists with email: {email}")
    try:
        # Use asyncio to run the database query in a thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            auth_executor,
            lambda: supabase.table("admin_users").select("*").eq("email", email).execute()
        )
        
        logger.debug(f"Supabase response for get_admin_user_by_email: found {len(response.data)} records")
        return response.data[0] if response.data else None
        
    except Exception as e:
        logger.error(f"Error querying admin user by email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )

async def create_admin_user(admin: AdminCreate):
    """Create admin user with async database operation."""
    logger.debug(f"Creating admin user with email: {admin.email}")
    
    try:
        # Hash password in thread pool (CPU-intensive)
        loop = asyncio.get_event_loop()
        hashed_password = await loop.run_in_executor(
            auth_executor,
            get_password_hash,
            admin.password
        )
        
        # Insert user into database
        response = await loop.run_in_executor(
            auth_executor,
            lambda: supabase.table("admin_users").insert({
                "email": admin.email,
                "hashed_password": hashed_password,
                "is_verified": False,
                "created_at": "now()"
            }).execute()
        )
        
        logger.debug(f"Admin user created successfully: {admin.email}")
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin user"
        )

def generate_otp() -> str:
    """Generate OTP secret."""
    logger.debug("Generating OTP secret")
    try:
        otp_secret = pyotp.random_base32()
        logger.debug("OTP secret generated successfully")
        return otp_secret
    except Exception as e:
        logger.error(f"Error generating OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OTP"
        )

async def send_otp_email(email: EmailStr, otp_secret: str) -> str:
    """Send OTP email with improved error handling and timeout."""
    logger.debug(f"Preparing to send OTP email to: {email}")
    
    try:
        # Generate TOTP code
        totp = pyotp.TOTP(otp_secret)
        otp_code = totp.now()
        logger.debug(f"Generated TOTP code for email sending")
        
        # Create email message
        message = EmailMessage()
        message.set_content(
            f"""
            Dear Admin,
            
            Your OTP for KNUST Student Registration System is: {otp_code}
            
            This code will expire in 5 minutes.
            
            Best regards,
            KNUST Registration Team
            """
        )
        message["Subject"] = "KNUST Registration OTP Verification"
        message["From"] = settings.EMAIL_USER
        message["To"] = email
        
        # Send email with timeout
        logger.debug(f"Connecting to SMTP server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        
        try:
            # Use asyncio.wait_for to add timeout to email sending
            await asyncio.wait_for(
                _send_email_async(message),
                timeout=30.0  # 30 second timeout for email sending
            )
            
            logger.info(f"OTP email sent successfully to: {email}")
            return otp_code
            
        except asyncio.TimeoutError:
            logger.error(f"Email sending timeout for: {email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email service timeout - please try again"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send OTP email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email service temporarily unavailable"
        )

async def _send_email_async(message: EmailMessage):
    """Helper function to send email asynchronously."""
    smtp_kwargs = {
        "hostname": settings.EMAIL_HOST,
        "port": settings.EMAIL_PORT,
        "use_tls": True,  # Use TLS from the start
        "timeout": 30
    }
    
    async with aiosmtplib.SMTP(**smtp_kwargs) as server:
        # Don't call starttls() since use_tls=True already enables it
        await server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        await server.send_message(message)

async def store_otp_for_admin(email: EmailStr, otp_secret: str) -> bool:
    """Store OTP secret for admin user."""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            auth_executor,
            lambda: supabase.table("admin_users").update({
                "otp": otp_secret
            }).eq("email", email).execute()
        )
        
        if response.data:
            logger.debug(f"OTP stored successfully for email: {email}")
            return True
        else:
            logger.error(f"Failed to store OTP for email: {email}")
            return False
            
    except Exception as e:
        logger.error(f"Error storing OTP: {str(e)}")
        return False

async def register_admin(admin: AdminCreate) -> dict:
    """Register admin with sequential async operations."""
    logger.debug(f"Starting admin registration for email: {admin.email}")
    
    try:
        # Check for existing admin
        logger.debug("Checking for existing admin")
        existing_admin = await get_admin_user_by_email(admin.email)
        if existing_admin:
            logger.warning(f"Email already registered: {admin.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create admin user
        logger.debug("Creating admin user")
        admin_user = await create_admin_user(admin)
        
        # Generate OTP
        logger.debug("Generating OTP")
        loop = asyncio.get_event_loop()
        otp_secret = await loop.run_in_executor(auth_executor, generate_otp)
        
        # Store OTP
        logger.debug("Storing OTP")
        otp_stored = await store_otp_for_admin(admin.email, otp_secret)
        
        # Send OTP email
        logger.debug("Sending OTP email")
        otp_code = await send_otp_email(admin.email, otp_secret)
        
        if not otp_stored:
            logger.error("Failed to store OTP, but email was sent")
            # Continue anyway as email was sent successfully
        
        logger.info(f"Admin registration completed successfully for: {admin.email}")
        return {
            "message": "Admin registered successfully. OTP sent to email.",
            "email": admin.email,
            "status": "pending_verification",
            "otp_sent": True
        }
        
    except HTTPException as he:
        logger.error(f"HTTP exception during registration: {str(he.detail)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration service temporarily unavailable"
        )

async def verify_admin_otp(email: EmailStr, provided_otp: str) -> bool:
    """Verify admin OTP code."""
    logger.debug(f"Verifying OTP for email: {email}")
    
    try:
        # Get admin user with OTP
        admin_user = await get_admin_user_by_email(email)
        if not admin_user or not admin_user.get("otp"):
            logger.warning(f"No OTP found for email: {email}")
            return False
        
        # Verify TOTP code
        totp = pyotp.TOTP(admin_user["otp"])
        is_valid = totp.verify(provided_otp, valid_window=1)  # Allow 1 window (30s) tolerance
        
        if is_valid:
            # Mark admin as verified and clear OTP
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                auth_executor,
                lambda: supabase.table("admin_users").update({
                    "is_verified": True,
                    "otp": None,
                    "verified_at": "now()"
                }).eq("email", email).execute()
            )
            
            logger.info(f"Admin verified successfully: {email}")
            return True
        else:
            logger.warning(f"Invalid OTP provided for email: {email}")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        return False

# Cleanup function for graceful shutdown
def cleanup_auth_service():
    """Cleanup auth service resources."""
    try:
        auth_executor.shutdown(wait=True)
        logger.info("Auth service executor shut down successfully")
    except Exception as e:
        logger.error(f"Error during auth service cleanup: {str(e)}")