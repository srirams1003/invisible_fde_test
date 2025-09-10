#!/usr/bin/env python3
"""
Database initialization script for Banking REST Service
Run this script to create all required database tables.
"""

from app.db import engine, Base
from app.models import AccountHolder, Account, Transaction, Card

def init_database():
    """Create all database tables"""
    print("🏦 Banking REST Service - Database Initialization")
    print("=" * 50)
    
    try:
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result]
            print(f"📋 Created tables: {', '.join(tables)}")
        
        print("\n🎉 Database initialization complete!")
        print("💡 You can now start the server with: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)
