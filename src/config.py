"""
Application configuration management.
Loads settings from environment variables with sensible defaults.
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "Funny How - Studio Booking API"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql://postgres:postgres@db:5432/book_studio"
    database_echo: bool = False

    # Security
    secret_key: str = "change-this-to-a-secure-random-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # OAuth - Google
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # Stripe
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_client_id: str = ""

    # Square
    square_application_id: str = ""
    square_access_token: str = ""
    square_environment: str = "sandbox"  # sandbox or production
    square_client_id: str = ""
    square_client_secret: str = ""

    # AWS S3
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    aws_bucket_name: str = ""

    # Email
    mail_from_address: str = "mail@funny-how.com"
    mail_from_name: str = "Funny How"
    smtp_host: str = "smtp.mailtrap.io"
    smtp_port: int = 2525
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_tls: bool = True

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"

    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_extensions: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Booking
    temporary_payment_link_expiry_minutes: int = 30
    service_fee_percentage: float = 4.0

    # Google APIs
    google_places_api_key: str = ""
    google_maps_api_key: str = ""

    # Sentry (optional)
    sentry_dsn: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Convenience instance for importing
settings = get_settings()
