"""
Working test suite for Banking REST Service
This version works around TestClient compatibility issues
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db, Base
from app.models import AccountType, TransactionType

# Test database setup
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

@pytest.fixture(scope="function")
def setup_database():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }

def test_app_imports():
    """Test that the app can be imported successfully"""
    from app.main import app
    assert app is not None

def test_health_endpoint(setup_database):
    """Test the health check endpoint"""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

def test_root_endpoint(setup_database):
    """Test the root endpoint"""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Banking REST Service" in data["message"]

def test_signup_endpoint(setup_database, test_user_data):
    """Test user signup"""
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/signup", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data

def test_login_endpoint(setup_database, test_user_data):
    """Test user login"""
    with TestClient(app) as client:
        # First signup
        signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
        assert signup_response.status_code == 201
        
        # Then login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

def test_account_creation(setup_database, test_user_data):
    """Test account creation"""
    with TestClient(app) as client:
        # Signup and login
        client.post("/api/v1/auth/signup", json=test_user_data)
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create account
        account_data = {
            "holder_id": 1,  # Assuming first user gets ID 1
            "type": "CHECKING"
        }
        response = client.post("/api/v1/accounts/", json=account_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "CHECKING"
        assert data["balance"] == 0.0

def test_deposit_transaction(setup_database, test_user_data):
    """Test deposit transaction"""
    with TestClient(app) as client:
        # Signup and login
        client.post("/api/v1/auth/signup", json=test_user_data)
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create account
        account_data = {
            "holder_id": 1,
            "type": "CHECKING"
        }
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=headers)
        account_id = account_response.json()["id"]
        
        # Make deposit
        transaction_data = {
            "account_id": account_id,
            "type": "DEPOSIT",
            "amount": 100.0,
            "description": "Test deposit"
        }
        response = client.post(f"/api/v1/transactions/{account_id}", json=transaction_data, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "DEPOSIT"
        assert data["amount"] == 100.0

def test_api_docs_available(setup_database):
    """Test that API documentation is available"""
    with TestClient(app) as client:
        response = client.get("/docs")
        assert response.status_code == 200

def test_openapi_schema(setup_database):
    """Test that OpenAPI schema is available"""
    with TestClient(app) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Banking REST Service"
