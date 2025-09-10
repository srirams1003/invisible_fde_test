"""
Statements router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import datetime, timedelta

from app.db import get_db
from app.models import Account, Transaction, TransactionType, AccountHolder
from app.schemas import StatementRequest, StatementResponse, TransactionResponse
from app.auth import get_current_active_user

router = APIRouter()

def verify_account_ownership(account_id: int, current_user: AccountHolder, db: Session) -> Account:
    """Verify that the account belongs to the current user"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.holder_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found or access denied"
        )
    
    return account

@router.get("/{account_id}", response_model=StatementResponse)
async def get_account_statement(
    account_id: int,
    start_date: Optional[datetime] = Query(None, description="Start date for statement (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date for statement (ISO format)"),
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get account statement with balance and transaction history
    """
    # Verify account ownership
    account = verify_account_ownership(account_id, current_user, db)
    
    # Set default date range if not provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)  # Last 30 days by default
    
    # Build query for transactions
    query = db.query(Transaction).filter(Transaction.account_id == account_id)
    
    # Apply date filters
    query = query.filter(
        and_(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
    )
    
    # Get transactions ordered by date (newest first)
    transactions = query.order_by(Transaction.created_at.desc()).all()
    
    # Calculate totals
    total_deposits = sum(
        t.amount for t in transactions 
        if t.type == TransactionType.DEPOSIT
    )
    total_withdrawals = sum(
        t.amount for t in transactions 
        if t.type == TransactionType.WITHDRAWAL
    )
    
    # Convert transactions to response format
    transaction_responses = [
        TransactionResponse(
            id=t.id,
            account_id=t.account_id,
            type=t.type,
            amount=t.amount,
            description=t.description,
            created_at=t.created_at
        ) for t in transactions
    ]
    
    return StatementResponse(
        account_id=account_id,
        start_date=start_date,
        end_date=end_date,
        transactions=transaction_responses,
        total_deposits=total_deposits,
        total_withdrawals=total_withdrawals,
        ending_balance=account.balance
    )

@router.get("/{account_id}/summary")
async def get_account_summary(
    account_id: int,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get quick account summary with current balance and recent activity
    """
    # Verify account ownership
    account = verify_account_ownership(account_id, current_user, db)
    
    # Get recent transactions (last 10)
    recent_transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.created_at.desc()).limit(10).all()
    
    # Get transaction counts by type
    deposit_count = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.type == TransactionType.DEPOSIT
    ).count()
    
    withdrawal_count = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.type == TransactionType.WITHDRAWAL
    ).count()
    
    return {
        "account_id": account_id,
        "account_type": account.type,
        "current_balance": account.balance,
        "recent_transactions": len(recent_transactions),
        "total_deposits": deposit_count,
        "total_withdrawals": withdrawal_count,
        "account_created": account.created_at,
        "last_updated": account.updated_at
    }
