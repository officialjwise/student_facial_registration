import logging
from supabase import create_client, Client
from core.config import settings

logger = logging.getLogger(__name__)

def create_supabase_client() -> Client:
    """Create a secure Supabase client with proper error handling."""
    try:
        # Validate configuration
        if not settings.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY is required")
        
        # Create client with service role key for admin operations
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY  # Updated to use correct variable name
        )
        
        logger.info("Supabase client created successfully")
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}")
        logger.error("Please check your .env file and ensure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set correctly")
        raise

# Create the global supabase client
try:
    supabase: Client = create_supabase_client()
    logger.info("Database connection established successfully")
except Exception as e:
    logger.error(f"Critical error: Could not initialize Supabase client: {str(e)}")
    # Re-raise to prevent application from starting with broken database connection
    raise