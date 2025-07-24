import pyotp
import aiosmtplib
from email.message import EmailMessage
from fastapi import HTTPException, status
from core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_otp_email(email: str, otp: str) -> None:
    """Send an OTP email to the specified address."""
    message = EmailMessage()
    message.set_content(f"Your KNUST System OTP for verification is: {otp}\nThis OTP is valid for 10 minutes.")
    message["Subject"] = "KNUST System OTP Verification"
    message["From"] = settings.EMAIL_USER
    message["To"] = email

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_USER,
            password=settings.EMAIL_PASSWORD,
            use_tls=True,
        )
        logger.info(f"OTP email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP email")

def generate_otp() -> str:
    """Generate a 6-digit time-based OTP."""
    return pyotp.TOTP(pyotp.random_base32(), interval=600).now()  # 10-minute validity