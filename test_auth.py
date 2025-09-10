#!/usr/bin/env python3
"""
Quick test script for authentication and account endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test the complete authentication flow"""
    print("🧪 Testing Banking REST Service Authentication Flow")
    print("=" * 50)
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    try:
        # 1. Test signup
        print("1. Testing user signup...")
        signup_response = requests.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json=test_user
        )
        print(f"   Status: {signup_response.status_code}")
        if signup_response.status_code == 201:
            print("   ✅ User created successfully")
            user_data = signup_response.json()
            print(f"   User ID: {user_data['id']}")
        else:
            print(f"   ❌ Signup failed: {signup_response.text}")
            return
        
        # 2. Test login
        print("\n2. Testing user login...")
        login_data = {
            "username": test_user["email"],
            "password": test_user["password"]
        }
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data=login_data
        )
        print(f"   Status: {login_response.status_code}")
        if login_response.status_code == 200:
            print("   ✅ Login successful")
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print(f"   Token: {access_token[:20]}...")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return
        
        # 3. Test protected endpoint - get profile
        print("\n3. Testing protected endpoint (get profile)...")
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = requests.get(
            f"{BASE_URL}/api/v1/account-holders/me",
            headers=headers
        )
        print(f"   Status: {profile_response.status_code}")
        if profile_response.status_code == 200:
            print("   ✅ Profile retrieved successfully")
            profile = profile_response.json()
            print(f"   Name: {profile['full_name']}")
            print(f"   Email: {profile['email']}")
        else:
            print(f"   ❌ Profile retrieval failed: {profile_response.text}")
            return
        
        # 4. Test account creation
        print("\n4. Testing account creation...")
        account_data = {
            "holder_id": user_data["id"],
            "type": "CHECKING"
        }
        account_response = requests.post(
            f"{BASE_URL}/api/v1/accounts/",
            json=account_data,
            headers=headers
        )
        print(f"   Status: {account_response.status_code}")
        if account_response.status_code == 201:
            print("   ✅ Account created successfully")
            account = account_response.json()
            print(f"   Account ID: {account['id']}")
            print(f"   Account Type: {account['type']}")
            print(f"   Balance: ${account['balance']}")
        else:
            print(f"   ❌ Account creation failed: {account_response.text}")
            return
        
        # 5. Test listing accounts
        print("\n5. Testing account listing...")
        accounts_response = requests.get(
            f"{BASE_URL}/api/v1/accounts/",
            headers=headers
        )
        print(f"   Status: {accounts_response.status_code}")
        if accounts_response.status_code == 200:
            print("   ✅ Accounts listed successfully")
            accounts = accounts_response.json()
            print(f"   Number of accounts: {len(accounts)}")
        else:
            print(f"   ❌ Account listing failed: {accounts_response.text}")
            return
        
        # 6. Test getting specific account
        print("\n6. Testing get specific account...")
        account_id = account["id"]
        get_account_response = requests.get(
            f"{BASE_URL}/api/v1/accounts/{account_id}",
            headers=headers
        )
        print(f"   Status: {get_account_response.status_code}")
        if get_account_response.status_code == 200:
            print("   ✅ Account retrieved successfully")
            account_detail = get_account_response.json()
            print(f"   Account ID: {account_detail['id']}")
            print(f"   Transactions: {len(account_detail.get('transactions', []))}")
        else:
            print(f"   ❌ Account retrieval failed: {get_account_response.text}")
            return
        
        print("\n🎉 All tests passed! Authentication and account system is working correctly.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on localhost:8000")
        print("   Start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_auth_flow()
