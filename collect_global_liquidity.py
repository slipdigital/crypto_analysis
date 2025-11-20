"""
Global Liquidity Data Collector

Fetches global liquidity data from the Federal Reserve Economic Data (FRED) API.
This includes M2 money supply, central bank balance sheets, and other monetary aggregates.

Key Series:
- M2SL: US M2 Money Supply
- WALCL: Federal Reserve Total Assets
- ECBASSETSW: European Central Bank Assets
- JPNASSETS: Bank of Japan Total Assets
- PBOCASSETSW: People's Bank of China Assets

Usage:
    python collect_global_liquidity.py              # Collect all series
    python collect_global_liquidity.py --series M2SL WALCL  # Specific series
    python collect_global_liquidity.py --days 90    # Last 90 days only
"""

import requests
import json
import argparse
from datetime import datetime, timedelta
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from flask_app.models import Base, GlobalLiquidity

# FRED API Configuration
FRED_API_BASE = "https://api.stlouisfed.org/fred/series"

# Key liquidity series to track
DEFAULT_SERIES = {
    "M2SL": {
        "name": "US M2 Money Supply",
        "description": "M2 includes cash, checking deposits, savings deposits, and money market securities",
        "units": "Billions of Dollars",
        "frequency": "Monthly"
    },
    "WALCL": {
        "name": "Federal Reserve Total Assets",
        "description": "All assets held by the Federal Reserve",
        "units": "Billions of Dollars",
        "frequency": "Weekly"
    },
    "BOGMBASE": {
        "name": "US Monetary Base",
        "description": "Total currency in circulation plus bank reserves",
        "units": "Billions of Dollars",
        "frequency": "Monthly"
    },
    "ECBASSETSW": {
        "name": "European Central Bank Assets",
        "description": "Total assets of the ECB",
        "units": "Billions of Euros",
        "frequency": "Weekly"
    },
    "JPNASSETS": {
        "name": "Bank of Japan Total Assets",
        "description": "Total assets of the Bank of Japan",
        "units": "Billions of Yen",
        "frequency": "Monthly"
    }
}


def load_config():
    """Load configuration from settings.json"""
    with open('config/settings.json', 'r') as f:
        return json.load(f)


def get_db_engine(config):
    """Create database engine from config"""
    pg = config['postgres']
    db_url = f"postgresql://{pg['username']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"
    return create_engine(db_url)


