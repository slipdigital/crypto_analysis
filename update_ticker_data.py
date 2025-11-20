"""
Script to collect historical daily price data for all tickers from Polygon API.
Checks existing data and only fetches missing dates.
"""
import argparse
import json
from datetime import datetime, timedelta
import time
import requests
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask_app.models import Ticker, TickerData, Base

def load_config(path='config/settings.json'):
    with open(path, 'r') as f:
        return json.load(f)

def get_db_session(config):
    pg_cfg = config["postgres"]
    db_url = f"postgresql+psycopg2://{pg_cfg['username']}:{pg_cfg['password']}@{pg_cfg['host']}:{pg_cfg['port']}/{pg_cfg['database']}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def get_date_range_for_ticker(session, ticker_obj):
    """Get the date range that needs to be collected for a ticker."""
    # Get the latest date we have data for this ticker (using ticker_id)
    latest = session.query(func.max(TickerData.date)).filter(
        TickerData.ticker_id == ticker_obj.id
    ).scalar()
    
    # Get earliest available data date (2 years ago as a safe default for crypto)
    earliest_available = datetime.now() - timedelta(days=730)
    # Only update up to yesterday (today's data is incomplete during trading)
    yesterday = (datetime.now() - timedelta(days=1)).date()
    
    if latest:
        # We have some data, fetch from day after latest to yesterday
        start_date = latest + timedelta(days=1)
        if start_date > yesterday:
            return None, None  # Already up to date
        return start_date, yesterday
    else:
        # No data yet, fetch all available history up to yesterday
        return earliest_available.date(), yesterday

def fetch_daily_data(config, ticker, from_date, to_date):
    """Fetch daily aggregates from Polygon API."""
    url = f"{config['api']['polygon_base_url']}/v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}"
    params = {
        'adjusted': 'true',
        'sort': 'asc',
        'limit': 50000,
        'apiKey': config['api']['api_key']
    }
    
    try:
        resp = requests.get(url, params=params, timeout=config['api']['timeout'])
        resp.raise_for_status()
        data = resp.json()
        
        if data.get('status') == 'OK' and data.get('results'):
            return data['results']
        return []
    except Exception as e:
        print(f"  Error fetching data for {ticker}: {e}")
        return []

def save_ticker_data(session, ticker_obj, daily_data):
    """Save daily price data to database."""
    collected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    saved_count = 0
    
    for bar in daily_data:
        # Convert timestamp (milliseconds) to date
        date = datetime.fromtimestamp(bar['t'] / 1000).date()
        
        ticker_data = TickerData(
            ticker_id=ticker_obj.id,
            date=date,
            open=bar.get('o'),
            high=bar.get('h'),
            low=bar.get('l'),
            close=bar.get('c'),
            volume=bar.get('v'),
            vwap=bar.get('vw'),
            transactions=bar.get('n'),
            collected_at=collected_at
        )
        
        try:
            session.add(ticker_data)
            session.commit()
            saved_count += 1
        except IntegrityError:
            # Duplicate entry, skip
            session.rollback()
            continue
    
    return saved_count

def process_ticker(session, config, ticker_obj, rate_limit_delay):
    """Process a single ticker to collect its historical data."""
    ticker_symbol = ticker_obj.ticker
    
    # Check what date range we need (pass ticker_obj instead of ticker string)
    from_date, to_date = get_date_range_for_ticker(session, ticker_obj)
    
    if not from_date or not to_date:
        print(f"✓ {ticker_symbol}: Already up to date")
        return 0
    
    print(f"→ {ticker_symbol}: Fetching data from {from_date} to {to_date}")
    
    # Fetch data from Polygon (still uses ticker symbol for API call)
    daily_data = fetch_daily_data(config, ticker_symbol, from_date, to_date)
    
    if not daily_data:
        print(f"  {ticker_symbol}: No data available")
        return 0
    
    # Save to database (pass ticker_obj instead of ticker string)
    saved_count = save_ticker_data(session, ticker_obj, daily_data)
    print(f"  {ticker_symbol}: Saved {saved_count} records")
    
    # Rate limiting for basic tier (5 requests per minute)
    time.sleep(rate_limit_delay)
    
    return saved_count

def main():
    parser = argparse.ArgumentParser(description='Update ticker historical price data from Polygon API')
    parser.add_argument('--ticker', type=str, help='Process only a specific ticker')
    parser.add_argument('--limit', type=int, help='Limit number of tickers to process')
    args = parser.parse_args()
    
    config = load_config()
    session = get_db_session(config)
    
    # Get rate limit delay (basic tier: 5 requests per minute = 12 seconds between requests)
    rate_limit_delay = config['api'].get('rate_limit_delay', 12)
    
    # Get tickers to process
    query = session.query(Ticker).filter(Ticker.active == True)
    
    if args.ticker:
        query = query.filter(Ticker.ticker == args.ticker)
    
    if args.limit:
        query = query.limit(args.limit)
    
    tickers = query.all()
    
    print(f"\n=== Processing {len(tickers)} tickers ===\n")
    
    total_saved = 0
    for i, ticker_obj in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] ", end="")
        saved = process_ticker(session, config, ticker_obj, rate_limit_delay)
        total_saved += saved
    
    print(f"\n=== Complete: Saved {total_saved} total records ===\n")

if __name__ == "__main__":
    main()
