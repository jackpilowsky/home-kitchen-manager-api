import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from api.v1.models import Base
from api.v1.database import get_db
from auth import create_user, create_access_token

# Test database URL (SQLite in memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create a test client"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Create a database session for testing"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = create_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123",
        first_name="Test",
        last_name="User",
        db=db_session
    )
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user"""
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_kitchen(test_user, db_session):
    """Create a test kitchen"""
    from api.v1.models import Kitchen
    kitchen = Kitchen(
        name="Test Kitchen",
        description="A test kitchen",
        owner_id=test_user.id
    )
    db_session.add(kitchen)
    db_session.commit()
    db_session.refresh(kitchen)
    return kitchen

@pytest.fixture
def test_shopping_list(test_kitchen, db_session):
    """Create a test shopping list"""
    from api.v1.models import ShoppingList
    shopping_list = ShoppingList(
        name="Test Shopping List",
        description="A test shopping list",
        kitchen_id=test_kitchen.id
    )
    db_session.add(shopping_list)
    db_session.commit()
    db_session.refresh(shopping_list)
    return shopping_list