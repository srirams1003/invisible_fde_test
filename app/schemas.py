"""
Pydantic schemas for request/response models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models import AccountType, TransactionType

# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    class Config:
        from_attributes = True

# AccountHolder schemas
class AccountHolderBase(BaseSchema):
    """Base account holder schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)

class AccountHolderCreate(AccountHolderBase):
    """Schema for creating account holder"""
    password: str = Field(..., min_length=8, max_length=100)

class AccountHolderUpdate(BaseSchema):
    """Schema for updating account holder"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    active: Optional[bool] = None

class AccountHolderResponse(AccountHolderBase):
    """Schema for account holder response"""
    id: int
    role: str
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class AccountHolderWithAccounts(AccountHolderResponse):
    """Account holder with accounts"""
    accounts: List["AccountResponse"] = []

# Account schemas
class AccountBase(BaseSchema):
    """Base account schema"""
    type: AccountType

class AccountCreate(AccountBase):
    """Schema for creating account"""
    holder_id: int

class AccountUpdate(BaseSchema):
    """Schema for updating account"""
    type: Optional[AccountType] = None

class AccountResponse(AccountBase):
    """Schema for account response"""
    id: int
    holder_id: int
    balance: float
    created_at: datetime
    updated_at: Optional[datetime] = None

class AccountWithTransactions(AccountResponse):
    """Account with transactions"""
    transactions: List["TransactionResponse"] = []

# Transaction schemas
class TransactionBase(BaseSchema):
    """Base transaction schema"""
    type: TransactionType
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)

class TransactionCreate(TransactionBase):
    """Schema for creating transaction"""
    account_id: int

class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    id: int
    account_id: int
    created_at: datetime

# Card schemas
class CardBase(BaseSchema):
    """Base card schema"""
    masked_number: str = Field(..., pattern=r'^\*\*\*\*-\*\*\*\*-\*\*\*\*-\d{4}$')
    brand: str = Field(..., min_length=2, max_length=50)
    last4: str = Field(..., pattern=r'^\d{4}$')

class CardCreate(CardBase):
    """Schema for creating card"""
    account_id: int
    holder_id: int

class CardUpdate(BaseSchema):
    """Schema for updating card"""
    active: Optional[bool] = None

class CardResponse(CardBase):
    """Schema for card response"""
    id: int
    account_id: int
    holder_id: int
    active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

# Authentication schemas
class LoginRequest(BaseSchema):
    """Schema for login request"""
    email: EmailStr
    password: str

class TokenResponse(BaseSchema):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseSchema):
    """Schema for token data"""
    email: Optional[str] = None

# Transfer schemas
class TransferRequest(BaseSchema):
    """Schema for money transfer request"""
    from_account_id: int
    to_account_id: int
    amount: float = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)

class TransferResponse(BaseSchema):
    """Schema for transfer response"""
    transaction_id: int
    from_account_id: int
    to_account_id: int
    amount: float
    created_at: datetime

# Statement schemas
class StatementRequest(BaseSchema):
    """Schema for statement request"""
    account_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class StatementResponse(BaseSchema):
    """Schema for statement response"""
    account_id: int
    start_date: datetime
    end_date: datetime
    transactions: List[TransactionResponse]
    total_deposits: float
    total_withdrawals: float
    ending_balance: float

# Update forward references
AccountHolderWithAccounts.model_rebuild()
AccountWithTransactions.model_rebuild()
