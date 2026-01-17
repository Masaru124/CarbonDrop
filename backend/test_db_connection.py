#!/usr/bin/env python3
"""
Test database connection using DATABASE_URL from environment.
Usage: DATABASE_URL=postgresql://... python test_db_connection.py
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set")
    print("Example: export DATABASE_URL=postgresql://user:password@localhost:5432/dbname")
    exit(1)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"✓ Connected successfully to: {DATABASE_URL}")
        print("✓ Database test query passed")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    exit(1)

