# Banking REST Service - Solution Documentation

## Overview
A secure banking REST API built with FastAPI, SQLAlchemy, and SQLite, featuring authentication, account management, transactions, and more.

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
│       ├── account_holders.py
│       ├── accounts.py
│       ├── transactions.py
│       ├── transfers.py
│       ├── cards.py
│       └── statements.py
├── tests/                   # Test files
├── client/                  # Demo client
├── requirements.txt
├── Dockerfile
├── .env.example
├── .env
├── SOLUTION.md
├── SECURITY.md
└── AI_USAGE.md
```

## API Endpoints

*Endpoints will be documented as they are implemented*

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Docker Deployment

```bash
# Build image
docker build -t banking-rest-service .

# Run container
docker run -p 8000:8000 banking-rest-service
```

## Security Considerations

See SECURITY.md for detailed security information.

## AI Usage

See AI_USAGE.md for AI development practices and tools used.
