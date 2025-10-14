"""
Create indicator_data table

This script creates the indicator_data table in the database.

Usage:
    python create_indicator_data_table.py
"""

import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, IndicatorData

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
    
    print("Creating indicator_data table...")
    
    try:
        # Check if table already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' AND table_name='indicator_data'
            """))
            
            if result.fetchone():
                print("✓ Table 'indicator_data' already exists!")
            else:
                # Create the table
                Base.metadata.create_all(engine, tables=[IndicatorData.__table__])
                print("✓ Table 'indicator_data' created successfully!")
                
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nDone! You can now use the indicator data feature.")

if __name__ == "__main__":
    main()
