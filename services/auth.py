import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException, status
from pydantic import EmailStr
import pyotp
from datetime import datetime, timedelta

from core.config import settings
from core.security import get_password_hash
from core.supabase import supabase
from core.email import send_otp_email  # Use the core email service
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

def generate_otp_secret() -> str:
    """Generate OTP secret."""
    logger.debug("Generating OTP secret")
    try:
        # Generate a proper secret for TOTP
        otp_secret = pyotp.random_base32()
        logger.debug("OTP secret generated successfully")
        return otp_secret
    except Exception as e:
        logger.error(f"Error generating OTP: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate OTP"
        )

async def store_otp_data_for_admin(email: EmailStr, otp_secret: str, otp_code: str) -> bool:
    """Store the OTP secret and code with expiration for the admin user."""
    try:
        # Calculate expiration time (5 minutes from now)
        expiration_time = datetime.utcnow() + timedelta(minutes=5)
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            auth_executor,
            lambda: supabase.table("admin_users").update({
                "otp_secret": otp_secret,
                "otp_code": otp_code,
                "otp_expires_at": expiration_time.isoformat()
            }).eq("email", email).execute()
        )
        
        if response.data:
            logger.debug(f"OTP data stored successfully for email: {email}")
            return True
        else:
            logger.error(f"Failed to store OTP data for email: {email} - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"Error storing OTP data: {str(e)}")
        return False

async def cleanup_admin_user(email: EmailStr):
    """Helper function to cleanup admin user."""
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            auth_executor,
            lambda: supabase.table("admin_users").delete().eq("email", email).execute()
        )
        logger.debug(f"Cleaned up admin user: {email}")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

async def register_admin(admin: AdminCreate) -> dict:
    """Register admin, generate OTP, store it, and then send it."""
    logger.debug(f"Starting admin registration for email: {admin.email}")
    
    try:
        # 1. Check for existing admin
        existing_admin = await get_admin_user_by_email(admin.email)
        if existing_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        # 2. Create admin user
        await create_admin_user(admin)
        
        # 3. Generate OTP secret and code
        otp_secret = generate_otp_secret()
        totp = pyotp.TOTP(otp_secret)
        otp_code = totp.now()
        
        # 4. Store the OTP secret and code
        otp_stored = await store_otp_data_for_admin(admin.email, otp_secret, otp_code)
        if not otp_stored:
            # If storing fails, cleanup the created user
            await cleanup_admin_user(admin.email)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to store OTP")
            
        # 5. Send the OTP email using core email service
        await send_otp_email(admin.email, otp_code)
        
        return {
            "message": "Admin registered successfully. OTP sent to email.",
            "email": admin.email,
            "status": "pending_verification"
        }
        
    except HTTPException as he:
        logger.error(f"HTTP exception during registration: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        # Attempt to cleanup user if something unexpected happened
        try:
            await cleanup_admin_user(admin.email)
        except:
            pass  # Ignore cleanup errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration service unavailable")

async def verify_admin_otp(email: EmailStr, provided_otp: str) -> bool:
    """Verify admin OTP code."""
    logger.debug(f"Verifying OTP for email: {email}")
    
    try:
        # Get admin user with OTP data
        admin_user = await get_admin_user_by_email(email)
        if not admin_user or not admin_user.get("otp_secret") or not admin_user.get("otp_code"):
            logger.warning(f"No OTP data found for email: {email}")
            return False
        
        # Check if OTP has expired
        if admin_user.get("otp_expires_at"):
            expiration_time = datetime.fromisoformat(admin_user["otp_expires_at"].replace('Z', '+00:00'))
            if datetime.utcnow() > expiration_time.replace(tzinfo=None):
                logger.warning(f"OTP expired for email: {email}")
                return False
        
        # Verify TOTP code using the stored secret
        totp = pyotp.TOTP(admin_user["otp_secret"])
        is_valid = totp.verify(provided_otp, valid_window=1)  # Allow 1 window (30s) tolerance
        
        # Also check against the stored code as backup
        if not is_valid:
            is_valid = (provided_otp == admin_user["otp_code"])
        
        if is_valid:
            # Mark admin as verified and clear OTP data
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                auth_executor,
                lambda: supabase.table("admin_users").update({
                    "is_verified": True,
                    "otp_secret": None,
                    "otp_code": None,
                    "otp_expires_at": None,
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

async def generate_login_otp(email: EmailStr, password: str) -> dict:
    """Generate OTP for admin login after password verification."""
    logger.debug(f"Generating login OTP for email: {email}")
    
    try:
        # Get admin user
        admin_user = await get_admin_user_by_email(email)
        if not admin_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Check if admin is verified
        if not admin_user.get("is_verified"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not verified")
        
        # Verify password
        from core.security import verify_password
        if not verify_password(password, admin_user["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Generate OTP
        otp_secret = generate_otp_secret()
        totp = pyotp.TOTP(otp_secret)
        otp_code = totp.now()
        
        # Store OTP data for login
        otp_stored = await store_otp_data_for_admin(email, otp_secret, otp_code)
        if not otp_stored:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate login OTP")
        
        # Send OTP email
        await send_otp_email(email, otp_code)
        
        return {
            "message": "Login OTP sent to email",
            "email": email,
            "status": "otp_required"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating login OTP: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate login OTP")

async def verify_login_otp(email: EmailStr, provided_otp: str) -> dict:
    """Verify login OTP and return tokens."""
    logger.debug(f"Verifying login OTP for email: {email}")
    
    try:
        # Verify OTP
        is_valid = await verify_admin_otp(email, provided_otp)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP")
        
        # Generate tokens
        from core.security import create_access_token, create_refresh_token
        
        access_token = create_access_token(data={"sub": email})
        refresh_token = create_refresh_token(data={"sub": email})
        
        logger.info(f"Admin logged in successfully: {email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying login OTP: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login verification failed")

# Cleanup function for graceful shutdown
def cleanup_auth_service():
    """Cleanup auth service resources."""
    try:
        auth_executor.shutdown(wait=True)
        logger.info("Auth service executor shut down successfully")
    except Exception as e:
        logger.error(f"Error during auth service cleanup: {str(e)}")