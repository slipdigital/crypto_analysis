"""
Setup Script for Polygon.io API Integration
Helps users configure their API key and test the connection
"""

import json
import os
import requests
from datetime import datetime


def setup_api_key():
    """Interactive setup for Polygon.io API key"""
    print("🔧 Polygon.io API Setup")
    print("=" * 50)
    
    # Check if config file exists
    config_path = "config/settings.json"
    if not os.path.exists(config_path):
        print("❌ Configuration file not found!")
        print("Please ensure config/settings.json exists.")
        return False
    
    # Load current config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    current_key = config["api"]["api_key"]
    
    if current_key != "YOUR_POLYGON_API_KEY":
        print(f"✅ API key is already configured: {current_key[:8]}...")
        update = input("Do you want to update it? (y/N): ").lower().strip()
        if update != 'y':
            return True
    
    print("\n📝 To get your Polygon.io API key:")
    print("1. Visit https://polygon.io/")
    print("2. Sign up for a free account")
    print("3. Go to your dashboard")
    print("4. Copy your API key")
    
    api_key = input("\n🔑 Enter your Polygon.io API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return False
    
    # Update config
    config["api"]["api_key"] = api_key
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ API key saved successfully!")
    return True


def test_api_connection():
    """Test the Polygon.io API connection"""
    print("\n🧪 Testing API Connection")
    print("=" * 30)
    
    # Load config
    config_path = "config/settings.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    api_key = config["api"]["api_key"]
    base_url = config["api"]["polygon_base_url"]
    
    if api_key == "YOUR_POLYGON_API_KEY":
        print("❌ Please set up your API key first!")
        return False
    
    # Test basic API call
    try:
        print("📡 Testing basic API connectivity...")
        url = f"{base_url}/v3/reference/tickers"
        params = {
            'apikey': api_key,
            'market': 'crypto',
            'active': 'true',
            'limit': 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and data['results']:
                print("✅ API connection successful!")
                print(f"📊 Found {len(data['results'])} cryptocurrency tickers")
                
                # Show sample tickers
                print("\n🪙 Sample cryptocurrency tickers:")
                for i, ticker in enumerate(data['results'][:3], 1):
                    name = ticker.get('name', 'Unknown')
                    symbol = ticker.get('ticker', 'Unknown')
                    print(f"  {i}. {name} ({symbol})")
                
                return True
            else:
                print("⚠️  API responded but no data found")
                return False
        
        elif response.status_code == 401:
            print("❌ Authentication failed - check your API key")
            return False
        
        elif response.status_code == 403:
            print("❌ Access forbidden - check your API plan permissions")
            return False
        
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_api_limits():
    """Check API plan limits and usage"""
    print("\n📊 API Plan Information")
    print("=" * 25)
    
    print("ℹ️  Polygon.io API Plans:")
    print("  • Free Tier: 5 calls per minute")
    print("  • Basic Plan: 100 calls per minute")
    print("  • Starter Plan: 500 calls per minute")
    print("  • Developer Plan: 1000 calls per minute")
    
    print("\n💡 Tips for optimal usage:")
    print("  • Free tier: Set rate_limit_delay to 12+ seconds")
    print("  • Paid plans: Set rate_limit_delay to 0.1-1 seconds")
    print("  • Monitor your usage in the Polygon.io dashboard")
    
    # Load current config
    config_path = "config/settings.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    current_delay = config["api"]["rate_limit_delay"]
    print(f"\n⚙️  Current rate limit delay: {current_delay} seconds")
    
    if current_delay < 12:
        print("⚠️  Warning: Current delay may be too low for free tier")
        update = input("Update to 12 seconds for free tier? (Y/n): ").lower().strip()
        if update != 'n':
            config["api"]["rate_limit_delay"] = 12
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Rate limit delay updated to 12 seconds")


def main():
    """Main setup function"""
    print("🚀 Polygon.io Cryptocurrency Data Collector Setup")
    print("=" * 55)
    print(f"⏰ Setup started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Setup API key
    if not setup_api_key():
        print("\n❌ Setup failed at API key configuration")
        return
    
    # Step 2: Test connection
    if not test_api_connection():
        print("\n❌ Setup failed at API connection test")
        return
    
    # Step 3: Check limits
    check_api_limits()
    
    print("\n" + "=" * 55)
    print("🎉 Setup completed successfully!")
    print("=" * 55)
    
    print("\n📚 Next steps:")
    print("1. Run a test collection: python example_usage.py")
    print("2. Start full data collection: python crypto_collector.py")
    print("3. Set up automation: python scheduler.py --mode daily --time 09:00")
    
    print("\n💡 Remember:")
    print("• Monitor your API usage in the Polygon.io dashboard")
    print("• Adjust rate_limit_delay based on your plan")
    print("• Check the logs for any issues during collection")


if __name__ == "__main__":
    main()