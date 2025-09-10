"""
Accounts router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Account, AccountHolder
from app.schemas import AccountCreate, AccountResponse, AccountWithTransactions
from app.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new account for the current user
    """
    # Verify the account is being created for the current user
    if account_data.holder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create account for another user"
        )
    
    # Create new account
    db_account = Account(
        holder_id=account_data.holder_id,
        type=account_data.type,
        balance=0.0
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account

@router.get("/", response_model=List[AccountResponse])
async def list_accounts(
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all accounts for the current user
    """
    accounts = db.query(Account).filter(Account.holder_id == current_user.id).all()
    return accounts

@router.get("/{account_id}", response_model=AccountWithTransactions)
async def get_account(
    account_id: int,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get account by ID (only if owned by current user)
    """
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
