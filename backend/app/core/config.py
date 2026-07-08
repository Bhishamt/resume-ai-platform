from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Resume Analyzer & Job Match Platform"
    API_V1_STR: str = "/api/v1"
    
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY: str = "placeholder_secret_key_change_in_production"
    JWT_SECRET: str = "placeholder_jwt_secret_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
    
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    GROQ_API_KEY: str = ""
    
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    
    APP_ENV: str = "development"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
