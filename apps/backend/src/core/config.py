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

    # SEO / Site
    site_base_url: str = os.getenv("SITE_BASE_URL", "http://localhost:3000")

    # SMTP (Email)
    smtp_host: str = os.getenv("SMTP_HOST", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "no-reply@example.com")

    # SMS Provider
    sms_api_base_url: str = os.getenv("SMS_API_BASE_URL", "")
    sms_api_key: str = os.getenv("SMS_API_KEY", "")

    # Rate limit
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    rate_limit_max_requests: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))

    class Config:
        env_file = ".env"

settings = Settings()
