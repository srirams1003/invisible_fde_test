# AI Usage Log

## Overview
This document mentions the AI tools I used to complete this assignment and how I used them.

## AI Tools Used

### AI Assistants
- **Cursor IDE** - Main AI agent to develop and test the service end-to-end
- **ChatGPT** - Used it initially to get an idea of how to prompt the Cursor Agent in the most optimal way to achieve the objectives outlined in the assignment

#### Here is the prompt I put into the ChatGPT as the first step of working on this assignment (I pasted in the whole assignment description first and then asked it the follwing):

```md

I plan to use FastAPI and Python along with a SQLite database with the SQLAlchemy ORM to build this service. I plan to handle authentication and security with JWT and bcrypt for hashing passwords. I plan to use Cursor Agent IDE for development. Structure prompts for me to iteratively build this service using AI-driven development and make sure to make the following things explicit to Cursor Agent:
Set up a venv instead of installing packages directly on the machine. Make it explicit to the cursor agent that I want it to only implement things from the current prompt instead of doing everything at once as I give it the entire assignment in the beginning so it has context about the bigger picture rather than having it to one-shot implement all the requirements.

```

Here is what ChatGPT gave me to put into Cursor Agent IDE to iteratively build out the service:

```md
You are my AI pair programmer. Context: I am completing a take-home test called “Banking REST Service” where I must show AI-driven development practices. I will paste the entire assignment for context. You MUST NOT try to complete the whole thing at once. Instead, follow my prompts one by one. Only implement what I ask in the current step.

Assignment Summary:
- Build a Banking REST Service with FastAPI + SQLite
- Implement: signup, authentication, account holders, accounts, transactions, money transfer, cards, statements
- Use SQLAlchemy ORM, JWT for auth, bcrypt for password hashing
- Deliverables: modular code (routers/models/schemas), pytest tests, demo client, Dockerfile, SOLUTION.md, SECURITY.md, AI_USAGE.md
- Must use AI-driven development practices, regular commits, and provide an AI usage log
- Security is paramount (no secrets in code, use env vars)

Development guidelines you must follow:
- Use FastAPI for the REST API
- Follow clean code principles (modular, PEP8, docstrings)
- Use SQLAlchemy ORM with SQLite
- Separate code into models.py, schemas.py, routers/, auth.py
- Follow TDD: generate pytest tests for happy paths
- Use JWT for auth, bcrypt for password hashing
- Ensure security best practices (no secrets in code, env vars instead)
- Write clear commit-sized chunks of code, not one giant file
- Prefer simplicity and readability over cleverness

Here is the whole assignment for context. Remember that you must only implement it iteratively as I prompt you subsquently:

# AI-Driven Development Test: Banking REST Service
## Overview
You are tasked with developing a REST service that a bank would use. To complete the test in a
short amount of time, you MUST use AI-driven development practices. This assessment
evaluates your ability to leverage AI tools effectively to design and implement a banking service.
Make sure you commit to the repository when you get started and commit continuously
until you are done. This way, we are going to track your overall time. You should only
dedicate 1 hour.
## Project Requirements
### Core Components
You must develop the following components:
1. **Service Interface**
- Signing up
- Authentication
- Account Holders
- Accounts
- Transactions
- Money Transfer
- Cards
- Statements
2. **Database** (using SQLLite)
- Database implementation
### Technology Stack
Your choices of technologies will be judged against the nature of the application and how
effective those technologies are in modern software development ecosystems
### Getting Started
1. Begin development using your AI tools of choice
## Deliverables
1. **Source Code**
- All components in separate directories
- Tests for critical functionality
- Configuration files
2. **Documentation**

- SOLUTION.md with setup instructions
- API documentation
- Security considerations document
3. **AI Usage Report**
- Tools used (Claude Code, ChatGPT, Cursor, Copilot, etc.)
- Example prompts and iterations
- Challenges faced and how AI helped solve them
- Areas where manual intervention was necessary
4. **Demo**
- Video walkthrough
- Test client application demonstrating the flow
## Ways of Working
1. Commit regularly with meaningful messages
2. Include your AI usage log as a Markdown file
## Additional Notes
- You MUST use any AI tools available to you
- External libraries and frameworks are allowed
- Focus on demonstrating effective AI-driven development
- Partial implementations are acceptable if well-documented
- Security is paramount - ensure no secrets are committed

I will now begin with Prompt 1. Wait for me to paste it in.


Prompt 1:

Set up the project structure with the following:
- Virtual environment setup instructions in SOLUTION.md
- .env file support using python-dotenv, with .env.example listing variables like SECRET_KEY and DATABASE_URL
- Directory structure: app/, app/routers/, tests/, client/
- Files: app/main.py, app/db.py, app/models.py, app/schemas.py, app/auth.py
- Empty router files under app/routers for: auth, account_holders, accounts, transactions, transfers, cards, statements
- requirements.txt with FastAPI, SQLAlchemy, pydantic, passlib[bcrypt], python-jose, python-dotenv, pytest, requests
- A Dockerfile to run uvicorn
- Placeholders for SOLUTION.md, SECURITY.md, AI_USAGE.md

Make app/main.py start an empty FastAPI app and include all routers (even if empty).



Prompt 2:

Fill in SQLAlchemy models in app/models.py:
- AccountHolder (id, email, full_name, hashed_password, role, active, accounts relation)
- Account (id, holder_id, type, balance, created_at, relations)
- Transaction (id, account_id, type, amount, description, created_at)
- Card (id, account_id, masked_number, brand, last4, active)

Use enums for AccountType (CHECKING, SAVINGS) and TransactionType (DEPOSIT, WITHDRAWAL, TRANSFER).

Also generate Pydantic schemas in app/schemas.py for requests and responses.




Prompt 3:

Implement authentication and account endpoints:
- app/auth.py: password hashing (bcrypt), JWT token creation/validation, get_current_user dependency
- app/routers/auth.py: /signup and /login endpoints
  - /signup hashes password and saves AccountHolder
  - /login verifies password and returns JWT
- app/routers/account_holders.py: /me endpoint to return current user profile
- app/routers/accounts.py: create account, list accounts, get account by id
Restrict access to accounts to their owner.




Prompt 4:

Implement:
- app/routers/transactions.py:
  - POST /transactions/{account_id}: deposit or withdrawal
  - GET /transactions/{account_id}: list transactions
- app/routers/transfers.py:
  - POST /transfers: transfer money between two accounts
  - Creates two transaction rows: debit from source, credit to destination
  - Enforce sufficient funds and ownership




Prompt 5:

Finish implementation:
- app/routers/cards.py: create card for account, list cards
- app/routers/statements.py: return account balance and recent transactions
- tests/test_happy_path.py: pytest tests for signup/login, create account, deposit, transfer, statement
- client/demo_client.py: script using requests that does:
  - Signup/login
  - Create checking and savings accounts
  - Deposit into checking
  - Transfer to savings
  - Print statements
- Add initial content to SOLUTION.md, SECURITY.md, and AI_USAGE.md placeholders

```