def fetch_fred_data(series_id, start_date=None, end_date=None, api_key=None):
    """
    Fetch data for a specific FRED series
    
    Args:
        series_id: FRED series identifier
        start_date: Start date (YYYY-MM-DD) or None for all available
        end_date: End date (YYYY-MM-DD) or None for latest
        api_key: FRED API key
    
    Returns:
        List of observations with date and value
    """
    url = f"{FRED_API_BASE}/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json"
    }
    
    if start_date:
        params["observation_start"] = start_date
    if end_date:
        params["observation_end"] = end_date
    
    try:
        print(f"Fetching {series_id}...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "observations" in data:
            observations = []
            for obs in data["observations"]:
                # Skip missing values (marked as ".")
                if obs["value"] != ".":
                    observations.append({
                        "date": obs["date"],
                        "value": float(obs["value"])
                    })
            
            print(f"  Retrieved {len(observations)} observations for {series_id}")
            return observations
        else:
            print(f"  No observations found for {series_id}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"  Error fetching {series_id}: {e}")
        return []


def save_liquidity_data(session, series_id, series_info, observations):
    """
    Save liquidity data to database
    
    Args:
        session: SQLAlchemy session
        series_id: FRED series identifier
        series_info: Dictionary with series metadata
        observations: List of date/value observations
    
    Returns:
        Tuple of (inserted_count, updated_count)
    """
    inserted = 0
    updated = 0
    
    for obs in observations:
        try:
            # Try to insert new record
            record = GlobalLiquidity(
                series_id=series_id,
                series_name=series_info["name"],
                date=datetime.strptime(obs["date"], "%Y-%m-%d").date(),
                value=obs["value"],
                units=series_info["units"],
                frequency=series_info["frequency"],
                collected_at=datetime.now().isoformat()
            )
            session.add(record)
            session.commit()
            inserted += 1
            
        except IntegrityError:
            # Record exists, update it
            session.rollback()
            existing = session.query(GlobalLiquidity).filter(
                and_(
                    GlobalLiquidity.series_id == series_id,
                    GlobalLiquidity.date == datetime.strptime(obs["date"], "%Y-%m-%d").date()
                )
            ).first()
            
            if existing:
                existing.value = obs["value"]
                existing.series_name = series_info["name"]
                existing.units = series_info["units"]
                existing.frequency = series_info["frequency"]
                existing.collected_at = datetime.now().isoformat()
                session.commit()
                updated += 1
    
    return inserted, updated


def main():
    parser = argparse.ArgumentParser(
        description="Collect global liquidity data from FRED API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python collect_global_liquidity.py                    # Collect all default series
  python collect_global_liquidity.py --series M2SL      # Collect only M2
  python collect_global_liquidity.py --days 90          # Last 90 days only
  python collect_global_liquidity.py --list             # List available series
        """
    )
    
    parser.add_argument(
        '--series',
        nargs='+',
        help='Specific FRED series IDs to collect (default: all configured series)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        help='Number of days of historical data to fetch (default: all available)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available series and exit'
    )
    
    parser.add_argument(
        '--api-key',
        help='FRED API key (if not using default)'
    )
    
    args = parser.parse_args()
    
    # List series and exit
    if args.list:
        print("\nAvailable Global Liquidity Series:")
        print("=" * 80)
        for series_id, info in DEFAULT_SERIES.items():
            print(f"\n{series_id}: {info['name']}")
            print(f"  Description: {info['description']}")
            print(f"  Units: {info['units']}")
            print(f"  Frequency: {info['frequency']}")
        print("\n" + "=" * 80)
        return
    
    # Load configuration
    config = load_config()
    
    # Get API key from config or command line
    api_key = args.api_key or config.get('fred', {}).get('api_key')
    if not api_key or api_key == "YOUR_FRED_API_KEY_HERE":
        print("\nError: FRED API key not configured!")
        print("Please get a free API key from: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("Then add it to config/settings.json under 'fred' -> 'api_key'")
        print("Or use --api-key argument")
        return
    
    # Setup database
    engine = get_db_engine(config)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Determine which series to collect
    if args.series:
        series_to_collect = {sid: DEFAULT_SERIES.get(sid, {"name": sid, "units": "Unknown", "frequency": "Unknown"}) 
                           for sid in args.series}
    else:
        series_to_collect = DEFAULT_SERIES
    
    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = None
    if args.days:
        start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    # Collect data for each series
    print(f"\nCollecting global liquidity data...")
    print(f"Date range: {start_date or 'All available'} to {end_date}")
    print(f"Series: {', '.join(series_to_collect.keys())}")
    print("=" * 80)
    
    total_inserted = 0
    total_updated = 0
    
    for series_id, series_info in series_to_collect.items():
        observations = fetch_fred_data(series_id, start_date, end_date, api_key)
        
        if observations:
            inserted, updated = save_liquidity_data(session, series_id, series_info, observations)
            total_inserted += inserted
            total_updated += updated
            print(f"  {series_id}: Inserted {inserted}, Updated {updated}")
        else:
            print(f"  {series_id}: No data to save")
    
    session.close()
    
    print("=" * 80)
    print(f"\nCollection complete!")
    print(f"Total records inserted: {total_inserted}")
    print(f"Total records updated: {total_updated}")
    
    # Show latest values
    session = Session()
    print("\nLatest values:")
    print("-" * 80)
    for series_id in series_to_collect.keys():
        latest = session.query(GlobalLiquidity).filter(
            GlobalLiquidity.series_id == series_id
        ).order_by(GlobalLiquidity.date.desc()).first()
        
        if latest:
            print(f"{series_id:12} ({latest.date}): {latest.value:,.2f} {latest.units}")
    
    session.close()


if __name__ == "__main__":
    main()
