"""
Comprehensive pytest tests for Banking REST Service
Tests the complete happy path: signup -> login -> create account -> deposit -> transfer -> statement
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

# Note: TestClient initialization moved to individual test functions due to compatibility issues

@pytest.fixture
def client():
    """Create TestClient instance"""
    return TestClient(app)

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

@pytest.fixture
def auth_headers(setup_database, test_user_data, client):
    """Create authenticated user and return headers"""
    # Signup
    signup_response = client.post("/api/v1/auth/signup", json=test_user_data)
    assert signup_response.status_code == 201
    
    # Login
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_signup_success(self, setup_database, test_user_data, client):
        """Test successful user signup"""
        response = client.post("/api/v1/auth/signup", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_signup_duplicate_email(self, setup_database, test_user_data):
        """Test signup with duplicate email fails"""
        # First signup
        client.post("/api/v1/auth/signup", json=test_user_data)
        
        # Second signup with same email
        response = client.post("/api/v1/auth/signup", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, setup_database, test_user_data):
        """Test successful login"""
        # Signup first
        client.post("/api/v1/auth/signup", json=test_user_data)
        
        # Login
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, setup_database, test_user_data):
        """Test login with invalid credentials fails"""
        # Signup first
        client.post("/api/v1/auth/signup", json=test_user_data)
        
        # Login with wrong password
        login_data = {
            "username": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

class TestAccountManagement:
    """Test account management endpoints"""
    
    def test_create_account_success(self, setup_database, auth_headers):
        """Test successful account creation"""
        # Get user profile to get user ID
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {
            "holder_id": user_id,
            "type": "CHECKING"
        }
        response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "CHECKING"
        assert data["balance"] == 0.0
        assert data["holder_id"] == user_id
    
    def test_list_accounts(self, setup_database, auth_headers):
        """Test listing user accounts"""
        # Get user profile to get user ID
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        # Create two accounts
        checking_data = {"holder_id": user_id, "type": "CHECKING"}
        savings_data = {"holder_id": user_id, "type": "SAVINGS"}
        
        client.post("/api/v1/accounts/", json=checking_data, headers=auth_headers)
        client.post("/api/v1/accounts/", json=savings_data, headers=auth_headers)
        
        # List accounts
        response = client.get("/api/v1/accounts/", headers=auth_headers)
        assert response.status_code == 200
        accounts = response.json()
        assert len(accounts) == 2
        assert any(acc["type"] == "CHECKING" for acc in accounts)
        assert any(acc["type"] == "SAVINGS" for acc in accounts)
    
    def test_get_account_by_id(self, setup_database, auth_headers):
        """Test getting specific account by ID"""
        # Get user profile to get user ID
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        # Create account
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        create_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = create_response.json()["id"]
        
        # Get account by ID
        response = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["type"] == "CHECKING"

class TestTransactions:
    """Test transaction endpoints"""
    
    def test_deposit_success(self, setup_database, auth_headers):
        """Test successful deposit"""
        # Create account
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Make deposit
        deposit_data = {
            "account_id": account_id,
            "type": "DEPOSIT",
            "amount": 100.0,
            "description": "Test deposit"
        }
        response = client.post(f"/api/v1/transactions/{account_id}", json=deposit_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "DEPOSIT"
        assert data["amount"] == 100.0
        
        # Verify account balance updated
        account_response = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
        assert account_response.json()["balance"] == 100.0
    
    def test_withdrawal_success(self, setup_database, auth_headers):
        """Test successful withdrawal"""
        # Create account and deposit money
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Deposit first
        deposit_data = {
            "account_id": account_id,
            "type": "DEPOSIT",
            "amount": 200.0,
            "description": "Initial deposit"
        }
        client.post(f"/api/v1/transactions/{account_id}", json=deposit_data, headers=auth_headers)
        
        # Make withdrawal
        withdrawal_data = {
            "account_id": account_id,
            "type": "WITHDRAWAL",
            "amount": 50.0,
            "description": "Test withdrawal"
        }
        response = client.post(f"/api/v1/transactions/{account_id}", json=withdrawal_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "WITHDRAWAL"
        assert data["amount"] == 50.0
        
        # Verify account balance updated
        account_response = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
        assert account_response.json()["balance"] == 150.0
    
    def test_withdrawal_insufficient_funds(self, setup_database, auth_headers):
        """Test withdrawal with insufficient funds fails"""
        # Create account
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Try to withdraw more than available
        withdrawal_data = {
            "account_id": account_id,
            "type": "WITHDRAWAL",
            "amount": 100.0,
            "description": "Large withdrawal"
        }
        response = client.post(f"/api/v1/transactions/{account_id}", json=withdrawal_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Insufficient funds" in response.json()["detail"]
    
    def test_list_transactions(self, setup_database, auth_headers):
        """Test listing account transactions"""
        # Create account and make transactions
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Make multiple transactions
        transactions = [
            {"account_id": account_id, "type": "DEPOSIT", "amount": 100.0, "description": "Deposit 1"},
            {"account_id": account_id, "type": "DEPOSIT", "amount": 50.0, "description": "Deposit 2"},
            {"account_id": account_id, "type": "WITHDRAWAL", "amount": 25.0, "description": "Withdrawal 1"}
        ]
        
        for txn in transactions:
            client.post(f"/api/v1/transactions/{account_id}", json=txn, headers=auth_headers)
        
        # List transactions
        response = client.get(f"/api/v1/transactions/{account_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["type"] == "WITHDRAWAL"  # Newest first

class TestTransfers:
    """Test money transfer endpoints"""
    
    def test_transfer_success(self, setup_database, auth_headers):
        """Test successful money transfer between accounts"""
        # Create two accounts
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        checking_data = {"holder_id": user_id, "type": "CHECKING"}
        savings_data = {"holder_id": user_id, "type": "SAVINGS"}
        
        checking_response = client.post("/api/v1/accounts/", json=checking_data, headers=auth_headers)
        savings_response = client.post("/api/v1/accounts/", json=savings_data, headers=auth_headers)
        
        checking_id = checking_response.json()["id"]
        savings_id = savings_response.json()["id"]
        
        # Deposit money to checking account
        deposit_data = {
            "account_id": checking_id,
            "type": "DEPOSIT",
            "amount": 500.0,
            "description": "Initial deposit"
        }
        client.post(f"/api/v1/transactions/{checking_id}", json=deposit_data, headers=auth_headers)
        
        # Transfer money from checking to savings
        transfer_data = {
            "from_account_id": checking_id,
            "to_account_id": savings_id,
            "amount": 200.0,
            "description": "Transfer to savings"
        }
        response = client.post("/api/v1/transfers/", json=transfer_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["from_account_id"] == checking_id
        assert data["to_account_id"] == savings_id
        assert data["amount"] == 200.0
        
        # Verify balances updated
        checking_account = client.get(f"/api/v1/accounts/{checking_id}", headers=auth_headers).json()
        savings_account = client.get(f"/api/v1/accounts/{savings_id}", headers=auth_headers).json()
        
        assert checking_account["balance"] == 300.0
        assert savings_account["balance"] == 200.0
    
    def test_transfer_insufficient_funds(self, setup_database, auth_headers):
        """Test transfer with insufficient funds fails"""
        # Create two accounts
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        checking_data = {"holder_id": user_id, "type": "CHECKING"}
        savings_data = {"holder_id": user_id, "type": "SAVINGS"}
        
        checking_response = client.post("/api/v1/accounts/", json=checking_data, headers=auth_headers)
        savings_response = client.post("/api/v1/accounts/", json=savings_data, headers=auth_headers)
        
        checking_id = checking_response.json()["id"]
        savings_id = savings_response.json()["id"]
        
        # Try to transfer without sufficient funds
        transfer_data = {
            "from_account_id": checking_id,
            "to_account_id": savings_id,
            "amount": 100.0,
            "description": "Transfer attempt"
        }
        response = client.post("/api/v1/transfers/", json=transfer_data, headers=auth_headers)
        assert response.status_code == 400
        assert "Insufficient funds" in response.json()["detail"]
    
    def test_self_transfer_prevention(self, setup_database, auth_headers):
        """Test that self-transfer is prevented"""
        # Create account
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Try to transfer to same account
        transfer_data = {
            "from_account_id": account_id,
            "to_account_id": account_id,
            "amount": 100.0,
            "description": "Self transfer"
        }
        response = client.post("/api/v1/transfers/", json=transfer_data, headers=auth_headers)
        assert response.status_code == 400
        assert "same account" in response.json()["detail"]

class TestStatements:
    """Test statement endpoints"""
    
    def test_get_account_statement(self, setup_database, auth_headers):
        """Test getting account statement"""
        # Create account and make transactions
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Make some transactions
        transactions = [
            {"account_id": account_id, "type": "DEPOSIT", "amount": 100.0, "description": "Deposit 1"},
            {"account_id": account_id, "type": "DEPOSIT", "amount": 50.0, "description": "Deposit 2"},
            {"account_id": account_id, "type": "WITHDRAWAL", "amount": 25.0, "description": "Withdrawal 1"}
        ]
        
        for txn in transactions:
            client.post(f"/api/v1/transactions/{account_id}", json=txn, headers=auth_headers)
        
        # Get statement
        response = client.get(f"/api/v1/statements/{account_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["account_id"] == account_id
        assert data["ending_balance"] == 125.0
        assert data["total_deposits"] == 150.0
        assert data["total_withdrawals"] == 25.0
        assert len(data["transactions"]) == 3
    
    def test_get_account_summary(self, setup_database, auth_headers):
        """Test getting account summary"""
        # Create account
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Get summary
        response = client.get(f"/api/v1/statements/{account_id}/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        assert data["account_id"] == account_id
        assert data["account_type"] == "CHECKING"
        assert data["current_balance"] == 0.0
        assert "account_created" in data

class TestCards:
    """Test card management endpoints"""
    
    def test_create_card_success(self, setup_database, auth_headers):
        """Test successful card creation"""
        # Create account
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Create card
        card_data = {
            "account_id": account_id,
            "holder_id": user_id,
            "masked_number": "****-****-****-1234",
            "brand": "VISA",
            "last4": "1234"
        }
        response = client.post("/api/v1/cards/", json=card_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["account_id"] == account_id
        assert data["holder_id"] == user_id
        assert data["active"] == True
        assert "****-****-****-" in data["masked_number"]
    
    def test_list_cards(self, setup_database, auth_headers):
        """Test listing user cards"""
        # Create account and cards
        profile_response = client.get("/api/v1/account-holders/me", headers=auth_headers)
        user_id = profile_response.json()["id"]
        
        account_data = {"holder_id": user_id, "type": "CHECKING"}
        account_response = client.post("/api/v1/accounts/", json=account_data, headers=auth_headers)
        account_id = account_response.json()["id"]
        
        # Create two cards
        card_data = {
            "account_id": account_id,
            "holder_id": user_id,
            "masked_number": "****-****-****-1234",
            "brand": "VISA",
            "last4": "1234"
        }
        client.post("/api/v1/cards/", json=card_data, headers=auth_headers)
        
        card_data["masked_number"] = "****-****-****-5678"
        card_data["last4"] = "5678"
        client.post("/api/v1/cards/", json=card_data, headers=auth_headers)
        
        # List cards
        response = client.get("/api/v1/cards/", headers=auth_headers)
        assert response.status_code == 200
        cards = response.json()
        assert len(cards) == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
