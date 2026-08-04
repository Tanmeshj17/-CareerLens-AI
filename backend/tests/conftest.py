import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load env variables to ensure TEST_DATABASE_URL is picked up
load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

# Explicit safety check: We must have a test database URL configured
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not set. Testing requires a dedicated PostgreSQL database.")

# Ensure we aren't accidentally pointing at production
if "careerlens_test" not in TEST_DATABASE_URL:
    raise RuntimeError(f"Safety violation: TEST_DATABASE_URL ({TEST_DATABASE_URL}) does not appear to be a test database.")

# We do not fallback to SQLite. The test framework requires Postgres.
engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.database import Base
from app.main import app, limiter
from app.database import get_db

# Disable rate limiter for testing
limiter.enabled = False

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Creates the database schema once per test session.
    Drops the schema at the very end of the test session.
    """
    # Drop tables first to ensure a clean slate (in case a previous run crashed)
    Base.metadata.drop_all(bind=engine)
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Drop tables after all tests finish
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Provides a transactional scope around each test.
    Rolls back any changes made during the test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection, join_transaction_mode="create_savepoint")

    # Override the app dependency to use this session
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    yield session

    # Teardown
    session.close()
    transaction.rollback()
    connection.close()
    
    # Crucial: Clean up dependency overrides so they don't leak between tests
    app.dependency_overrides.clear()
