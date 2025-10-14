"""
Add is_favorite column to tickers table

This script adds the is_favorite boolean column to the tickers table.
Run this once to update your existing database.

Usage:
    python add_favorites_column.py
"""

import json
from sqlalchemy import create_engine, Boolean, Column, text
from sqlalchemy.orm import sessionmaker

def load_config():
    with open('config/settings.json', 'r') as f:
        return json.load(f)

def main():
    # Load configuration
    config = load_config()
    pg_cfg = config["postgres"]
    db_url = f"postgresql+psycopg2://{pg_cfg['username']}:{pg_cfg['password']}@{pg_cfg['host']}:{pg_cfg['port']}/{pg_cfg['database']}"
    
    # Create engine
    engine = create_engine(db_url)
    
    print("Adding is_favorite column to tickers table...")
    
    with engine.connect() as conn:
        try:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='tickers' AND column_name='is_favorite'
            """))
            
            if result.fetchone():
                print("✓ Column 'is_favorite' already exists!")
            else:
                # Add the column
                conn.execute(text("""
                    ALTER TABLE tickers 
                    ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("✓ Column 'is_favorite' added successfully!")
                
                # Update all existing records to have is_favorite = False
                conn.execute(text("""
                    UPDATE tickers 
                    SET is_favorite = FALSE 
                    WHERE is_favorite IS NULL
                """))
                conn.commit()
                print("✓ Initialized all existing tickers with is_favorite = False")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            conn.rollback()
    
    print("\nDone! You can now use the favorites feature.")

if __name__ == "__main__":
    main()
