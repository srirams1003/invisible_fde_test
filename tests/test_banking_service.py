"""
Comprehensive test suite for Banking REST Service
This version works with pytest 8.4.2 and Python 3.13
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db, Base
from app.models import AccountType, TransactionType

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_banking.db"
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
async def setup_database():
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

@pytest.fixture
async def auth_headers(setup_database, test_user_data):
    """Create authenticated user and return headers"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Signup
        signup_response = await client.post("/api/v1/auth/signup", json=test_user_data)
        assert signup_response.status_code == 201
        
        # Login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = await client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

class TestAuthentication:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_signup_success(self, setup_database, test_user_data):
        """Test successful user signup"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/signup", json=test_user_data)
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == test_user_data["email"]
            assert data["full_name"] == test_user_data["full_name"]
            assert "id" in data
            assert "hashed_password" not in data  # Password should not be returned
    
    @pytest.mark.asyncio
    async def test_signup_duplicate_email(self, setup_database, test_user_data):
        """Test signup with duplicate email fails"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First signup
            await client.post("/api/v1/auth/signup", json=test_user_data)
            
            # Second signup with same email
            response = await client.post("/api/v1/auth/signup", json=test_user_data)
            assert response.status_code == 400
            assert "already registered" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_success(self, setup_database, test_user_data):
        """Test successful user login"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First signup
            await client.post("/api/v1/auth/signup", json=test_user_data)
            
            # Then login
            login_data = {
                "username": test_user_data["email"],
                "password": test_user_data["password"]
            }
            response = await client.post("/api/v1/auth/login", data=login_data)
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "expires_in" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, setup_database, test_user_data):
        """Test login with invalid credentials fails"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First signup
            await client.post("/api/v1/auth/signup", json=test_user_data)
            
            # Login with wrong password
            login_data = {
                "username": test_user_data["email"],
                "password": "wrongpassword"
            }
            response = await client.post("/api/v1/auth/login", data=login_data)
            assert response.status_code == 401
            assert "Incorrect email or password" in response.json()["detail"]

class TestAccountManagement:
    """Test account management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_account(self, setup_database, auth_headers):
        """Test account creation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            account_data = {
                "holder_id": 1,  # Assuming first user gets ID 1
                "type": "CHECKING"
            }
            response = await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            assert response.status_code == 201
            data = response.json()
            assert data["type"] == "CHECKING"
            assert data["balance"] == 0.0
            assert "id" in data
            assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_list_accounts(self, setup_database, auth_headers):
        """Test listing user accounts"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create a checking account
            account_data = {"holder_id": 1, "type": "CHECKING"}
            await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            
            # Create a savings account
            account_data = {"holder_id": 1, "type": "SAVINGS"}
            await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            
            # List accounts
            response = await client.get("/api/v1/accounts/", headers=auth_headers)
            assert response.status_code == 200
            accounts = response.json()
            assert len(accounts) == 2
            assert any(acc["type"] == "CHECKING" for acc in accounts)
            assert any(acc["type"] == "SAVINGS" for acc in accounts)
    
    @pytest.mark.asyncio
    async def test_get_account_details(self, setup_database, auth_headers):
        """Test getting account details"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create account
            account_data = {"holder_id": 1, "type": "CHECKING"}
            create_response = await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            account_id = create_response.json()["id"]
            
            # Get account details
            response = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == account_id
            assert data["type"] == "CHECKING"
            assert data["balance"] == 0.0

