"""
Banking REST Service - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Banking REST Service",
    description="A secure banking REST API with authentication, accounts, and transactions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers (will be created in subsequent steps)
from app.routers import auth, account_holders, accounts, transactions, transfers, cards, statements

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(account_holders.router, prefix="/api/v1/account-holders", tags=["account-holders"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(transfers.router, prefix="/api/v1/transfers", tags=["transfers"])
app.include_router(cards.router, prefix="/api/v1/cards", tags=["cards"])
app.include_router(statements.router, prefix="/api/v1/statements", tags=["statements"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Banking REST Service API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
