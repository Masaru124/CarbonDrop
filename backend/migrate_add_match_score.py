"""
Migration script to add match_score and co2_per_unit columns to items table.
"""

from sqlalchemy import create_engine, text
import os

# Use PostgreSQL database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_AHFsyU0CI9TX@ep-cool-lab-adm9rvmd-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

def migrate():
    """Add match_score and co2_per_unit columns to items table."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # Check if match_score column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='items' AND column_name='match_score'
            """))
            
            if not result.fetchone():
                print("Adding match_score column to items table...")
                connection.execute(text("""
                    ALTER TABLE items ADD COLUMN match_score INTEGER
                """))
                connection.commit()
                print("✅ match_score column added successfully")
            else:
                print("✓ match_score column already exists")
            
            # Check if co2_per_unit column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='items' AND column_name='co2_per_unit'
            """))
            
            if not result.fetchone():
                print("Adding co2_per_unit column to items table...")
                connection.execute(text("""
                    ALTER TABLE items ADD COLUMN co2_per_unit NUMERIC(10, 4)
                """))
                connection.commit()
                print("✅ co2_per_unit column added successfully")
            else:
                print("✓ co2_per_unit column already exists")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    print("\n✅ Migration completed successfully!")
    return True

if __name__ == "__main__":
    migrate()
