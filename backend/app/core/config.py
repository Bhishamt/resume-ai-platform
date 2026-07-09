from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Resume Analyzer & Job Match Platform"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "placeholder_secret_key_change_in_production"
    JWT_SECRET: str = "placeholder_jwt_secret_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    CORS_ORIGINS: List[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    GROQ_API_KEY: str = ""

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    APP_ENV: str = "development"

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
    }


settings = Settings()
