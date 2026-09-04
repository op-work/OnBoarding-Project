"""
Pytest configuration and test setup for Azure PostgreSQL environment.
"""
import pytest
from sqlalchemy.exc import OperationalError
from database import engine, Base, SessionLocal

@pytest.fixture(scope="module")
def db_session():
    """
    Provides a database session connected to Azure PostgreSQL.
    If Azure PostgreSQL is unreachable (e.g. placeholder config or network offline),
    skips the database integration test gracefully.
    """
    try:
        with engine.connect() as conn:
            pass
    except (OperationalError, Exception) as e:
        pytest.skip(f"Azure PostgreSQL database is not reachable ({e}). Configure valid DB credentials in .env.")

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
