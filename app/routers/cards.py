"""
Cards router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import random
import string

from app.db import get_db
from app.models import Account, Card, AccountHolder
from app.schemas import CardCreate, CardResponse, CardUpdate
from app.auth import get_current_active_user

router = APIRouter()

def generate_card_number():
    """Generate a masked card number for demo purposes"""
    # Generate last 4 digits
    last4 = ''.join(random.choices(string.digits, k=4))
    return f"****-****-****-{last4}"

def generate_card_brand():
    """Generate a random card brand"""
    brands = ["VISA", "MASTERCARD", "AMERICAN EXPRESS", "DISCOVER"]
    return random.choice(brands)

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

@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    card_data: CardCreate,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new card for the specified account
    """
    # Verify account ownership
    account = verify_account_ownership(card_data.account_id, current_user, db)
    
    # Verify the card is being created for the current user
    if card_data.holder_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create card for another user"
        )
    
    # Generate card details
    masked_number = generate_card_number()
    brand = generate_card_brand()
    last4 = masked_number[-4:]
    
    # Create new card
    db_card = Card(
        account_id=card_data.account_id,
        holder_id=card_data.holder_id,
        masked_number=masked_number,
        brand=brand,
        last4=last4,
        active=True
    )
    
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    
    return db_card

@router.get("/", response_model=List[CardResponse])
async def list_cards(
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all cards for the current user
    """
    cards = db.query(Card).filter(Card.holder_id == current_user.id).all()
    return cards

@router.get("/account/{account_id}", response_model=List[CardResponse])
async def list_account_cards(
    account_id: int,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all cards for a specific account owned by the current user
    """
    # Verify account ownership
    account = verify_account_ownership(account_id, current_user, db)
    
    cards = db.query(Card).filter(
        Card.account_id == account_id,
        Card.holder_id == current_user.id
    ).all()
    
    return cards

@router.patch("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: int,
    card_update: CardUpdate,
    current_user: AccountHolder = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update card status (activate/deactivate)
    """
    card = db.query(Card).filter(
        Card.id == card_id,
        Card.holder_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found or access denied"
        )
    
    # Update card fields
    if card_update.active is not None:
        card.active = card_update.active
    
    db.add(card)
    db.commit()
    db.refresh(card)
    
    return card
