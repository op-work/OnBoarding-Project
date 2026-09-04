"""
Application Configuration
Defines base paths, database location, asset upload paths, and application metadata constants.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Ensure runtime directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

APP_TITLE = "Onboarding Operations"
APP_SUBTITLE = "Streamlined onboarding operations and candidate readiness tracking."

# Azure PostgreSQL Database Configuration
DB_HOST = os.getenv("DB_HOST", "yourserver.postgres.database.azure.com")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "employee360")
DB_USER = os.getenv("DB_USER", "app_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_db_password")
DB_SSL_MODE = os.getenv("DB_SSL_MODE", "require")

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("AZURE_POSTGRESQL_CONNECTIONSTRING")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    DB_URI = DATABASE_URL
else:
    encoded_password = quote_plus(DB_PASSWORD)
    DB_URI = f"postgresql+psycopg2://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode={DB_SSL_MODE}"


# Security & Authentication Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "hr_onboarding_super_secret_jwt_key_2026")
JWT_ALGORITHM = "HS256"



