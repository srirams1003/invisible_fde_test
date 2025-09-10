"""
Transactions router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.db import get_db
from app.models import Account, Transaction, TransactionType, AccountHolder
from app.schemas import TransactionCreate, TransactionResponse
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

@router.post("/{account_id}", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    account_id: int,
    transaction_data: TransactionCreate,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a deposit or withdrawal transaction for the specified account
    """
    # Verify account ownership
    account = verify_account_ownership(account_id, current_user, db)
    
    # Verify the transaction is for the correct account
    if transaction_data.account_id != account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account ID mismatch"
        )
    
    # Check for sufficient funds for withdrawals
    if transaction_data.type == TransactionType.WITHDRAWAL:
        if account.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds"
            )
    
    # Create transaction
    db_transaction = Transaction(
        account_id=account_id,
        type=transaction_data.type,
        amount=transaction_data.amount,
        description=transaction_data.description
    )
    
    # Update account balance
    if transaction_data.type == TransactionType.DEPOSIT:
        account.balance += transaction_data.amount
    elif transaction_data.type == TransactionType.WITHDRAWAL:
        account.balance -= transaction_data.amount
    
    # Save to database
    db.add(db_transaction)
    db.add(account)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/{account_id}", response_model=List[TransactionResponse])
async def list_transactions(
    account_id: int,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all transactions for the specified account
    """
    # Verify account ownership
    account = verify_account_ownership(account_id, current_user, db)
    
    # Get transactions ordered by creation date (newest first)
    transactions = db.query(Transaction).filter(
        Transaction.account_id == account_id
    ).order_by(Transaction.created_at.desc()).all()
    
    return transactions
