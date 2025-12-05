"""
Database migration script to add new columns for multi-domain support.

This script adds:
- document_type column to receipts table
- category column to items table

Run this script before starting the application with the new models.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, String, Enum as SQLEnum, text
from sqlalchemy.orm import sessionmaker
from app.models import Base, DocumentType
from app import database

def add_document_type_to_receipts():
    """Add document_type column to receipts table."""
    try:
        with database.engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("PRAGMA table_info(receipts)"))
            columns = [row[1] for row in result]

            if 'document_type' not in columns:
                # Add document_type column with default value
                conn.execute(text("ALTER TABLE receipts ADD COLUMN document_type VARCHAR(20) DEFAULT 'grocery'"))
                conn.commit()
                print("✓ Added document_type column to receipts table")
            else:
                print("✓ document_type column already exists in receipts table")

    except Exception as e:
        print(f"✗ Error adding document_type column: {e}")
        return False
    return True

def add_category_to_items():
    """Add category column to items table."""
    try:
        with database.engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("PRAGMA table_info(items)"))
            columns = [row[1] for row in result]

            if 'category' not in columns:
                # Add category column with default value
                conn.execute(text("ALTER TABLE items ADD COLUMN category VARCHAR(50) DEFAULT 'food'"))
                conn.commit()
                print("✓ Added category column to items table")
            else:
                print("✓ category column already exists in items table")

    except Exception as e:
        print(f"✗ Error adding category column: {e}")
        return False
    return True

def run_migration():
    """Run the database migration."""
    print("Starting database migration for multi-domain support...")
    print()

    success = True

    success &= add_document_type_to_receipts()
    success &= add_category_to_items()

    print()
    if success:
        print("🎉 Migration completed successfully!")
        print("You can now use the multi-domain CarbonDrop system.")
    else:
        print("❌ Migration failed. Please check the errors above.")
        print("You may need to run this manually or check your database permissions.")

if __name__ == "__main__":
    run_migration()
