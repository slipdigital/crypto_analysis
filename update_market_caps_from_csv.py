"""
Script to update market cap values from a CSV file.
Matches tickers by name or crypto symbol and updates the market_cap field.
"""
import csv
import json
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Ticker

def load_config(path='config/settings.json'):
    with open(path, 'r') as f:
        return json.load(f)

def get_db_session(config):
    pg_cfg = config["postgres"]
    db_url = f"postgresql+psycopg2://{pg_cfg['username']}:{pg_cfg['password']}@{pg_cfg['host']}:{pg_cfg['port']}/{pg_cfg['database']}"
    engine = create_engine(db_url)
    return sessionmaker(bind=engine)()

def parse_market_cap(market_cap_str):
    """Parse market cap string like '$2,217,478,194,907' or '$12.5B' to float."""
    if not market_cap_str or market_cap_str == '-':
        return None
    
    # Remove $ and commas
    cleaned = market_cap_str.replace('$', '').replace(',', '').strip()
    
    # Handle B (billions) and M (millions) suffixes
    multiplier = 1
    if cleaned.endswith('B'):
        multiplier = 1_000_000_000
        cleaned = cleaned[:-1]
    elif cleaned.endswith('M'):
        multiplier = 1_000_000
        cleaned = cleaned[:-1]
    elif cleaned.endswith('K'):
        multiplier = 1_000
        cleaned = cleaned[:-1]
    
    try:
        return float(cleaned) * multiplier
    except ValueError:
        return None

def extract_crypto_symbol(name_col):
    """Extract crypto symbol from name column like 'BitcoinBTCBuy'."""
    # Pattern to match capital letters before 'Buy' or at the end
    match = re.search(r'([A-Z]{2,10})(?:Buy)?$', name_col)
    if match:
        return match.group(1)
    return None

def update_market_caps(csv_file_path):
    """Update market caps from CSV file."""
    config = load_config()
    session = get_db_session(config)
    
    updated_count = 0
    not_found_count = 0
    skipped_count = 0
    
    print(f"\nReading market cap data from: {csv_file_path}\n")
    
    with open(csv_file_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            name = row.get('Name', '').strip()
            market_cap_str = row.get('Market Cap', '').strip()
            
            if not name or not market_cap_str:
                skipped_count += 1
                continue
            
            # Extract crypto symbol from name
            crypto_symbol = extract_crypto_symbol(name)
            if not crypto_symbol:
                print(f"⚠ Could not extract symbol from: {name}")
                skipped_count += 1
                continue
            
            # Parse market cap value
            market_cap = parse_market_cap(market_cap_str)
            if market_cap is None:
                print(f"⚠ Could not parse market cap for {crypto_symbol}: {market_cap_str}")
                skipped_count += 1
                continue
            
            # Try to find matching ticker by crypto_symbol
            ticker = session.query(Ticker).filter(
                Ticker.crypto_symbol == crypto_symbol
            ).first()
            
            if ticker:
                # Update market cap
                old_value = ticker.market_cap
                ticker.market_cap = market_cap
                session.commit()
                
                print(f"✓ Updated {ticker.ticker} ({crypto_symbol}): "
                      f"${old_value:,.2f} → ${market_cap:,.2f}" if old_value else 
                      f"✓ Updated {ticker.ticker} ({crypto_symbol}): ${market_cap:,.2f}")
                updated_count += 1
            else:
                print(f"✗ Ticker not found for: {crypto_symbol} ({name})")
                not_found_count += 1
    
    print(f"\n=== Update Summary ===")
    print(f"Updated: {updated_count}")
    print(f"Not found: {not_found_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Total: {updated_count + not_found_count + skipped_count}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update ticker market caps from CSV file')
    parser.add_argument('--file', type=str, default='data/market_cap_20251014.csv',
                        help='Path to CSV file with market cap data')
    args = parser.parse_args()
    
    update_market_caps(args.file)
