import logging
from supabase import create_client, Client
from .config import settings

logger = logging.getLogger(__name__)

def create_supabase_client() -> Client:
    """Create a secure Supabase client with proper error handling."""
    try:
        # Validate configuration
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("Missing required Supabase configuration")
        
        # Create client with service role key for admin operations
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
        )
        
        # Test connection
        try:
            # Simple test query to verify connection
            test_response = client.table("admin_users").select("id").limit(1).execute()
            logger.info("Supabase connection established successfully")
        except Exception as e:
            logger.warning(f"Supabase connection test failed: {str(e)}")
            # Don't fail here, let the application handle it gracefully
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}")
        raise

# Create the global supabase client
try:
    supabase: Client = create_supabase_client()
except Exception as e:
    logger.error(f"Critical error: Could not initialize Supabase client: {str(e)}")
    # Re-raise to prevent application from starting with broken database connection
    raise

def get_supabase_client() -> Client:
    """Get the Supabase client instance."""
    return supabase