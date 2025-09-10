"""
Money transfers router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db import get_db
from app.models import Account, Transaction, TransactionType, AccountHolder
from app.schemas import TransferRequest, TransferResponse
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

@router.post("/", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def transfer_money(
    transfer_data: TransferRequest,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Transfer money between two accounts owned by the current user
    """
    # Prevent self-transfer
    if transfer_data.from_account_id == transfer_data.to_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer to the same account"
        )
    
    # Verify both accounts belong to the current user
    from_account = verify_account_ownership(transfer_data.from_account_id, current_user, db)
    to_account = verify_account_ownership(transfer_data.to_account_id, current_user, db)
    
    # Check sufficient funds
    if from_account.balance < transfer_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds for transfer"
        )
    
    # Validate transfer amount
    if transfer_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer amount must be positive"
        )
    
    try:
        # Create debit transaction (withdrawal from source account)
        debit_transaction = Transaction(
            account_id=transfer_data.from_account_id,
            type=TransactionType.WITHDRAWAL,
            amount=transfer_data.amount,
            description=f"Transfer to Account {transfer_data.to_account_id}: {transfer_data.description or 'Money transfer'}"
        )
        
        # Create credit transaction (deposit to destination account)
        credit_transaction = Transaction(
            account_id=transfer_data.to_account_id,
            type=TransactionType.DEPOSIT,
            amount=transfer_data.amount,
            description=f"Transfer from Account {transfer_data.from_account_id}: {transfer_data.description or 'Money transfer'}"
        )
        
        # Update account balances
        from_account.balance -= transfer_data.amount
        to_account.balance += transfer_data.amount
        
        # Save all changes to database
        db.add(debit_transaction)
        db.add(credit_transaction)
        db.add(from_account)
        db.add(to_account)
        db.commit()
        
        # Refresh to get the transaction ID
        db.refresh(debit_transaction)
        
        return TransferResponse(
            transaction_id=debit_transaction.id,
            from_account_id=transfer_data.from_account_id,
            to_account_id=transfer_data.to_account_id,
            amount=transfer_data.amount,
            created_at=debit_transaction.created_at
        )
        
    except Exception as e:
        # Rollback on any error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transfer failed due to database error"
        )
