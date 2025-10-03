"""
Example Usage Script for Cryptocurrency Data Collection System
Demonstrates how to use the various components of the system
"""

import os
import sys
import json
from datetime import datetime
from backtest.crypto_collector import CryptoDataCollector
from dashboard.data_utils import CryptoDataUtils
from scheduler import CryptoScheduler


def demo_basic_collection():
    """Demonstrate basic data collection"""
    print("=" * 60)
    print("DEMO: Basic Data Collection")
    print("=" * 60)
    
    try:
        # Initialize collector
        collector = CryptoDataCollector()
        
        # Get cryptocurrency tickers (smaller sample for demo)
        print("Fetching cryptocurrency tickers...")
        crypto_tickers = collector.get_crypto_tickers()
        
        if crypto_tickers:
            print(f"Successfully fetched {len(crypto_tickers)} cryptocurrency tickers:")
            for i, ticker in enumerate(crypto_tickers[:5], 1):  # Show first 5
                print(f"  {i}. {ticker}")
            
            # Get details and prices for demo
            demo_data = []
            for ticker in crypto_tickers[:3]:  # Process first 3 for demo
                details = collector.get_ticker_details(ticker)
                price_data = collector.get_current_price(ticker)
                if details and price_data:
                    demo_data.append({
                        'ticker': ticker,
                        'details': details,
                        'price_data': price_data
                    })
            
            if demo_data:
                # Save a sample snapshot
                collector.save_daily_snapshot_to_csv(demo_data)
                print("\nDaily snapshot saved successfully!")
                
                # Get historical data for first ticker
                first_ticker = demo_data[0]['ticker']
                ticker_name = demo_data[0]['details'].get('name', first_ticker)
                print(f"\nFetching historical data for {ticker_name} ({first_ticker})...")
                
                historical_data = collector.get_historical_data(first_ticker, days=30)  # Last 30 days for demo
                if historical_data:
                    collector.save_historical_data_to_csv(first_ticker, demo_data[0]['details'], historical_data)
                    print(f"Historical data for {ticker_name} saved successfully!")
        
        print("\n✅ Basic collection demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in basic collection demo: {e}")


def demo_data_analysis():
    """Demonstrate data analysis capabilities"""
    print("\n" + "=" * 60)
    print("DEMO: Data Analysis")
    print("=" * 60)
    
    try:
        utils = CryptoDataUtils()
        
        # Generate summary report
        print("Generating data summary report...")
        report = utils.generate_summary_report()
        
        print(f"📊 Data Summary:")
        print(f"  • Total cryptocurrencies: {report['cryptocurrencies']['total_count']}")
        print(f"  • Total snapshots: {report['snapshots']['total_count']}")
        
        if report['cryptocurrencies']['list']:
            print(f"  • Available cryptocurrencies: {', '.join(report['cryptocurrencies']['list'][:5])}...")
        
        if report['snapshots']['date_range']['earliest']:
            print(f"  • Date range: {report['snapshots']['date_range']['earliest']} to {report['snapshots']['date_range']['latest']}")
        
        # Check for available data
        available_tickers = utils.get_available_cryptocurrencies()
        available_snapshots = utils.get_available_snapshots()
        
        if available_tickers:
            print(f"\n📈 Historical data available for: {len(available_tickers)} cryptocurrency tickers")
            
            # Load sample data
            sample_ticker = available_tickers[0]
            df = utils.load_historical_data(sample_ticker)
            if df is not None:
                print(f"  • Sample data for {sample_ticker}:")
                print(f"    - Date range: {df['date'].min()} to {df['date'].max()}")
                
                # Check which price column exists
                if 'close' in df.columns:
                    price_col = 'close'
                elif 'current_price' in df.columns:
                    price_col = 'current_price'
                else:
                    price_col = df.select_dtypes(include=['float64', 'int64']).columns[0]
                
                print(f"    - Price range: ${df[price_col].min():.2f} - ${df[price_col].max():.2f}")
                print(f"    - Data points: {len(df)}")
        
        if available_snapshots:
            print(f"\n📅 Daily snapshots available: {len(available_snapshots)}")
            
            # Load latest snapshot
            latest_snapshot = utils.load_daily_snapshot(available_snapshots[-1])
            if latest_snapshot is not None:
                print(f"  • Latest snapshot ({available_snapshots[-1]}):")
                if 'ticker_name' in latest_snapshot.columns:
                    print(f"    - Top ticker: {latest_snapshot.iloc[0]['ticker_name']}")
                elif 'ticker' in latest_snapshot.columns:
                    print(f"    - Top ticker: {latest_snapshot.iloc[0]['ticker']}")
                
                if 'current_price' in latest_snapshot.columns:
                    total_value = latest_snapshot['current_price'].sum()
                    print(f"    - Total price sum: ${total_value:,.2f}")
        
        print("\n✅ Data analysis demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in data analysis demo: {e}")


