"""
Add url column to indicators table

This script adds an optional url field to the indicators table for storing
reference URLs or documentation links.

Usage:
    python add_indicator_url_column.py
"""

import json
from sqlalchemy import create_engine, text

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
    
    print("Adding url column to indicators table...")
    
    try:
        # Check if column already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='indicators' AND column_name='url'
            """))
            
            if result.fetchone():
                print("✓ Column 'url' already exists in indicators table!")
            else:
                # Add the column
                conn.execute(text("""
                    ALTER TABLE indicators 
                    ADD COLUMN url VARCHAR(500)
                """))
                conn.commit()
                print("✓ Column 'url' added successfully!")
                
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nDone! You can now add URLs to indicators.")

if __name__ == "__main__":
    main()