class TestTransactions:
    """Test transaction endpoints"""
    
    @pytest.mark.asyncio
    async def test_deposit_transaction(self, setup_database, auth_headers):
        """Test deposit transaction"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create account
            account_data = {"holder_id": 1, "type": "CHECKING"}
            account_response = await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            account_id = account_response.json()["id"]
            
            # Make deposit
            transaction_data = {
                "account_id": account_id,
                "type": "DEPOSIT",
                "amount": 100.0,
                "description": "Test deposit"
            }
            response = await client.post(f"/api/v1/transactions/{account_id}", json=transaction_data, headers=auth_headers)
            assert response.status_code == 201
            data = response.json()
            assert data["type"] == "DEPOSIT"
            assert data["amount"] == 100.0
            assert data["description"] == "Test deposit"
            
            # Verify account balance updated
            account_response = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
            assert account_response.json()["balance"] == 100.0
    
    @pytest.mark.asyncio
    async def test_withdrawal_transaction(self, setup_database, auth_headers):
        """Test withdrawal transaction"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create account and deposit money
            account_data = {"holder_id": 1, "type": "CHECKING"}
            account_response = await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            account_id = account_response.json()["id"]
            
            # Deposit first
            deposit_data = {
                "account_id": account_id,
                "type": "DEPOSIT",
                "amount": 200.0,
                "description": "Initial deposit"
            }
            await client.post(f"/api/v1/transactions/{account_id}", json=deposit_data, headers=auth_headers)
            
            # Then withdraw
            withdrawal_data = {
                "account_id": account_id,
                "type": "WITHDRAWAL",
                "amount": 50.0,
                "description": "Test withdrawal"
            }
            response = await client.post(f"/api/v1/transactions/{account_id}", json=withdrawal_data, headers=auth_headers)
            assert response.status_code == 201
            data = response.json()
            assert data["type"] == "WITHDRAWAL"
            assert data["amount"] == 50.0
            
            # Verify account balance updated
            account_response = await client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
            assert account_response.json()["balance"] == 150.0
    
    @pytest.mark.asyncio
    async def test_insufficient_funds(self, setup_database, auth_headers):
        """Test withdrawal with insufficient funds fails"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create account
            account_data = {"holder_id": 1, "type": "CHECKING"}
            account_response = await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            account_id = account_response.json()["id"]
            
            # Try to withdraw more than balance
            withdrawal_data = {
                "account_id": account_id,
                "type": "WITHDRAWAL",
                "amount": 100.0,
                "description": "Test withdrawal"
            }
            response = await client.post(f"/api/v1/transactions/{account_id}", json=withdrawal_data, headers=auth_headers)
            assert response.status_code == 400
            assert "Insufficient funds" in response.json()["detail"]

class TestTransfers:
    """Test money transfer endpoints"""
    
    @pytest.mark.asyncio
    async def test_money_transfer(self, setup_database, auth_headers):
        """Test money transfer between accounts"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create two accounts
            checking_data = {"holder_id": 1, "type": "CHECKING"}
            checking_response = await client.post("/api/v1/accounts/", json=checking_data, headers=auth_headers)
            checking_id = checking_response.json()["id"]
            
            savings_data = {"holder_id": 1, "type": "SAVINGS"}
            savings_response = await client.post("/api/v1/accounts/", json=savings_data, headers=auth_headers)
            savings_id = savings_response.json()["id"]
            
            # Deposit money to checking account
            deposit_data = {
                "account_id": checking_id,
                "type": "DEPOSIT",
                "amount": 500.0,
                "description": "Initial deposit"
            }
            await client.post(f"/api/v1/transactions/{checking_id}", json=deposit_data, headers=auth_headers)
            
            # Transfer money
            transfer_data = {
                "from_account_id": checking_id,
                "to_account_id": savings_id,
                "amount": 200.0,
                "description": "Transfer to savings"
            }
            response = await client.post("/api/v1/transfers/", json=transfer_data, headers=auth_headers)
            assert response.status_code == 201
            data = response.json()
            assert data["from_account_id"] == checking_id
            assert data["to_account_id"] == savings_id
            assert data["amount"] == 200.0
            
            # Verify balances
            checking_response = await client.get(f"/api/v1/accounts/{checking_id}", headers=auth_headers)
            assert checking_response.json()["balance"] == 300.0
            
            savings_response = await client.get(f"/api/v1/accounts/{savings_id}", headers=auth_headers)
            assert savings_response.json()["balance"] == 200.0

class TestCards:
    """Test card management endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_card(self, setup_database, auth_headers):
        """Test card creation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create account
            account_data = {"holder_id": 1, "type": "CHECKING"}
            account_response = await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            account_id = account_response.json()["id"]
            
            # Create card
            card_data = {
                "account_id": account_id,
                "holder_id": 1
            }
            response = await client.post("/api/v1/cards/", json=card_data, headers=auth_headers)
            assert response.status_code == 201
            data = response.json()
            assert data["account_id"] == account_id
            assert data["holder_id"] == 1
            assert data["active"] == True
            assert "masked_number" in data
            assert "brand" in data
            assert "last4" in data

class TestStatements:
    """Test statement endpoints"""
    
    @pytest.mark.asyncio
    async def test_account_statement(self, setup_database, auth_headers):
        """Test account statement generation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create account
            account_data = {"holder_id": 1, "type": "CHECKING"}
            account_response = await client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
            account_id = account_response.json()["id"]
            
            # Make some transactions
            deposit_data = {
                "account_id": account_id,
                "type": "DEPOSIT",
                "amount": 1000.0,
                "description": "Initial deposit"
            }
            await client.post(f"/api/v1/transactions/{account_id}", json=deposit_data, headers=auth_headers)
            
            withdrawal_data = {
                "account_id": account_id,
                "type": "WITHDRAWAL",
                "amount": 200.0,
                "description": "ATM withdrawal"
            }
            await client.post(f"/api/v1/transactions/{account_id}", json=withdrawal_data, headers=auth_headers)
            
            # Get statement
            response = await client.get(f"/api/v1/statements/{account_id}", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["account_id"] == account_id
            assert data["ending_balance"] == 800.0
            assert data["total_deposits"] == 1000.0
            assert data["total_withdrawals"] == 200.0
            assert len(data["transactions"]) == 2

class TestAPIEndpoints:
    """Test basic API endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, setup_database):
        """Test health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, setup_database):
        """Test root endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert "Banking REST Service" in data["message"]
    
    @pytest.mark.asyncio
    async def test_api_docs_available(self, setup_database):
        """Test that API documentation is available"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/docs")
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_openapi_schema(self, setup_database):
        """Test that OpenAPI schema is available"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/openapi.json")
            assert response.status_code == 200
            data = response.json()
            assert data["info"]["title"] == "Banking REST Service"
