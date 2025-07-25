import pyotp
import aiosmtplib
from email.message import EmailMessage
from fastapi import HTTPException, status
from core.config import settings
import logging
import ssl

logger = logging.getLogger(__name__)

async def send_otp_email(email: str, otp: str) -> None:
    """Send an OTP email to the specified address with Gmail-specific configuration."""
    message = EmailMessage()
    message.set_content(f"Your KNUST System OTP for verification is: {otp}\nThis OTP is valid for 10 minutes.")
    message["Subject"] = "KNUST System OTP Verification"
    message["From"] = settings.EMAIL_USER
    message["To"] = email

    try:
        if settings.EMAIL_HOST.lower() == "smtp.gmail.com":
            # Gmail-specific configuration
            if settings.EMAIL_PORT == 587:
                # Method 1: Using aiosmtplib.send with explicit STARTTLS
                try:
                    await aiosmtplib.send(
                        message,
                        hostname=settings.EMAIL_HOST,
                        port=settings.EMAIL_PORT,
                        start_tls=True,
                        username=settings.EMAIL_USER,
                        password=settings.EMAIL_PASSWORD,
                        timeout=30
                    )
                    logger.info(f"OTP email sent to {email} via Gmail STARTTLS")
                    return
                except Exception as e:
                    logger.warning(f"Method 1 failed: {e}. Trying method 2...")
                    
                # Method 2: Manual connection with custom SSL context
                context = ssl.create_default_context()
                async with aiosmtplib.SMTP(
                    hostname=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    timeout=30,
                    tls_context=context
                ) as smtp:
                    await smtp.starttls(tls_context=context)
                    await smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                    await smtp.send_message(message)
                    logger.info(f"OTP email sent to {email} via Gmail STARTTLS (method 2)")
                    
            elif settings.EMAIL_PORT == 465:
                # SSL/TLS for Gmail
                await aiosmtplib.send(
                    message,
                    hostname=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    use_tls=True,
                    username=settings.EMAIL_USER,
                    password=settings.EMAIL_PASSWORD,
                    timeout=30
                )
                logger.info(f"OTP email sent to {email} via Gmail SSL/TLS")
                
            else:
                raise ValueError(f"Unsupported Gmail port: {settings.EMAIL_PORT}")
                
        else:
            # Generic SMTP configuration for non-Gmail providers
            if settings.EMAIL_PORT == 587:
                async with aiosmtplib.SMTP(
                    hostname=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    timeout=30
                ) as smtp:
                    await smtp.starttls()
                    await smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                    await smtp.send_message(message)
                    logger.info(f"OTP email sent to {email} via generic STARTTLS")
                    
            elif settings.EMAIL_PORT == 465:
                async with aiosmtplib.SMTP(
                    hostname=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    use_tls=True,
                    timeout=30
                ) as smtp:
                    await smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                    await smtp.send_message(message)
                    logger.info(f"OTP email sent to {email} via generic SSL/TLS")
                    
            else:
                raise ValueError("EMAIL_PORT must be 587 (STARTTLS) or 465 (SSL/TLS)")
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        
        # Provide specific error messages for common Gmail issues
        error_msg = "Email service temporarily unavailable"
        if "authentication" in str(e).lower():
            error_msg = "Email authentication failed. Please check your app password."
        elif "connection" in str(e).lower():
            error_msg = "Failed to connect to email server. Please try again."
        elif "tls" in str(e).lower():
            error_msg = "TLS connection error. Please check email configuration."
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=error_msg
        )

def generate_otp() -> str:
    """Generate a 6-digit time-based OTP."""
    return pyotp.TOTP(pyotp.random_base32(), interval=600).now()  # 10-minute validity