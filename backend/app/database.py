from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'receipts.db')
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'greenhouse-gas-emissions-per-kilogram-of-food-product.csv')

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()