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
        env_file="../.env",
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
    password_encryption_key: str = ""  # Fernet key for encrypting device passwords

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

    # Google Cloud Storage
    gcs_bucket_name: str = ""
    gcs_project_id: str = ""
    gcs_credentials_path: Optional[str] = None  # Path to service account JSON

    # Email - SendGrid Only
    mail_from_address: str = "mail@funny-how.com"
    mail_from_name: str = "Funny How"
    sendgrid_api_key: str = ""

    # Twilio - SMS Authentication
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Frontend URLs for emails
    frontend_url: str = "http://127.0.0.1"  # Will be overridden by .env
    frontend_url_for_qr: str = "http://192.168.1.227"  # For QR codes - use local IP for testing
    unsubscribe_url: str = "https://funny-how.com/unsubscribe"
    email_assets_base_url: str = "https://funny-how.com/mail"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Celery (using Redis as broker and backend)
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

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
    google_maps_api: str = ""  # Alternative key name for compatibility

    # Sentry (optional)
    sentry_dsn: Optional[str] = None

    # Admin Panel
    admin_username: str = "admin"
    admin_password: str = "change-this-admin-password-in-production"
    admin_secret_key: str = "change-this-admin-secret-key-min-32-chars-long"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Convenience instance for importing
settings = get_settings()
