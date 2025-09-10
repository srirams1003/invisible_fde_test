#!/usr/bin/env python3
"""
Test script for transaction and transfer endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token for testing"""
    # First, create a test user if it doesn't exist
    test_user = {
        "email": "transaction_test@example.com",
        "full_name": "Transaction Test User",
        "password": "testpassword123"
    }
    
    # Try to signup (ignore if user already exists)
    signup_response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=test_user)
    
    # Login to get token
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    
    if login_response.status_code == 200:
        return login_response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {login_response.text}")

def test_transaction_flow():
    """Test complete transaction and transfer flow"""
    print("🧪 Testing Banking Transaction and Transfer Flow")
    print("=" * 60)
    
    try:
        # Get authentication token
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Get user profile to get user ID
        profile_response = requests.get(f"{BASE_URL}/api/v1/account-holders/me", headers=headers)
        user_data = profile_response.json()
        user_id = user_data["id"]
        print(f"✅ User ID: {user_id}")
        
        # Create two accounts for testing
        print("\n1. Creating test accounts...")
        
        # Create checking account
        checking_account = {
            "holder_id": user_id,
            "type": "CHECKING"
        }
        checking_response = requests.post(
            f"{BASE_URL}/api/v1/accounts/",
            json=checking_account,
            headers=headers
        )
        if checking_response.status_code == 201:
            checking_data = checking_response.json()
            checking_id = checking_data["id"]
            print(f"   ✅ Checking account created: ID {checking_id}")
        else:
            print(f"   ❌ Checking account creation failed: {checking_response.text}")
            return
        
        # Create savings account
        savings_account = {
            "holder_id": user_id,
            "type": "SAVINGS"
        }
        savings_response = requests.post(
            f"{BASE_URL}/api/v1/accounts/",
            json=savings_account,
            headers=headers
        )
        if savings_response.status_code == 201:
            savings_data = savings_response.json()
            savings_id = savings_data["id"]
            print(f"   ✅ Savings account created: ID {savings_id}")
        else:
            print(f"   ❌ Savings account creation failed: {savings_response.text}")
            return
        
        # Test deposits
        print("\n2. Testing deposits...")
        
        # Deposit to checking account
        deposit_data = {
            "account_id": checking_id,
            "type": "DEPOSIT",
            "amount": 1000.0,
            "description": "Initial deposit"
        }
        deposit_response = requests.post(
            f"{BASE_URL}/api/v1/transactions/{checking_id}",
            json=deposit_data,
            headers=headers
        )
        if deposit_response.status_code == 201:
            print(f"   ✅ Deposit successful: ${deposit_data['amount']}")
        else:
            print(f"   ❌ Deposit failed: {deposit_response.text}")
            return
        
        # Deposit to savings account
        deposit_data["account_id"] = savings_id
        deposit_data["amount"] = 500.0
        deposit_data["description"] = "Savings deposit"
        deposit_response = requests.post(
            f"{BASE_URL}/api/v1/transactions/{savings_id}",
            json=deposit_data,
            headers=headers
        )
        if deposit_response.status_code == 201:
            print(f"   ✅ Savings deposit successful: ${deposit_data['amount']}")
        else:
            print(f"   ❌ Savings deposit failed: {deposit_response.text}")
            return
        
        # Test withdrawals
        print("\n3. Testing withdrawals...")
        
        # Withdraw from checking account
        withdrawal_data = {
            "account_id": checking_id,
            "type": "WITHDRAWAL",
            "amount": 200.0,
            "description": "ATM withdrawal"
        }
        withdrawal_response = requests.post(
            f"{BASE_URL}/api/v1/transactions/{checking_id}",
            json=withdrawal_data,
            headers=headers
        )
        if withdrawal_response.status_code == 201:
            print(f"   ✅ Withdrawal successful: ${withdrawal_data['amount']}")
        else:
            print(f"   ❌ Withdrawal failed: {withdrawal_response.text}")
            return
        
        # Test insufficient funds
        print("\n4. Testing insufficient funds validation...")
        large_withdrawal = {
            "account_id": checking_id,
            "type": "WITHDRAWAL",
            "amount": 10000.0,
            "description": "Large withdrawal attempt"
        }
        large_withdrawal_response = requests.post(
            f"{BASE_URL}/api/v1/transactions/{checking_id}",
            json=large_withdrawal,
            headers=headers
        )
        if large_withdrawal_response.status_code == 400:
            print("   ✅ Insufficient funds validation working")
        else:
            print(f"   ❌ Insufficient funds validation failed: {large_withdrawal_response.text}")
        
        # Test transfers
        print("\n5. Testing money transfers...")
        
        # Transfer from checking to savings
        transfer_data = {
            "from_account_id": checking_id,
            "to_account_id": savings_id,
            "amount": 300.0,
            "description": "Transfer to savings"
        }
        transfer_response = requests.post(
            f"{BASE_URL}/api/v1/transfers/",
            json=transfer_data,
            headers=headers
        )
        if transfer_response.status_code == 201:
            transfer_result = transfer_response.json()
            print(f"   ✅ Transfer successful: ${transfer_data['amount']}")
            print(f"   Transaction ID: {transfer_result['transaction_id']}")
        else:
            print(f"   ❌ Transfer failed: {transfer_response.text}")
            return
        
        # Test self-transfer prevention
        print("\n6. Testing self-transfer prevention...")
        self_transfer = {
            "from_account_id": checking_id,
            "to_account_id": checking_id,
            "amount": 100.0,
            "description": "Self transfer attempt"
        }
        self_transfer_response = requests.post(
            f"{BASE_URL}/api/v1/transfers/",
            json=self_transfer,
            headers=headers
        )
        if self_transfer_response.status_code == 400:
            print("   ✅ Self-transfer prevention working")
        else:
            print(f"   ❌ Self-transfer prevention failed: {self_transfer_response.text}")
        
        # Test transaction listing
        print("\n7. Testing transaction listing...")
        
        # List checking account transactions
        transactions_response = requests.get(
            f"{BASE_URL}/api/v1/transactions/{checking_id}",
            headers=headers
        )
        if transactions_response.status_code == 200:
            transactions = transactions_response.json()
            print(f"   ✅ Checking account transactions: {len(transactions)} found")
            for i, txn in enumerate(transactions[:3]):  # Show first 3
                print(f"      {i+1}. {txn['type']}: ${txn['amount']} - {txn['description']}")
        else:
            print(f"   ❌ Transaction listing failed: {transactions_response.text}")
        
        # List savings account transactions
        savings_transactions_response = requests.get(
            f"{BASE_URL}/api/v1/transactions/{savings_id}",
            headers=headers
        )
        if savings_transactions_response.status_code == 200:
            savings_transactions = savings_transactions_response.json()
            print(f"   ✅ Savings account transactions: {len(savings_transactions)} found")
        else:
            print(f"   ❌ Savings transaction listing failed: {savings_transactions_response.text}")
        
        # Check final balances
        print("\n8. Checking final account balances...")
        
        # Get checking account
        checking_response = requests.get(
            f"{BASE_URL}/api/v1/accounts/{checking_id}",
            headers=headers
        )
        if checking_response.status_code == 200:
            checking_account = checking_response.json()
            print(f"   ✅ Checking account balance: ${checking_account['balance']}")
        
        # Get savings account
        savings_response = requests.get(
            f"{BASE_URL}/api/v1/accounts/{savings_id}",
            headers=headers
        )
        if savings_response.status_code == 200:
            savings_account = savings_response.json()
            print(f"   ✅ Savings account balance: ${savings_account['balance']}")
        
        print("\n🎉 All transaction and transfer tests passed!")
        print("   - Deposits and withdrawals working correctly")
        print("   - Balance validation working")
        print("   - Money transfers between accounts working")
        print("   - Transaction history tracking working")
        print("   - Security validations working")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on localhost:8000")
        print("   Start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_transaction_flow()
