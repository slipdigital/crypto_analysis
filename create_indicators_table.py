"""
Create indicators table

This script creates the indicators table in the database.

Usage:
    python create_indicators_table.py
"""

import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask_app.models import Base, Indicator

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
    
    print("Creating indicators table...")
    
    try:
        # Check if table already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' AND table_name='indicators'
            """))
            
            if result.fetchone():
                print("✓ Table 'indicators' already exists!")
            else:
                # Create the table
                Base.metadata.create_all(engine, tables=[Indicator.__table__])
                print("✓ Table 'indicators' created successfully!")
                
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nDone! You can now use the indicators feature.")

if __name__ == "__main__":
    main()
