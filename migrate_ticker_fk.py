"""
Migration script to convert TickerData from using ticker string to ticker_id foreign key.

This script:
1. Adds a new ticker_id column to ticker_data
2. Populates ticker_id based on the ticker string
3. Drops the old ticker column
4. Renames ticker_id to ticker_id (if needed)
5. Updates the unique constraint
"""
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def load_config(path='config/settings.json'):
    with open(path, 'r') as f:
        return json.load(f)

def get_db_session(config):
    pg_cfg = config["postgres"]
    db_url = f"postgresql+psycopg2://{pg_cfg['username']}:{pg_cfg['password']}@{pg_cfg['host']}:{pg_cfg['port']}/{pg_cfg['database']}"
    engine = create_engine(db_url)
    return sessionmaker(bind=engine)(), engine

def migrate():
    config = load_config()
    session, engine = get_db_session(config)
    
    print("Starting migration: ticker string -> ticker_id foreign key\n")
    
    try:
        # Step 1: Add ticker_id column
        print("Step 1: Adding ticker_id column...")
        session.execute(text("""
            ALTER TABLE ticker_data 
            ADD COLUMN IF NOT EXISTS ticker_id INTEGER;
        """))
        session.commit()
        print("✓ ticker_id column added\n")
        
        # Step 2: Populate ticker_id from ticker string
        print("Step 2: Populating ticker_id from ticker strings...")
        result = session.execute(text("""
            UPDATE ticker_data td
            SET ticker_id = t.id
            FROM tickers t
            WHERE td.ticker = t.ticker
            AND td.ticker_id IS NULL;
        """))
        session.commit()
        print(f"✓ Updated {result.rowcount} rows\n")
        
        # Step 3: Check for orphaned records (ticker_data without matching ticker)
        print("Step 3: Checking for orphaned records...")
        orphaned = session.execute(text("""
            SELECT COUNT(*) FROM ticker_data WHERE ticker_id IS NULL;
        """)).scalar()
        
        if orphaned > 0:
            print(f"⚠ WARNING: Found {orphaned} orphaned records (no matching ticker)")
            print("  These will be deleted. Press Enter to continue or Ctrl+C to abort...")
            input()
            
            session.execute(text("""
                DELETE FROM ticker_data WHERE ticker_id IS NULL;
            """))
            session.commit()
            print(f"✓ Deleted {orphaned} orphaned records\n")
        else:
            print("✓ No orphaned records found\n")
        
        # Step 4: Drop the old unique constraint
        print("Step 4: Dropping old unique constraint...")
        session.execute(text("""
            ALTER TABLE ticker_data 
            DROP CONSTRAINT IF EXISTS _ticker_date_uc;
        """))
        session.commit()
        print("✓ Old constraint dropped\n")
        
        # Step 5: Make ticker_id NOT NULL
        print("Step 5: Making ticker_id NOT NULL...")
        session.execute(text("""
            ALTER TABLE ticker_data 
            ALTER COLUMN ticker_id SET NOT NULL;
        """))
        session.commit()
        print("✓ ticker_id is now NOT NULL\n")
        
        # Step 6: Add foreign key constraint
        print("Step 6: Adding foreign key constraint...")
        session.execute(text("""
            ALTER TABLE ticker_data 
            ADD CONSTRAINT fk_ticker_data_ticker_id 
            FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE;
        """))
        session.commit()
        print("✓ Foreign key constraint added\n")
        
        # Step 7: Add index on ticker_id
        print("Step 7: Adding index on ticker_id...")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_ticker_data_ticker_id ON ticker_data(ticker_id);
        """))
        session.commit()
        print("✓ Index added\n")
        
        # Step 8: Create new unique constraint
        print("Step 8: Creating new unique constraint on (ticker_id, date)...")
        session.execute(text("""
            ALTER TABLE ticker_data 
            ADD CONSTRAINT _ticker_date_uc UNIQUE (ticker_id, date);
        """))
        session.commit()
        print("✓ New unique constraint added\n")
        
        # Step 9: Drop old ticker column and its index
        print("Step 9: Dropping old ticker column and index...")
        session.execute(text("""
            DROP INDEX IF EXISTS ix_ticker_data_ticker;
        """))
        session.execute(text("""
            ALTER TABLE ticker_data DROP COLUMN IF EXISTS ticker;
        """))
        session.commit()
        print("✓ Old ticker column and index dropped\n")
        
        # Verify migration
        print("Step 10: Verifying migration...")
        count = session.execute(text("""
            SELECT COUNT(*) FROM ticker_data;
        """)).scalar()
        print(f"✓ ticker_data has {count} records\n")
        
        # Show sample of migrated data
        print("Sample of migrated data:")
        sample = session.execute(text("""
            SELECT td.id, t.ticker, td.date, td.close 
            FROM ticker_data td
            JOIN tickers t ON t.id = td.ticker_id
            ORDER BY td.date DESC
            LIMIT 5;
        """))
        for row in sample:
            print(f"  ID: {row[0]}, Ticker: {row[1]}, Date: {row[2]}, Close: {row[3]}")
        
        print("\n✅ Migration completed successfully!")
        print("\nIMPORTANT: Update your application code to use ticker_id instead of ticker string.")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Migration failed: {e}")
        print("\nRolling back changes...")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("="*60)
    print("TICKER DATA FOREIGN KEY MIGRATION")
    print("="*60)
    print("\nThis will modify the ticker_data table to use a foreign key")
    print("relationship to the tickers table instead of storing ticker strings.")
    print("\n⚠ BACKUP YOUR DATABASE BEFORE PROCEEDING ⚠")
    print("\nPress Enter to continue or Ctrl+C to abort...")
    input()
    
    migrate()
