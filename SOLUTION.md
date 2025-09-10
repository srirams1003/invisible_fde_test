# Banking REST Service - Solution Documentation

## Overview
A secure banking REST API built with FastAPI, SQLAlchemy, and SQLite, featuring authentication, account management, transactions, transfers, cards, and statements. This service demonstrates AI-driven development practices and follows banking industry security standards.

## Features Implemented

### Core Banking Features
- **User Authentication**: JWT-based authentication with bcrypt password hashing
- **Account Management**: Create and manage CHECKING and SAVINGS accounts
- **Transactions**: Deposit and withdrawal operations with balance validation
- **Money Transfers**: Secure transfers between user's own accounts
- **Card Management**: Create and manage debit/credit cards for accounts
- **Statements**: Generate account statements with transaction history
- **Security**: Comprehensive access control and data validation

### Technical Features
- **RESTful API**: Clean, well-documented REST endpoints
- **Database**: SQLAlchemy ORM with SQLite for development
- **Validation**: Pydantic schemas for request/response validation
- **Testing**: Comprehensive pytest test suite
- **Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Docker**: Containerized deployment ready

## Setup Instructions

### 1. Virtual Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Update SECRET_KEY for production use
```

### 3. Database Setup

```bash
# The database will be created automatically on first run
# SQLite database file will be created at ./banking.db
```

### 4. Running the Application

```bash
# Development server
uvicorn app.main:app --reload

# Or run directly
python -m app.main
```

### 5. API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
banking-rest-service/
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
│   └── test_happy_path.py   # Comprehensive pytest tests
├── client/
│   └── demo_client.py       # Demo client script
├── requirements.txt
├── Dockerfile
├── .env.example
├── .env
├── SOLUTION.md
├── SECURITY.md
└── AI_USAGE.md
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

## Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_happy_path.py -v
```

### Test Coverage
The test suite covers:
- User registration and authentication
- Account creation and management
- Deposit and withdrawal operations
- Money transfers between accounts
- Card creation and management
- Statement generation
- Error handling and validation
- Security and access control

## Demo Client

### Run Demo
```bash
# Make sure the server is running first
uvicorn app.main:app --reload

# In another terminal, run the demo
python client/demo_client.py
```

The demo client demonstrates:
- Complete user registration and login flow
- Account creation (checking and savings)
- Deposit and withdrawal operations
- Money transfers between accounts
- Card creation
- Statement generation
- Real-time balance tracking

## Docker Deployment

### Build and Run
```bash
# Build image
docker build -t banking-rest-service .

# Run container
docker run -p 8000:8000 banking-rest-service
```

### Docker Compose (Optional)
```yaml
version: '3.8'
services:
  banking-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./banking.db
      - SECRET_KEY=your-secret-key-here
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt for password security
- **Access Control**: Users can only access their own data
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **Environment Variables**: No secrets in source code
- **HTTPS Ready**: Production-ready security configuration

## Performance Considerations

- **Database Indexing**: Proper indexes on frequently queried fields
- **Connection Pooling**: SQLAlchemy connection management
- **Async Support**: FastAPI async capabilities
- **Caching Ready**: Structure supports Redis/Memcached integration
- **Scalable Architecture**: Modular design for horizontal scaling

## Monitoring and Logging

- **Health Check**: `/health` endpoint for monitoring
- **Structured Logging**: Ready for structured logging integration
- **Error Tracking**: Comprehensive error handling and reporting
- **Metrics Ready**: Structure supports Prometheus/Grafana integration

## Security Considerations

See SECURITY.md for detailed security information.

## AI Usage

See AI_USAGE.md for AI development practices and tools used.

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure SQLite file permissions are correct
   - Check DATABASE_URL in .env file

2. **Authentication Errors**
   - Verify SECRET_KEY is set in .env
   - Check token expiration settings

3. **Import Errors**
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

4. **Port Already in Use**
   - Change port: `uvicorn app.main:app --port 8001`
   - Kill existing process: `lsof -ti:8000 | xargs kill`

### Support

For issues or questions:
1. Check the logs for error details
2. Verify environment configuration
3. Run tests to identify specific problems
4. Check API documentation at `/docs`
