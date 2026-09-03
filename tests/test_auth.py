"""
Unit tests for AuthService and User model.
Verifies JWT password encoding, registration validation, duplicate email prevention, and authentication.
"""

import pytest
from database import init_db, get_db
from models import User
from services.auth_service import AuthService


@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = get_db()
    yield db
    db.close()


def test_jwt_password_hashing(db_session):
    email = "test.jwt@company.com"
    raw_password = "SecretPassword123"

    token = AuthService.hash_password_to_jwt(raw_password, email)
    assert token is not None
    assert isinstance(token, str)
    assert token.startswith("ey")  # Standard JWT header start

    # Raw password should NOT be in token plain text
    assert raw_password not in token

    # Verification should succeed with correct password
    assert AuthService.verify_jwt_password(token, raw_password, email) is True
    # Verification should fail with wrong password
    assert AuthService.verify_jwt_password(token, "WrongPassword", email) is False


def test_user_registration_and_jwt_storage(db_session):
    email = "new.user@company.com"
    password = "MySecurePassword"

    # Clean up pre-existing user from prior test runs
    existing = db_session.query(User).filter(User.email == email).first()
    if existing:
        db_session.delete(existing)
        db_session.commit()

    # Register user

    success, msg, user = AuthService.register_user(
        db=db_session,
        full_name="Test User",
        email=email,
        password=password,
        role="HR Manager"
    )

    assert success is True
    assert user is not None
    assert user.email == email
    assert user.role == "HR Manager"

    # Verify password token in DB is a JWT string
    db_user = db_session.query(User).filter(User.email == email).first()
    assert db_user is not None
    assert db_user.password_token.startswith("ey")
    assert password not in db_user.password_token

    # Verify authentication works
    auth_success, auth_msg, auth_user = AuthService.authenticate_user(db_session, email, password)
    assert auth_success is True
    assert auth_user.id == db_user.id

    # Verify duplicate email registration fails
    dup_success, dup_msg, dup_user = AuthService.register_user(
        db=db_session,
        full_name="Duplicate User",
        email=email,
        password="SomePassword",
        role="HR Admin"
    )
    assert dup_success is False
    assert "already exists" in dup_msg.lower()
