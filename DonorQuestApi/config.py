import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    API_JWT_SECRET: str = "change_me"
    API_REFRESH_SECRET: str = "change_me_refresh"
    API_JWT_EXPIRES_MIN: int = 30
    API_REFRESH_EXPIRES_MIN: int = 43200  # 30 days
    API_DATABASE_URL: str = "postgresql+psycopg://postgres:root@localhost:5432/bloodconnect"
    API_CORS_ORIGINS: str = "*"
    API_FIREBASE_CREDENTIALS: str = ""
    API_VERSION: str = os.getenv("API_VERSION", "v1")

    class Config:
        env_file = ".env"

settings = Settings()
