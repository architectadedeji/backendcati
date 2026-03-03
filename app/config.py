from pydantic_settings import BaseSettings
from typing import List
from pydantic import Field
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    # Database - defaults to SQLite (dev), override with DATABASE_URL env var for MySQL (prod)
    database_url: str = Field(default="sqlite+aiosqlite:///./db.sqlite3")

    # Auth
    secret_key: str = Field(default="streamcati-backend-secret-key-2026-development")
    token_expiry_hours: int = Field(default=24)

    # CORS - will be parsed as comma-separated string from env
    cors_origins: str = Field(default="http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174")

    # App
    environment: str = Field(default="development")
    testing_mode: bool = Field(default=True)
    testing_interval_minutes: int = Field(default=2)
    production_interval_months: int = Field(default=3)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
