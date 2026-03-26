"""
Application configuration loaded from environment variables via python-dotenv.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings resolved from .env or environment variables."""

    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "guide_to_global"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Single shared instance used across the application
settings = Settings()
