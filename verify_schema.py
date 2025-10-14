"""
Script to verify and align the tickers table schema with the model definition.
This will detect missing columns, extra columns, and optionally drop unwanted columns.
"""
import json
from sqlalchemy import create_engine, inspect, text
from models import Ticker, Base

def load_config(path='config/settings.json'):
    with open(path, 'r') as f:
        return json.load(f)

def get_engine(config):
    pg_cfg = config["postgres"]
    db_url = f"postgresql+psycopg2://{pg_cfg['username']}:{pg_cfg['password']}@{pg_cfg['host']}:{pg_cfg['port']}/{pg_cfg['database']}"
    return create_engine(db_url)

def get_model_columns():
    """Get column names from the SQLAlchemy model."""
    return {col.name: col for col in Ticker.__table__.columns}

def get_table_columns(engine):
    """Get column names from the actual database table."""
    inspector = inspect(engine)
    if 'tickers' not in inspector.get_table_names():
        return {}
    columns = inspector.get_columns('tickers')
    return {col['name']: col for col in columns}

def verify_schema():
    config = load_config()
    engine = get_engine(config)
    
    model_columns = get_model_columns()
    table_columns = get_table_columns(engine)
    
    if not table_columns:
        print("Table 'tickers' does not exist. Creating from model...")
        Base.metadata.create_all(engine)
        print("✓ Table created successfully.")
        return
    
    model_col_names = set(model_columns.keys())
    table_col_names = set(table_columns.keys())
    
    missing_in_table = model_col_names - table_col_names
    extra_in_table = table_col_names - model_col_names
    matching = model_col_names & table_col_names
    
    print("\n=== Schema Verification Report ===\n")
    print(f"Model columns: {len(model_col_names)}")
    print(f"Table columns: {len(table_col_names)}")
    print(f"Matching columns: {len(matching)}")
    
    if missing_in_table:
        print(f"\n⚠ Missing in table (need to add): {sorted(missing_in_table)}")
    
    if extra_in_table:
        print(f"\n⚠ Extra in table (may need to drop): {sorted(extra_in_table)}")
    
    if not missing_in_table and not extra_in_table:
        print("\n✓ Schema is aligned! All columns match.")
        return
    
    # Ask user if they want to fix the schema
    print("\n--- Alignment Options ---")
    if extra_in_table:
        print(f"\nColumns to drop: {sorted(extra_in_table)}")
        response = input("Drop these columns from the database? (yes/no): ").strip().lower()
        if response == 'yes':
            with engine.connect() as conn:
                for col_name in extra_in_table:
                    print(f"Dropping column: {col_name}")
                    conn.execute(text(f'ALTER TABLE tickers DROP COLUMN IF EXISTS "{col_name}"'))
                    conn.commit()
            print("✓ Columns dropped successfully.")
    
    if missing_in_table:
        print(f"\nColumns to add: {sorted(missing_in_table)}")
        response = input("Add these columns to the database? (yes/no): ").strip().lower()
        if response == 'yes':
            for col_name in missing_in_table:
                col = model_columns[col_name]
                col_type = str(col.type)
                nullable = "NULL" if col.nullable else "NOT NULL"
                default = ""
                
                print(f"Adding column: {col_name} ({col_type})")
                with engine.connect() as conn:
                    conn.execute(text(f'ALTER TABLE tickers ADD COLUMN IF NOT EXISTS "{col_name}" {col_type} {nullable}'))
                    conn.commit()
            print("✓ Columns added successfully.")
    
    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_schema()
