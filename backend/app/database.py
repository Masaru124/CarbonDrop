from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'receipts.db')
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'greenhouse-gas-emissions-per-kilogram-of-food-product.csv')

# DATABASE_URL environment variable is required
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

SQLALCHEMY_DATABASE_URL = DATABASE_URL

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