def demo_backup_restore():
    """Demonstrate backup and restore functionality"""
    print("\n" + "=" * 60)
    print("DEMO: Backup & Restore")
    print("=" * 60)
    
    try:
        utils = CryptoDataUtils()
        
        # Create backup
        print("Creating data backup...")
        backup_path = utils.backup_data("demo_backup")
        print(f"✅ Backup created at: {backup_path}")
        
        # List backup contents
        if os.path.exists(backup_path):
            backup_contents = os.listdir(backup_path)
            print(f"📁 Backup contains: {', '.join(backup_contents)}")
        
        print("\n✅ Backup demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in backup demo: {e}")


def demo_scheduler():
    """Demonstrate scheduler functionality"""
    print("\n" + "=" * 60)
    print("DEMO: Scheduler")
    print("=" * 60)
    
    try:
        scheduler = CryptoScheduler()
        
        # Setup a demo schedule (but don't run it)
        scheduler.setup_daily_schedule("10:00")
        
        # Get next run time
        next_run = scheduler.get_next_run_time()
        if next_run:
            print(f"📅 Next scheduled run: {next_run}")
        
        # List scheduled jobs
        scheduler.list_scheduled_jobs()
        
        print("\n✅ Scheduler demo completed successfully!")
        print("   (Note: Scheduler was configured but not started)")
        
    except Exception as e:
        print(f"❌ Error in scheduler demo: {e}")


def check_system_requirements():
    """Check if system requirements are met"""
    print("=" * 60)
    print("SYSTEM REQUIREMENTS CHECK")
    print("=" * 60)
    
    requirements_met = True
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("   ❌ Python 3.7+ required")
        requirements_met = False
    else:
        print("   ✅ Python version OK")
    
    # Check required packages
    required_packages = ['requests', 'pandas', 'schedule']
    for package in required_packages:
        try:
            __import__(package)
            print(f"📦 {package}: ✅ Installed")
        except ImportError:
            print(f"📦 {package}: ❌ Not installed")
            requirements_met = False
    
    # Check configuration file
    config_path = "config/settings.json"
    if os.path.exists(config_path):
        print(f"⚙️  Configuration: ✅ Found at {config_path}")
        try:
            with open(config_path, 'r') as f:
                json.load(f)
            print("   ✅ Configuration file is valid JSON")
        except json.JSONDecodeError:
            print("   ❌ Configuration file contains invalid JSON")
            requirements_met = False
    else:
        print(f"⚙️  Configuration: ❌ Not found at {config_path}")
        requirements_met = False
    
    # Check internet connectivity (basic)
    try:
        import requests
        response = requests.get("https://api.coingecko.com/api/v3/ping", timeout=10)
        if response.status_code == 200:
            print("🌐 Internet connectivity: ✅ CoinGecko API accessible")
        else:
            print("🌐 Internet connectivity: ⚠️  CoinGecko API returned non-200 status")
    except Exception as e:
        print(f"🌐 Internet connectivity: ❌ Cannot reach CoinGecko API ({e})")
        requirements_met = False
    
    print("\n" + "=" * 60)
    if requirements_met:
        print("✅ ALL REQUIREMENTS MET - System ready to use!")
    else:
        print("❌ SOME REQUIREMENTS NOT MET - Please install missing dependencies")
        print("\nTo install missing packages, run:")
        print("pip install -r requirements.txt")
    print("=" * 60)
    
    return requirements_met


def main():
    """Main function to run all demos"""
    print("🚀 Cryptocurrency Data Collection System - Demo")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check system requirements first
    if not check_system_requirements():
        print("\n⚠️  Please resolve system requirements before running demos.")
        return
    
    print("\n🎯 Running demonstration of all system features...")
    
    # Run demos
    demo_basic_collection()
    demo_data_analysis()
    demo_backup_restore()
    demo_scheduler()
    
    print("\n" + "=" * 60)
    print("🎉 ALL DEMOS COMPLETED!")
    print("=" * 60)
    print("\n📚 Next steps:")
    print("1. Run full data collection: python crypto_collector.py")
    print("2. Set up daily automation: python scheduler.py --mode daily --time 09:00")
    print("3. Analyze your data using the utilities in data_utils.py")
    print("4. Check the README.md for detailed usage instructions")
    print("\n💡 Tip: Check the crypto_data/ directory for your collected data!")


if __name__ == "__main__":
    main()