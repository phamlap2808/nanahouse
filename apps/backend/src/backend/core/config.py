from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    app_name: str = 'nanahouse'
    debug: bool = True
    
    # JWT Settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "file:./dev.db")

    class Config:
        env_file = ".env"

settings = Settings()
