#!/usr/bin/env python3
"""
Migration script to add eco_credits column to users table
"""
import sqlite3
import os

# Path to the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'receipts.db')

def add_eco_credits_column():
    """Add eco_credits column to users table if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'eco_credits' not in column_names:
            print("Adding eco_credits column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN eco_credits INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Successfully added eco_credits column")
        else:
            print("✅ eco_credits column already exists")

        conn.close()

    except Exception as e:
        print(f"❌ Error adding eco_credits column: {e}")

if __name__ == "__main__":
    add_eco_credits_column()