### NOTE: My entire conversation with the Cursor Agent is in `cursor_developing_a_banking_rest_service.md`


### AI Development Workflow
1. **Architecture Planning**: AI-assisted system design and structure
2. **Code Generation**: Automated boilerplate and implementation
3. **Code Review**: AI-powered code analysis and improvements
4. **Documentation**: Comprehensive documentation generation
5. **Testing**: AI-assisted test case creation and validation
6. **Security**: AI-guided security implementation and review

## Development Process

### Phase 1: Project Foundation (AI-Driven)

#### Project Structure Setup
```
AI Prompt: "Set up the project structure with the following:
- Virtual environment setup instructions in SOLUTION.md
- .env file support using python-dotenv
- Directory structure: app/, app/routers/, tests/, client/
- Files: app/main.py, app/db.py, app/models.py, app/schemas.py, app/auth.py
- Empty router files for all modules
- requirements.txt with all dependencies
- Dockerfile for uvicorn deployment
- Placeholders for documentation files"
```

**AI Generated**:
- Complete FastAPI application structure
- Database configuration with SQLAlchemy
- Environment variable management
- Docker containerization setup
- Comprehensive documentation templates

### Phase 2: Data Models & Schemas (AI-Driven)

#### Database Models
```
AI Prompt: "Fill in SQLAlchemy models in app/models.py:
- AccountHolder (id, email, full_name, hashed_password, role, active, accounts relation)
- Account (id, holder_id, type, balance, created_at, relations)
- Transaction (id, account_id, type, amount, description, created_at)
- Card (id, account_id, masked_number, brand, last4, active)

Use enums for AccountType (CHECKING, SAVINGS) and TransactionType (DEPOSIT, WITHDRAWAL, TRANSFER).

Also generate Pydantic schemas in app/schemas.py for requests and responses."
```

**AI Generated**:
- Complete SQLAlchemy models with relationships
- Type-safe enums for business logic
- Comprehensive Pydantic schemas
- Proper foreign key relationships
- Data validation rules

### Phase 3: Authentication System (AI-Driven)

#### Authentication Implementation
```
AI Prompt: "Implement authentication and account endpoints:
- app/auth.py: password hashing (bcrypt), JWT token creation/validation, get_current_user dependency
- app/routers/auth.py: /signup and /login endpoints
- app/routers/account_holders.py: /me endpoint to return current user profile
- app/routers/accounts.py: create account, list accounts, get account by id
Restrict access to accounts to their owner."
```

**AI Generated**:
- Complete JWT authentication system
- bcrypt password hashing
- OAuth2 compatible login endpoint
- User profile management
- Account CRUD with ownership validation
- Comprehensive error handling

### Phase 4: Transaction System (AI-Driven)

#### Transaction & Transfer Implementation
```
AI Prompt: "Implement:
- app/routers/transactions.py: POST /transactions/{account_id}: deposit or withdrawal, GET /transactions/{account_id}: list transactions
- app/routers/transfers.py: POST /transfers: transfer money between two accounts
- Creates two transaction rows: debit from source, credit to destination
- Enforce sufficient funds and ownership"
```

