from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    TOKEN_DURATION_MINUTES: Optional[int] = None
    TOKEN_ALGORITHM: Optional[str] = None
    TOKEN_URL: Optional[str] = None
    TOKEN_TYPE: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()