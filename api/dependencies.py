from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_access_token
from models.database import supabase
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    """Dependency to get the current authenticated admin."""
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        response = supabase.table("admin_users").select("*").eq("email", email).eq("is_verified", True).execute()
        if not response.data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found or not verified")
        
        logger.info(f"Authenticated admin: {email}")
        return response.data[0]
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")