import argparse
import json
from datetime import datetime
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_app.models import Ticker, Base

def load_config(path='config/settings.json'):
    with open(path, 'r') as f:
        return json.load(f)

def get_db_session(config):
    pg_cfg = config["postgres"]
    db_url = f"postgresql+psycopg2://{pg_cfg['username']}:{pg_cfg['password']}@{pg_cfg['host']}:{pg_cfg['port']}/{pg_cfg['database']}"
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def fetch_polygon_tickers(config):
    url = f"{config['api']['polygon_base_url']}/v3/reference/tickers"
    params = {
        'market': 'crypto',
        'active': 'true',
        'limit': 1000,
        'sort': 'ticker',
        'order': 'asc',
        'apikey': config['api']['api_key']
    }
    tickers = []
    while True:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        tickers.extend(data.get('results', []))
        next_url = data.get('next_url')
        if not next_url:
            break
        url = next_url
        params = {'apikey': config['api']['api_key']}
    return tickers

def save_tickers_to_db(session, tickers):
    for t in tickers:
        # Skip delisted tickers
        if t.get('delisted_utc'):
            continue
            
        ticker = t.get('ticker', '')
        name = t.get('name', '')
        market = t.get('market', '')
        locale = t.get('locale', '')
        active = t.get('active', False)
        currency_symbol = t.get('currency_symbol', '')
        base_currency_symbol = t.get('base_currency_symbol', '')
        crypto_symbol = ''
        if ticker.startswith('X:') and ticker.endswith('USD'):
            crypto_symbol = ticker.replace('X:', '').replace('USD', '')
        elif '-' in ticker:
            parts = ticker.split('-')
            if len(parts) >= 2:
                crypto_symbol = parts[0]
        row = {
            'ticker': ticker,
            'name': name,
            'crypto_symbol': crypto_symbol,
            'market': market,
            'locale': locale,
            'active': active,
            'is_usd_pair': ticker.endswith('USD') or base_currency_symbol == 'USD',
            'currency_symbol': currency_symbol,
            'base_currency_symbol': base_currency_symbol,
            'market_cap': None,
            'last_trade_timestamp': None,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        ticker_obj = session.query(Ticker).filter_by(ticker=row['ticker']).first()
        if ticker_obj:
            for key, value in row.items():
                setattr(ticker_obj, key, value)
        else:
            ticker_obj = Ticker(**row)
            session.add(ticker_obj)
    session.commit()


def check_already_updated_today(session):
    """Check if any ticker has been updated today."""
    today = datetime.now().strftime('%Y-%m-%d')
    ticker = session.query(Ticker).filter(
        Ticker.last_updated.like(f'{today}%')
    ).first()
    return ticker is not None

def clear_all_tickers(session):
    """Delete all tickers from the database."""
    count = session.query(Ticker).count()
    session.query(Ticker).delete()
    session.commit()
    return count

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Force update all tickers regardless of last update time')
    parser.add_argument('--clear', action='store_true', help='Clear all ticker data from the database')
    args = parser.parse_args()

    config = load_config()
    session = get_db_session(config)
    
    if args.clear:
        count = clear_all_tickers(session)
        print(f'Cleared {count} tickers from the database.')
    elif args.force:
        tickers = fetch_polygon_tickers(config)
        save_tickers_to_db(session, tickers)
        print('Updated all tickers (forced).')
    else:
        if check_already_updated_today(session):
            print('Tickers already updated today. Use --force to update anyway.')
        else:
            tickers = fetch_polygon_tickers(config)
            save_tickers_to_db(session, tickers)
            print('Updated all tickers.')

if __name__ == "__main__":
    main()
