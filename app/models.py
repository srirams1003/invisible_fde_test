"""
SQLAlchemy models for the Banking REST Service
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
import enum

class AccountType(str, enum.Enum):
    """Account type enumeration"""
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"

class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"

class AccountHolder(Base):
    """Account holder model"""
    __tablename__ = "account_holders"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="customer")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    accounts = relationship("Account", back_populates="holder", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="holder", cascade="all, delete-orphan")

class Account(Base):
    """Account model"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    holder_id = Column(Integer, ForeignKey("account_holders.id"), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    holder = relationship("AccountHolder", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="account", cascade="all, delete-orphan")

class Transaction(Base):
    """Transaction model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    account = relationship("Account", back_populates="transactions")

class Card(Base):
    """Card model"""
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    holder_id = Column(Integer, ForeignKey("account_holders.id"), nullable=False)
    masked_number = Column(String(19), nullable=False)  # Format: ****-****-****-1234
    brand = Column(String(50), nullable=False)  # VISA, MASTERCARD, etc.
    last4 = Column(String(4), nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    account = relationship("Account", back_populates="cards")
    holder = relationship("AccountHolder", back_populates="cards")
