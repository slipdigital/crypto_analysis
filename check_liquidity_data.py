"""
Global Liquidity Data Status Checker

Quick utility to check what global liquidity data you have collected.
Shows latest values, date ranges, and data quality.

Usage:
    python check_liquidity_data.py
"""

import json
from datetime import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models import GlobalLiquidity


def load_config():
    """Load configuration from settings.json"""
    with open('config/settings.json', 'r') as f:
        return json.load(f)


def get_db_engine(config):
    """Create database engine from config"""
    pg = config['postgres']
    db_url = f"postgresql://{pg['username']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"
    return create_engine(db_url)


def main():
    # Load configuration
    config = load_config()
    
    # Setup database
    engine = get_db_engine(config)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if table exists
    try:
        total_records = session.query(GlobalLiquidity).count()
    except Exception as e:
        print("\n❌ Global liquidity data not yet collected!")
        print(f"Error: {e}")
        print("\nRun this command to start collecting data:")
        print(r"  .\.venv\Scripts\python.exe collect_global_liquidity.py")
        return
    
    if total_records == 0:
        print("\n⚠️  Global liquidity table exists but is empty.")
        print("\nRun this command to collect data:")
        print(r"  .\.venv\Scripts\python.exe collect_global_liquidity.py")
        return
    
    # Get all series
    series_list = session.query(GlobalLiquidity.series_id).distinct().all()
    series_ids = [s[0] for s in series_list]
    
    print("\n" + "=" * 80)
    print("GLOBAL LIQUIDITY DATA STATUS")
    print("=" * 80)
    print(f"\nTotal records: {total_records:,}")
    print(f"Series tracked: {len(series_ids)}")
    print("\n" + "-" * 80)
    
    # Analyze each series
    for series_id in sorted(series_ids):
        # Get series info
        latest = session.query(GlobalLiquidity).filter(
            GlobalLiquidity.series_id == series_id
        ).order_by(GlobalLiquidity.date.desc()).first()
        
        oldest = session.query(GlobalLiquidity).filter(
            GlobalLiquidity.series_id == series_id
        ).order_by(GlobalLiquidity.date.asc()).first()
        
        count = session.query(GlobalLiquidity).filter(
            GlobalLiquidity.series_id == series_id
        ).count()
        
        # Calculate days since last update
        if latest:
            days_since_update = (datetime.now().date() - latest.date).days
            status = "✅" if days_since_update <= 7 else "⚠️" if days_since_update <= 30 else "❌"
        else:
            days_since_update = None
            status = "❌"
        
        print(f"\n{status} {series_id}: {latest.series_name if latest else 'Unknown'}")
        print(f"   Records: {count:,}")
        print(f"   Date range: {oldest.date if oldest else 'N/A'} to {latest.date if latest else 'N/A'}")
        
        if latest:
            print(f"   Latest value: {latest.value:,.2f} {latest.units}")
            print(f"   Last updated: {days_since_update} days ago")
            
            # Show trend (compare to 30 days ago)
            thirty_days_ago = session.query(GlobalLiquidity).filter(
                GlobalLiquidity.series_id == series_id,
                GlobalLiquidity.date <= latest.date
            ).order_by(GlobalLiquidity.date.desc()).offset(30).first()
            
            if thirty_days_ago:
                change = latest.value - thirty_days_ago.value
                pct_change = (change / thirty_days_ago.value) * 100
                trend = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                print(f"   30-day change: {trend} {change:+,.2f} ({pct_change:+.2f}%)")
    
    print("\n" + "=" * 80)
    
    # Show update recommendation
    max_days_old = max(
        (datetime.now().date() - session.query(GlobalLiquidity).filter(
            GlobalLiquidity.series_id == sid
        ).order_by(GlobalLiquidity.date.desc()).first().date).days
        for sid in series_ids
    )
    
    print("\nRECOMMENDATIONS:")
    print("-" * 80)
    
    if max_days_old <= 7:
        print("✅ All data is current (updated within 7 days)")
    elif max_days_old <= 30:
        print("⚠️  Some data is getting stale. Consider running an update:")
        print(r"   .\.venv\Scripts\python.exe collect_global_liquidity.py --days 30")
    else:
        print("❌ Data is outdated. Run an update:")
        print(r"   .\.venv\Scripts\python.exe collect_global_liquidity.py --days 90")
    
    # Calculate total global liquidity (USD only)
    print("\n" + "-" * 80)
    print("AGGREGATE GLOBAL LIQUIDITY (USD-denominated only):")
    print("-" * 80)
    
    usd_series = ['M2SL', 'WALCL', 'BOGMBASE']
    total_usd = 0
    
    for series_id in usd_series:
        latest = session.query(GlobalLiquidity).filter(
            GlobalLiquidity.series_id == series_id
        ).order_by(GlobalLiquidity.date.desc()).first()
        
        if latest and 'Dollar' in latest.units:
            total_usd += latest.value
            print(f"{series_id:12} {latest.value:15,.2f} B")
    
    print(f"{'TOTAL':12} {total_usd:15,.2f} B (${total_usd/1000:.2f}T)")
    
    print("\nNote: For true global liquidity, you'd need to convert EUR and JPY series")
    print("      using current exchange rates and add them to this total.")
    
    print("\n" + "=" * 80 + "\n")
    
    session.close()


if __name__ == "__main__":
    main()
