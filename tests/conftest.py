# tests/conftest.py

import os
import sys
import logging
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import app components
try:
    from sqlalchemy_utils import database_exists, create_database
except ImportError:
    logger.error("Please install sqlalchemy-utils: pip install sqlalchemy-utils")
    raise

from app.models import Base, UserModel, TrackModel
from app.database import get_db
from main import app

# Database config
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def list_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tables in database: {tables}")
    return tables

@pytest.fixture(scope="function")
def test_db():
    """Set up and tear down test DB per test function."""
    if not database_exists(engine.url):
        create_database(engine.url)

    logger.info("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    list_tables()

    db = TestingSessionLocal()

    try:
        # Seed test user
        test_user = UserModel(
            username="test_user",
            email="test@example.com",
            is_active=True
        )
        test_user.hashed_password = get_password_hash("test_password")
        db.add(test_user)
        db.flush()

        # Seed tracks
        tracks = [
            TrackModel(title="Rock Song 1", artist="Rock Artist", album="Rock Album"),
            TrackModel(title="Rock Song 2", artist="Rock Artist", album="Rock Album"),
            TrackModel(title="Pop Song 1", artist="Pop Artist", album="Pop Album"),
            TrackModel(title="Jazz Song 1", artist="Jazz Artist", album="Jazz Album")
        ]
        db.add_all(tracks)
        db.commit()
        db.refresh(test_user)

        yield db

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Test client with DB override."""
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers(client):
    """Returns auth headers for test user."""
    response = client.post("/token", data={
        "username": "test_user",
        "password": "test_password"
    })

    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
