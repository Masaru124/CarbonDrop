"""
SQLite migration script to add match_score and co2_per_unit columns to items table.
"""

from sqlalchemy import create_engine, text
import os

# Use local SQLite database
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, '..', 'receipts.db')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

def migrate():
    """Add match_score and co2_per_unit columns to items table."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # SQLite doesn't have information_schema, so we try to add the columns
            # If they already exist, the ALTER TABLE will fail, which we catch
            
            try:
                print("Adding match_score column to items table...")
                connection.execute(text("""
                    ALTER TABLE items ADD COLUMN match_score INTEGER
                """))
                connection.commit()
                print("✅ match_score column added successfully")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print("✓ match_score column already exists")
                else:
                    print(f"Error adding match_score: {e}")
            
            try:
                print("Adding co2_per_unit column to items table...")
                connection.execute(text("""
                    ALTER TABLE items ADD COLUMN co2_per_unit REAL
                """))
                connection.commit()
                print("✅ co2_per_unit column added successfully")
            except Exception as e:
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print("✓ co2_per_unit column already exists")
                else:
                    print(f"Error adding co2_per_unit: {e}")
                    
        except Exception as e:
            print(f"Migration error: {e}")
            raise

if __name__ == "__main__":
    print(f"Running SQLite migration on: {SQLALCHEMY_DATABASE_URL}")
    migrate()
    print("Migration complete!")
