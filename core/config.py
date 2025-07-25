import os
from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Database Configuration
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Legacy support for old variable names
    SUPABASE_KEY: Optional[str] = None  # Old name for SERVICE_ROLE_KEY
    
    # Security Configuration
    SECRET_KEY: Optional[str] = None
    JWT_SECRET: Optional[str] = None  # Old name for SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Configuration
    EMAIL_HOST: str
    EMAIL_PORT: int = 587
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    
    # Face Recognition Configuration
    FACE_RECOGNITION_THRESHOLD: float = 0.6
    MAX_FACE_DISTANCE: float = 0.6
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "KNUST Student Registration System"
    
    # Performance Configuration
    MAX_WORKERS: int = 4
    REQUEST_TIMEOUT: int = 300  # 5 minutes for face processing
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._migrate_legacy_variables()
        self._validate_required_settings()
        
    def _migrate_legacy_variables(self):
        """Handle backward compatibility for old variable names."""
        # Migrate SUPABASE_KEY to SUPABASE_SERVICE_ROLE_KEY
        if not self.SUPABASE_SERVICE_ROLE_KEY and self.SUPABASE_KEY:
            self.SUPABASE_SERVICE_ROLE_KEY = self.SUPABASE_KEY
            logger.warning("Using legacy SUPABASE_KEY. Please rename to SUPABASE_SERVICE_ROLE_KEY in your .env file")
        
        # Migrate JWT_SECRET to SECRET_KEY
        if not self.SECRET_KEY and self.JWT_SECRET:
            self.SECRET_KEY = self.JWT_SECRET
            logger.warning("Using legacy JWT_SECRET. Please rename to SECRET_KEY in your .env file")
        
        # Set default SUPABASE_ANON_KEY if not provided
        if not self.SUPABASE_ANON_KEY:
            logger.warning("SUPABASE_ANON_KEY not set. Some features may not work correctly.")
            self.SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
        
    def _validate_required_settings(self):
        """Validate that all required settings are present and secure."""
        required_settings = [
            ('SUPABASE_URL', self.SUPABASE_URL),
            ('SUPABASE_SERVICE_ROLE_KEY', self.SUPABASE_SERVICE_ROLE_KEY),
            ('SECRET_KEY', self.SECRET_KEY),
            ('EMAIL_HOST', self.EMAIL_HOST),
            ('EMAIL_USER', self.EMAIL_USER),
            ('EMAIL_PASSWORD', self.EMAIL_PASSWORD)
        ]
        
        missing_settings = []
        for setting_name, setting_value in required_settings:
            if not setting_value:
                missing_settings.append(setting_name)
                
        if missing_settings:
            error_msg = f"Missing required environment variables: {', '.join(missing_settings)}"
            logger.error(error_msg)
            
            # Provide helpful guidance
            if 'SUPABASE_SERVICE_ROLE_KEY' in missing_settings:
                logger.error("Hint: If you have SUPABASE_KEY in your .env, rename it to SUPABASE_SERVICE_ROLE_KEY")
            if 'SECRET_KEY' in missing_settings:
                logger.error("Hint: If you have JWT_SECRET in your .env, rename it to SECRET_KEY")
            if 'SUPABASE_ANON_KEY' in missing_settings:
                logger.error("Hint: Get your anon key from Supabase Dashboard > Settings > API")
                
            raise ValueError(error_msg)
            
        # Validate key lengths for security
        if self.SECRET_KEY and len(self.SECRET_KEY) < 32:
            logger.warning("SECRET_KEY should be at least 32 characters long for security")
            
        # Validate Supabase URL format
        if not self.SUPABASE_URL.startswith('https://'):
            raise ValueError("SUPABASE_URL must start with https://")
            
        # Validate email port
        if self.EMAIL_PORT not in [587, 465]:
            raise ValueError("EMAIL_PORT must be either 587 (STARTTLS) or 465 (SSL/TLS)")
            
        logger.info("Configuration validated successfully")

# Create settings instance with error handling
try:
    settings = Settings()
    logger.info("Settings loaded successfully")
    
    # Log migration warnings
    if hasattr(settings, 'SUPABASE_KEY') and settings.SUPABASE_KEY:
        logger.warning("🔄 Migration needed: Update SUPABASE_KEY to SUPABASE_SERVICE_ROLE_KEY in .env")
    if hasattr(settings, 'JWT_SECRET') and settings.JWT_SECRET:
        logger.warning("🔄 Migration needed: Update JWT_SECRET to SECRET_KEY in .env")
        
except Exception as e:
    logger.error(f"❌ Failed to load settings: {str(e)}")
    logger.error("💡 Check your .env file and ensure all required variables are set")
    raise