"""
Authentication Service
Handles JWT password token generation, token verification, user registration, authentication, and seed initialization.
"""

import datetime
import hashlib
import jwt
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from config import JWT_SECRET, JWT_ALGORITHM
from models import User
from utils.logger import app_logger
from utils.validation import validate_email



class AuthService:
    @staticmethod
    def hash_password_to_jwt(password: str, email: str) -> str:
        """
        Encodes the password into a signed JWT token string.
        The token hides raw password in DB while remaining cryptographically verifiable.
        """
        # Create a SHA256 digest of the password combined with email salt
        pwd_hash = hashlib.sha256(f"{email.lower().strip()}:{password}".encode("utf-8")).hexdigest()
        
        payload = {
            "sub": email.lower().strip(),
            "pwd_digest": pwd_hash,
            "iat": datetime.datetime.utcnow(),
            "type": "password_token"
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def verify_jwt_password(token: str, input_password: str, email: str) -> bool:
        """
        Decodes the stored JWT password token and verifies if the input password matches.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            expected_hash = hashlib.sha256(f"{email.lower().strip()}:{input_password}".encode("utf-8")).hexdigest()
            return payload.get("pwd_digest") == expected_hash
        except jwt.PyJWTError as e:
            app_logger.error(f"AUTH: Invalid JWT token verification error: {e}")
            return False

    @classmethod
    def register_user(
        cls, db: Session, full_name: str, email: str, password: str, role: str = "HR Admin"
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Registers a new user in the database with password stored in JWT token form.
        """
        full_name = full_name.strip()
        email = email.lower().strip()

        if not full_name:
            return False, "Full Name is required.", None

        if not email or not validate_email(email):
            return False, "Please enter a valid email address.", None


        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters long.", None

        # Check for existing user
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return False, f"A user with email '{email}' already exists.", None

        # Generate JWT token stored in password_token column
        password_jwt = cls.hash_password_to_jwt(password, email)

        new_user = User(
            full_name=full_name,
            email=email,
            password_token=password_jwt,
            role=role,
            created_at=datetime.datetime.utcnow()
        )

        try:
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            app_logger.info(f"AUTH: Registered new user '{email}' (Role: {role}) with JWT tokenized password.")
            return True, "User registered successfully!", new_user
        except Exception as e:
            db.rollback()
            app_logger.error(f"AUTH: Failed to register user {email}: {e}")
            return False, f"Database error while creating user: {str(e)}", None

    @classmethod
    def authenticate_user(cls, db: Session, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticates user by email and password using the stored JWT password token.
        """
        email = email.lower().strip()
        if not email or not password:
            return False, "Please provide both email and password.", None

        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False, "Invalid email or password.", None

        # Verify password using JWT token
        if cls.verify_jwt_password(user.password_token, password, email):
            app_logger.info(f"AUTH: Successful login for user '{email}'")
            return True, "Authentication successful!", user
        else:
            app_logger.warning(f"AUTH: Failed login attempt for user '{email}' (Invalid password)")
            return False, "Invalid email or password.", None

    @classmethod
    def seed_default_user(cls, db: Session):
        """
        Seeds default HR Admin account if user table is empty.
        Default credentials: admin@company.com / admin123
        """
        user_count = db.query(User).count()
        if user_count == 0:
            app_logger.info("AUTH: Seeding default HR Admin user (admin@company.com)")
            cls.register_user(
                db=db,
                full_name="HR Administrator",
                email="admin@company.com",
                password="admin123",
                role="HR Admin"
            )
