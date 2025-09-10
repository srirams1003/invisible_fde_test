"""
Account holders router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AccountHolder
from app.schemas import AccountHolderResponse
from app.auth import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=AccountHolderResponse)
async def get_current_user_profile(
    current_user: AccountHolder = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    return current_user
