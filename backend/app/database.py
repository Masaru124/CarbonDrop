from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Use the comprehensive multi-domain emission dataset
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'comprehensive_emissions.csv')

# Fallback to enhanced dataset if comprehensive one doesn't exist
FALLBACK_DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'defra_enhanced_emissions.csv')

# Use PostgreSQL database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_AHFsyU0CI9TX@ep-cool-lab-adm9rvmd-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
