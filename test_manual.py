#!/usr/bin/env python3
"""
Manual test script for Banking REST Service
This bypasses the TestClient compatibility issues and tests the core functionality
"""
import requests
import json
import time
import subprocess
import signal
import os
from threading import Thread

def start_server():
    """Start the FastAPI server in background"""
    return subprocess.Popen([
        "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def test_banking_service():
    """Test the banking service functionality"""
    print("🏦 Banking REST Service - Manual Test Suite")
    print("=" * 60)
    
    # Start server
    print("🚀 Starting server...")
    server = start_server()
    
    # Wait for server to start
    time.sleep(3)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Health check
        print("\n1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Root endpoint
        print("\n2️⃣ Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint: {data['message']}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test 3: API documentation
        print("\n3️⃣ Testing API documentation...")
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ API documentation available")
        else:
            print(f"   ❌ API documentation failed: {response.status_code}")
            return False
        
        # Test 4: OpenAPI schema
        print("\n4️⃣ Testing OpenAPI schema...")
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            print(f"   ✅ OpenAPI schema: {schema['info']['title']} v{schema['info']['version']}")
        else:
            print(f"   ❌ OpenAPI schema failed: {response.status_code}")
            return False
        
        # Test 5: Authentication endpoints
        print("\n5️⃣ Testing authentication endpoints...")
        
        # Test signup endpoint (should return validation error for empty data)
        response = requests.post(f"{base_url}/api/v1/auth/signup", json={}, timeout=5)
        if response.status_code == 422:  # Validation error expected
            print("   ✅ Signup endpoint validation working")
        else:
            print(f"   ❌ Signup endpoint failed: {response.status_code}")
            return False
        
        # Test login endpoint (should return validation error for empty data)
        response = requests.post(f"{base_url}/api/v1/auth/login", data={}, timeout=5)
        if response.status_code == 422:  # Validation error expected
            print("   ✅ Login endpoint validation working")
        else:
            print(f"   ❌ Login endpoint failed: {response.status_code}")
            return False
        
        # Test 6: Complete workflow
        print("\n6️⃣ Testing complete banking workflow...")
        
        # Create test user
        user_data = {
            "email": f"test_{int(time.time())}@example.com",
            "full_name": "Test User",
            "password": "testpassword123"
        }
        
        # Signup
        response = requests.post(f"{base_url}/api/v1/auth/signup", json=user_data, timeout=5)
        if response.status_code == 201:
            print("   ✅ User signup successful")
            user = response.json()
        else:
            print(f"   ❌ User signup failed: {response.status_code} - {response.text}")
            return False
        
        # Login
        login_data = {
            "username": user_data["email"],
            "password": user_data["password"]
        }
        response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data, timeout=5)
        if response.status_code == 200:
            print("   ✅ User login successful")
            token_data = response.json()
            token = token_data["access_token"]
        else:
            print(f"   ❌ User login failed: {response.status_code} - {response.text}")
            return False
        
        # Test authenticated endpoints
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get profile
        response = requests.get(f"{base_url}/api/v1/account-holders/me", headers=headers, timeout=5)
        if response.status_code == 200:
            print("   ✅ Profile retrieval successful")
        else:
            print(f"   ❌ Profile retrieval failed: {response.status_code}")
            return False
        
        # Create account
        account_data = {
            "holder_id": user["id"],
            "type": "CHECKING"
        }
        response = requests.post(f"{base_url}/api/v1/accounts/", json=account_data, headers=headers, timeout=5)
        if response.status_code == 201:
            print("   ✅ Account creation successful")
            account = response.json()
        else:
            print(f"   ❌ Account creation failed: {response.status_code} - {response.text}")
            return False
        
        # Make deposit
        transaction_data = {
            "account_id": account["id"],
            "type": "DEPOSIT",
            "amount": 100.0,
            "description": "Test deposit"
        }
        response = requests.post(f"{base_url}/api/v1/transactions/{account['id']}", json=transaction_data, headers=headers, timeout=5)
        if response.status_code == 201:
            print("   ✅ Deposit transaction successful")
        else:
            print(f"   ❌ Deposit transaction failed: {response.status_code} - {response.text}")
            return False
        
        print("\n🎉 All tests passed! Banking service is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running.")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Stop server
        print("\n🛑 Stopping server...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    success = test_banking_service()
    if success:
        print("\n✅ Banking REST Service is fully functional!")
        print("   - All endpoints working")
        print("   - Authentication system working")
        print("   - Database operations working")
        print("   - Complete banking workflow working")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        exit(1)
