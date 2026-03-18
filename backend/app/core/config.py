from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./network_manager.db"
    
    # API Settings
    API_TITLE: str = "Unified Network Manager API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "API for managing Starlink dishes and MikroTik routers"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    GOOGLE_CLIENT_ID: str = ""  # Set via GOOGLE_CLIENT_ID env var
    
    # Device Refresh Intervals (seconds)
    STARLINK_REFRESH_INTERVAL: int = 30
    MIKROTIK_REFRESH_INTERVAL: int = 30
    
    # Credentials storage
    CREDENTIALS_DIR: str = "./credentials"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
