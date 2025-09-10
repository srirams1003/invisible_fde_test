### **API Documentation**

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Project Structure

```
invisible_fde_test/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── db.py                # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication endpoints
│       ├── account_holders.py # User profile management
│       ├── accounts.py      # Account CRUD operations
│       ├── transactions.py  # Deposit/withdrawal operations
│       ├── transfers.py     # Money transfer between accounts
│       ├── cards.py         # Card management
│       └── statements.py    # Account statements
├── tests/
│   ├── test_happy_path.py   # Comprehensive pytest tests (has compatibility issues)
│   ├── test_banking_service.py # Additional test suite (has compatibility issues)
│   ├── test_simple.py       # Simple tests (has compatibility issues)
│   └── test_working.py      # Working test attempts (has compatibility issues)
├── test_manual.py           # ✅ WORKING manual test suite (17 tests)
├── test_auth.py             # ✅ WORKING pytest test (authentication)
├── test_transactions.py     # ✅ WORKING pytest test (transactions)
├── init_db.py               # Database initialization script
├── client/
│   └── demo_client.py       # ✅ WORKING demo client (end-to-end)
├── requirements.txt         # Python dependencies
├── pytest.ini              # pytest configuration
├── Dockerfile              # Container configuration
├── .env.example            # Environment template
├── .env                    # Environment variables
├── .gitignore              # Git ignore rules
├── banking.db              # SQLite database (auto-created)
├── SOLUTION.md             # This documentation
├── SECURITY.md             # Security considerations
└── AI_USAGE.md             # AI development practices log
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/login` - User login (OAuth2 compatible)

### Account Holders
- `GET /api/v1/account-holders/me` - Get current user profile

### Accounts
- `POST /api/v1/accounts/` - Create new account
- `GET /api/v1/accounts/` - List user's accounts
- `GET /api/v1/accounts/{id}` - Get specific account details

### Transactions
- `POST /api/v1/transactions/{account_id}` - Create deposit/withdrawal
- `GET /api/v1/transactions/{account_id}` - List account transactions

### Transfers
- `POST /api/v1/transfers/` - Transfer money between accounts

### Cards
- `POST /api/v1/cards/` - Create new card
- `GET /api/v1/cards/` - List user's cards
- `GET /api/v1/cards/account/{account_id}` - List account cards
- `PATCH /api/v1/cards/{card_id}` - Update card status

### Statements
- `GET /api/v1/statements/{account_id}` - Get account statement
- `GET /api/v1/statements/{account_id}/summary` - Get account summary


