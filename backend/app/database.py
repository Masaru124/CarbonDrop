import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = (BASE_DIR.parent / 'carbondrop.db').resolve()
DATASET_PATH = BASE_DIR / 'dataset'

# Use the configured database if present, otherwise fall back to local SQLite.
DATABASE_URL = os.environ.get('DATABASE_URL')
SQLALCHEMY_DATABASE_URL = DATABASE_URL or f"sqlite:///{DB_PATH.as_posix()}"

# Check if using SQLite for thread safety
if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()