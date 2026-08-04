import os
import sys
import logging

logger = logging.getLogger(__name__)

def validate_environment():
    """
    Validates required environment variables for production launch.
    Fails fast with explicit warnings/errors if configuration is invalid.
    """
    env = os.environ.get("ENVIRONMENT", "development").lower()
    errors = []
    warnings = []

    # Database URL
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        if env == "production":
            errors.append("DATABASE_URL environment variable is missing!")
        else:
            warnings.append("DATABASE_URL not set; using default local sqlite/postgresfallback.")

    # Secret Key
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key or secret_key == "supersecretkey123":
        if env == "production":
            errors.append("SECRET_KEY is insecure or unset for production!")
        else:
            warnings.append("SECRET_KEY is using default development fallback.")

    # Frontend URL (for CORS)
    frontend_url = os.environ.get("FRONTEND_URL")
    if env == "production" and not frontend_url:
        warnings.append("FRONTEND_URL is not explicitly set; defaulting to wildcard/fallback.")

    # Resend API Key
    resend_key = os.environ.get("RESEND_API_KEY")
    if env == "production" and not resend_key:
        warnings.append("RESEND_API_KEY is not set. Transactional email sending will operate in mock mode.")

    for w in warnings:
        logger.warning(f"[CONFIG WARNING] {w}")

    if errors:
        for e in errors:
            logger.error(f"[CONFIG CRITICAL ERROR] {e}")
        if env == "production":
            sys.exit(1)
