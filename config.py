"""
Application Configuration
Defines base paths, database location, asset upload paths, and application metadata constants.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
DB_PATH = DATA_DIR / "onboarding.db"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

APP_TITLE = "Onboarding Operations"
APP_SUBTITLE = "Streamlined onboarding operations and candidate readiness tracking."

# Security & Authentication Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "hr_onboarding_super_secret_jwt_key_2026")
JWT_ALGORITHM = "HS256"

