#!/usr/bin/env python3
"""
Demo client for Banking REST Service
Demonstrates the complete banking workflow: signup -> login -> create accounts -> deposit -> transfer -> statement
"""
import requests
import json
from datetime import datetime
import time

class BankingClient:
    """Banking REST Service client"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.accounts = {}
    
    def signup(self, email, full_name, password):
        """Register a new user"""
        print(f"📝 Registering user: {email}")
        
        user_data = {
            "email": email,
            "full_name": full_name,
            "password": password
        }
        
        response = requests.post(f"{self.base_url}/api/v1/auth/signup", json=user_data)
        
        if response.status_code == 201:
            user = response.json()
            print(f"   ✅ User registered successfully (ID: {user['id']})")
            return user
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return None
    
    def login(self, email, password):
        """Login user and get authentication token"""
        print(f"🔐 Logging in user: {email}")
        
        login_data = {
            "username": email,
            "password": password
        }
        
        response = requests.post(f"{self.base_url}/api/v1/auth/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            print(f"   ✅ Login successful")
            return True
        else:
            print(f"   ❌ Login failed: {response.text}")
            return False
    
    def get_headers(self):
        """Get authentication headers"""
        if not self.token:
            raise Exception("Not authenticated. Please login first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_profile(self):
        """Get current user profile"""
        print("👤 Getting user profile...")
        
        response = requests.get(f"{self.base_url}/api/v1/account-holders/me", headers=self.get_headers())
        
        if response.status_code == 200:
            profile = response.json()
            self.user_id = profile["id"]
            print(f"   ✅ Profile: {profile['full_name']} ({profile['email']})")
            return profile
        else:
            print(f"   ❌ Failed to get profile: {response.text}")
            return None
    
    def create_account(self, account_type):
        """Create a new account"""
        print(f"🏦 Creating {account_type} account...")
        
        account_data = {
            "holder_id": self.user_id,
            "type": account_type
        }
        
        response = requests.post(f"{self.base_url}/api/v1/accounts/", json=account_data, headers=self.get_headers())
        
        if response.status_code == 201:
            account = response.json()
            self.accounts[account_type.lower()] = account
            print(f"   ✅ {account_type} account created (ID: {account['id']}, Balance: ${account['balance']})")
            return account
        else:
            print(f"   ❌ Account creation failed: {response.text}")
            return None
    
    def deposit(self, account_type, amount, description="Deposit"):
        """Make a deposit to an account"""
        if account_type.lower() not in self.accounts:
            print(f"   ❌ {account_type} account not found")
            return None
        
        account = self.accounts[account_type.lower()]
        print(f"💰 Depositing ${amount} to {account_type} account...")
        
        transaction_data = {
            "account_id": account["id"],
            "type": "DEPOSIT",
            "amount": amount,
            "description": description
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/transactions/{account['id']}", 
            json=transaction_data, 
            headers=self.get_headers()
        )
        
        if response.status_code == 201:
            transaction = response.json()
            print(f"   ✅ Deposit successful (Transaction ID: {transaction['id']})")
            
            # Update local account balance
            account["balance"] += amount
            print(f"   💳 New balance: ${account['balance']}")
            return transaction
        else:
            print(f"   ❌ Deposit failed: {response.text}")
            return None
    
    def withdraw(self, account_type, amount, description="Withdrawal"):
        """Make a withdrawal from an account"""
        if account_type.lower() not in self.accounts:
            print(f"   ❌ {account_type} account not found")
            return None
        
        account = self.accounts[account_type.lower()]
        print(f"💸 Withdrawing ${amount} from {account_type} account...")
        
        transaction_data = {
            "account_id": account["id"],
            "type": "WITHDRAWAL",
            "amount": amount,
            "description": description
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/transactions/{account['id']}", 
            json=transaction_data, 
            headers=self.get_headers()
        )
        
        if response.status_code == 201:
            transaction = response.json()
            print(f"   ✅ Withdrawal successful (Transaction ID: {transaction['id']})")
            
            # Update local account balance
            account["balance"] -= amount
            print(f"   💳 New balance: ${account['balance']}")
            return transaction
        else:
            print(f"   ❌ Withdrawal failed: {response.text}")
            return None
    
    def transfer(self, from_account_type, to_account_type, amount, description="Transfer"):
        """Transfer money between accounts"""
        if from_account_type.lower() not in self.accounts:
            print(f"   ❌ {from_account_type} account not found")
            return None
        if to_account_type.lower() not in self.accounts:
            print(f"   ❌ {to_account_type} account not found")
            return None
        
        from_account = self.accounts[from_account_type.lower()]
        to_account = self.accounts[to_account_type.lower()]
        
        print(f"🔄 Transferring ${amount} from {from_account_type} to {to_account_type}...")
        
        transfer_data = {
            "from_account_id": from_account["id"],
            "to_account_id": to_account["id"],
            "amount": amount,
            "description": description
        }
        
        response = requests.post(f"{self.base_url}/api/v1/transfers/", json=transfer_data, headers=self.get_headers())
        
        if response.status_code == 201:
            transfer = response.json()
            print(f"   ✅ Transfer successful (Transaction ID: {transfer['transaction_id']})")
            
            # Update local account balances
            from_account["balance"] -= amount
            to_account["balance"] += amount
            print(f"   💳 {from_account_type} balance: ${from_account['balance']}")
            print(f"   💳 {to_account_type} balance: ${to_account['balance']}")
            return transfer
        else:
            print(f"   ❌ Transfer failed: {response.text}")
            return None
    
    def get_statement(self, account_type):
        """Get account statement"""
        if account_type.lower() not in self.accounts:
            print(f"   ❌ {account_type} account not found")
            return None
        
        account = self.accounts[account_type.lower()]
        print(f"📊 Getting statement for {account_type} account...")
        
        response = requests.get(f"{self.base_url}/api/v1/statements/{account['id']}", headers=self.get_headers())
        
        if response.status_code == 200:
            statement = response.json()
            print(f"   ✅ Statement retrieved")
            print(f"   📅 Period: {statement['start_date'][:10]} to {statement['end_date'][:10]}")
            print(f"   💰 Ending Balance: ${statement['ending_balance']}")
            print(f"   📈 Total Deposits: ${statement['total_deposits']}")
            print(f"   📉 Total Withdrawals: ${statement['total_withdrawals']}")
            print(f"   📋 Transactions: {len(statement['transactions'])}")
            
            # Show recent transactions
            if statement['transactions']:
                print(f"   📝 Recent transactions:")
                for i, txn in enumerate(statement['transactions'][:5]):  # Show first 5
                    print(f"      {i+1}. {txn['type']}: ${txn['amount']} - {txn['description']}")
            
            return statement
        else:
            print(f"   ❌ Statement retrieval failed: {response.text}")
            return None
    
    def create_card(self, account_type):
        """Create a card for an account"""
        if account_type.lower() not in self.accounts:
            print(f"   ❌ {account_type} account not found")
            return None
        
        account = self.accounts[account_type.lower()]
        print(f"💳 Creating card for {account_type} account...")
        
        card_data = {
            "account_id": account["id"],
            "holder_id": self.user_id,
            "masked_number": "****-****-****-1234",
            "brand": "VISA",
            "last4": "1234"
        }
        
        response = requests.post(f"{self.base_url}/api/v1/cards/", json=card_data, headers=self.get_headers())
        
        if response.status_code == 201:
            card = response.json()
            print(f"   ✅ Card created (ID: {card['id']}, {card['brand']} {card['masked_number']})")
            return card
        else:
            print(f"   ❌ Card creation failed: {response.text}")
            return None

def main():
    """Main demo function"""
    print("🏦 Banking REST Service Demo")
    print("=" * 50)
    
    # Initialize client
    client = BankingClient()
    
    try:
        # Demo user data
        email = f"demo_{int(time.time())}@example.com"
        full_name = "Demo User"
        password = "demopassword123"
        
        # 1. Signup
        print("\n1️⃣ USER REGISTRATION")
        print("-" * 30)
        user = client.signup(email, full_name, password)
        if not user:
            return
        
        # 2. Login
        print("\n2️⃣ USER LOGIN")
        print("-" * 30)
        if not client.login(email, password):
            return
        
        # 3. Get profile
        print("\n3️⃣ USER PROFILE")
        print("-" * 30)
        profile = client.get_profile()
        if not profile:
            return
        
        # 4. Create accounts
        print("\n4️⃣ ACCOUNT CREATION")
        print("-" * 30)
        checking = client.create_account("CHECKING")
        savings = client.create_account("SAVINGS")
        
        if not checking or not savings:
            return
        
        # 5. Make deposits
        print("\n5️⃣ DEPOSITS")
        print("-" * 30)
        client.deposit("CHECKING", 1000.0, "Initial checking deposit")
        client.deposit("SAVINGS", 500.0, "Initial savings deposit")
        
        # 6. Make withdrawals
        print("\n6️⃣ WITHDRAWALS")
        print("-" * 30)
        client.withdraw("CHECKING", 200.0, "ATM withdrawal")
        
        # 7. Transfer money
        print("\n7️⃣ MONEY TRANSFERS")
        print("-" * 30)
        client.transfer("CHECKING", "SAVINGS", 300.0, "Transfer to savings")
        
        # 8. Create cards
        print("\n8️⃣ CARD CREATION")
        print("-" * 30)
        client.create_card("CHECKING")
        client.create_card("SAVINGS")
        
        # 9. Get statements
        print("\n9️⃣ ACCOUNT STATEMENTS")
        print("-" * 30)
        client.get_statement("CHECKING")
        print()
        client.get_statement("SAVINGS")
        
        # 10. Final summary
        print("\n🔟 FINAL SUMMARY")
        print("-" * 30)
        print("✅ Demo completed successfully!")
        print(f"📧 User: {email}")
        print(f"🏦 Checking Account: ${client.accounts['checking']['balance']}")
        print(f"🏦 Savings Account: ${client.accounts['savings']['balance']}")
        print(f"💳 Total Cards: 2")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server.")
        print("   Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main()
