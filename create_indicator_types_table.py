"""
Create indicator_types table and add indicator_type_id column to indicators table

This script creates the indicator_types table and adds the indicator_type_id foreign key
to the indicators table.

Usage:
    python create_indicator_types_table.py
"""

import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask_app.models import Base, IndicatorType

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
    
    print("Creating indicator_types table...")
    
    try:
        # Check if table already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public' AND table_name='indicator_types'
            """))
            
            if result.fetchone():
                print("✓ Table 'indicator_types' already exists!")
            else:
                # Create the table
                Base.metadata.create_all(engine, tables=[IndicatorType.__table__])
                print("✓ Table 'indicator_types' created successfully!")
        
        # Check if indicator_type_id column exists in indicators table
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='indicators' AND column_name='indicator_type_id'
            """))
            
            if result.fetchone():
                print("✓ Column 'indicator_type_id' already exists in indicators table!")
            else:
                # Add the column
                print("Adding indicator_type_id column to indicators table...")
                conn.execute(text("""
                    ALTER TABLE indicators 
                    ADD COLUMN indicator_type_id INTEGER REFERENCES indicator_types(id)
                """))
                conn.commit()
                print("✓ Column 'indicator_type_id' added successfully!")
        
        # Insert default indicator types
        print("\nAdding default indicator types...")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        default_types = [
            {'name': 'Technical', 'description': 'Technical analysis indicators (RSI, MACD, etc.)', 'color': '#3B82F6'},
            {'name': 'Sentiment', 'description': 'Market sentiment and fear/greed indicators', 'color': '#8B5CF6'},
            {'name': 'On-Chain', 'description': 'Blockchain and on-chain metrics', 'color': '#10B981'},
            {'name': 'Fundamental', 'description': 'Fundamental analysis indicators', 'color': '#F59E0B'},
            {'name': 'Macro', 'description': 'Macroeconomic indicators', 'color': '#EF4444'},
            {'name': 'Custom', 'description': 'Custom indicators', 'color': '#6B7280'},
        ]
        
        from datetime import datetime
        added = 0
        
        for type_data in default_types:
            existing = session.query(IndicatorType).filter_by(name=type_data['name']).first()
            if not existing:
                indicator_type = IndicatorType(
                    name=type_data['name'],
                    description=type_data['description'],
                    color=type_data['color'],
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                session.add(indicator_type)
                added += 1
        
        session.commit()
        session.close()
        
        if added > 0:
            print(f"✓ Added {added} default indicator types!")
        else:
            print("✓ Default indicator types already exist!")
                
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\nDone! You can now use indicator types in the application.")

if __name__ == "__main__":
    main()