**AI Generated**:
- Complete transaction management system
- Atomic money transfer operations
- Balance validation and fund checking
- Transaction history tracking
- Comprehensive error handling

### Phase 5: Other Features and Testing (AI-Driven)

#### Cards & Statements Implementation
```
AI Prompt: "Finish implementation:
- app/routers/cards.py: create card for account, list cards
- app/routers/statements.py: return account balance and recent transactions
- tests/test_happy_path.py: pytest tests for signup/login, create account, deposit, transfer, statement
- client/demo_client.py: script using requests that does complete workflow
- Add initial content to SOLUTION.md, SECURITY.md, and AI_USAGE.md placeholders"
```

**AI Generated**:
- Card management system with security
- Statement generation with date filtering
- Comprehensive pytest test suite
- Complete demo client with workflow
- Professional documentation

## AI-Generated Code Examples

### 1. FastAPI Application Structure
```python
# AI-generated main.py with complete router integration
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

app = FastAPI(
    title="Banking REST Service",
    description="A secure banking REST API with authentication, accounts, and transactions",
    version="1.0.0"
)
```

### 2. Security Implementation
```python
# AI-generated authentication system
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AccountHolder:
    """Get current authenticated user from JWT token"""
    # Comprehensive JWT validation and user lookup
```

### 3. Database Models
```python
# AI-generated SQLAlchemy models with relationships
class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    holder_id = Column(Integer, ForeignKey("account_holders.id"), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    # ... with proper relationships
```

### 4. Comprehensive Testing
```python
# AI-generated pytest test suite
class TestAuthentication:
    def test_signup_success(self, setup_database, test_user_data):
        """Test successful user signup"""
        # Complete test implementation
```

## Challenges and AI Solutions

### Challenge 1: Python 3.13 Compatibility Issues
**Problem**: `pydantic.errors.PydanticUserError: 'regex' is removed. use 'pattern' instead`

**AI Solution**: 
- Updated Pydantic schemas to use `pattern` instead of `regex` parameter
- Fixed Pydantic v2 compatibility issues in CardBase schema

### Challenge 2: Pydantic Core Build Failures
**Problem**: `ERROR: Failed building wheel for pydantic-core` during pip install

**AI Solution**: 
- Upgraded Pydantic from 2.5.0 to 2.8.2 for Python 3.13 compatibility
- Updated requirements.txt with compatible versions

### Challenge 3: SQLAlchemy Compatibility Issues
**Problem**: `AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'> directly inherits TypingOnly`

**AI Solution**: 
- Updated SQLAlchemy from 2.0.23 to 2.0.43 for Python 3.13 compatibility
- Fixed declarative_base import deprecation warning

### Challenge 4: TestClient Compatibility Issues
**Problem**: `TypeError: Client.__init__() got an unexpected keyword argument 'app'`

**AI Solution**: 
- Created alternative testing approaches (manual tests, working pytest tests)
- Documented the limitation and provided working test alternatives
- Created comprehensive test coverage through multiple approaches

### Challenge 5: Missing Dependencies
**Problem**: `ImportError: email-validator is not installed` and `RuntimeError: Form data requires "python-multipart"`

**AI Solution**: 
- Added missing dependencies: email-validator, python-multipart, httpx
- Updated requirements.txt with all necessary packages

### Challenge 6: Database Table Creation
**Problem**: `sqlite3.OperationalError: no such table: account_holders`

**AI Solution**: 
- Created `init_db.py` script for easy database initialization
- Updated setup instructions to include required database creation step
- Added verification steps to confirm tables are created

### Challenge 7: Git Cache File Management
**Problem**: `__pycache__` files showing up in git status

**AI Solution**: 
- Removed `__pycache__` files from git tracking
- Enhanced `.gitignore` file with comprehensive Python ignores
- Cleaned up repository to exclude all unnecessary files

### Challenge 8: Documentation Clarity
**Problem**: Unclear setup instructions and test status

**AI Solution**: 
- Updated SOLUTION.md with clear testing status (working vs. broken tests)
- Added step-by-step database setup instructions
- Created comprehensive troubleshooting section

## Areas Requiring Manual Intervention

1. ChatGPT did not include in the prompt initially to Cursor Agent that a virtual environment needed to be created for Python to install packages and this would have resulted in all the packages from requirements.txt being installed directly on my local machine.
2. .env and .env.example files needed to be created manually as the agent did not create these for me.
3. Cursor agent committed banking.db by default which should be ignored properly via .gitignore as it has user passwords and other sensitive info.
4. Some pycache and other files that are supposed to be in .gitignore slipped through the cracks and made it to the remote and I thus had to untrack them.
5. There was a version mismatch between Python 3.13 and some packages that Pytest needed due to which I could not finish getting all the Pytest tests to work within the 1 hour window. Cursor Agent was not helpful here as it kept going in circles failing to fix the incompatibility issue. However, I did make sure all the other tests and the end-to-end tests worked.
