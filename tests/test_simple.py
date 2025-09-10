"""
Simple test file to verify the Banking REST Service works
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db, Base

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

def test_app_imports():
    """Test that the app imports successfully"""
    from app.main import app
    assert app is not None

def test_health_endpoint():
    """Test the health check endpoint"""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "Banking REST Service API" in response.json()["message"]

def test_signup_endpoint_exists():
    """Test that signup endpoint exists and returns proper error for missing data"""
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/signup", json={})
        assert response.status_code == 422  # Validation error for missing required fields

def test_login_endpoint_exists():
    """Test that login endpoint exists"""
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", data={})
        assert response.status_code == 422  # Validation error for missing data

def test_api_docs_available():
    """Test that API documentation is available"""
    with TestClient(app) as client:
        response = client.get("/docs")
        assert response.status_code == 200

def test_openapi_schema():
    """Test that OpenAPI schema is available"""
    with TestClient(app) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
