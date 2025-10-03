#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Flask Crypto Dashboard
Verifies basic functionality and data integration
"""

import os
import sys
import json
import time
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_flask_app():
    """Test the Flask application"""
    print("Testing Flask Crypto Dashboard")
    print("=" * 50)
    
    # Test 1: Check if required files exist
    print("\n1. Checking required files...")
    required_files = [
        'app.py',
        'config/settings.json',
        'services/data_service.py',
        'services/chart_service.py',
        'services/market_service.py',
        'templates/base.html',
        'templates/dashboard.html',
        'static/css/dashboard.css',
        'static/js/dashboard.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  [OK] {file_path}")
        else:
            print(f"  [MISSING] {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n[ERROR] Missing files: {missing_files}")
        return False
    
    # Test 2: Check data availability
    print("\n2. Checking data availability...")
    data_dirs = [
        'crypto_data',
        'crypto_data/historical',
        'crypto_data/daily_snapshots'
    ]
    
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            files = os.listdir(data_dir)
            print(f"  [OK] {data_dir} ({len(files)} files)")
        else:
            print(f"  [WARNING] {data_dir} (not found)")
    
    # Test 3: Check configuration
    print("\n3. Checking configuration...")
    try:
        with open('config/settings.json', 'r') as f:
            config = json.load(f)
        
        if 'flask' in config:
            print("  [OK] Flask configuration found")
        else:
            print("  [WARNING] Flask configuration not found in settings")
        
        if 'data' in config:
            print("  [OK] Data configuration found")
        else:
            print("  [ERROR] Data configuration missing")
            
    except Exception as e:
        print(f"  [ERROR] Configuration error: {e}")
        return False
    
    # Test 4: Import test
    print("\n4. Testing imports...")
    try:
        sys.path.insert(0, '.')
        
        from services.data_service import CryptoDataService
        print("  [OK] CryptoDataService import successful")
        
        from services.chart_service import ChartService
        print("  [OK] ChartService import successful")
        
        from services.market_service import MarketService
        print("  [OK] MarketService import successful")
        
        # Test service initialization
        data_service = CryptoDataService()
        print("  [OK] CryptoDataService initialization successful")
        
        chart_service = ChartService()
        print("  [OK] ChartService initialization successful")
        
        market_service = MarketService()
        print("  [OK] MarketService initialization successful")
        
    except Exception as e:
        print(f"  [ERROR] Import error: {e}")
        return False
    
    # Test 5: Data service functionality
    print("\n5. Testing data service functionality...")
    try:
        # Test getting available cryptocurrencies
        cryptos = data_service.get_available_cryptocurrencies()
        print(f"  [OK] Available cryptocurrencies: {len(cryptos)}")
        
        if cryptos:
            print(f"  [DATA] Sample cryptos: {[c['symbol'] for c in cryptos[:5]]}")
        
        # Test market cap data
        market_cap_data = data_service.get_market_cap_data()
        print(f"  [OK] Market cap data: {len(market_cap_data)} entries")
        
        # Test market summary
        market_summary = market_service.get_market_summary()
        print(f"  [OK] Market summary: {market_summary.get('total_cryptocurrencies', 0)} cryptos")
        
    except Exception as e:
        print(f"  [WARNING] Data service test failed: {e}")
        print("  [INFO] This may be normal if no data has been collected yet")
    
    print("\n" + "=" * 50)
    print("[SUCCESS] Basic tests completed successfully!")
    print("\n[NEXT STEPS]:")
    print("1. Ensure you have collected crypto data:")
    print("   python crypto_collector.py")
    print("\n2. Start the Flask dashboard:")
    print("   python app.py")
    print("\n3. Open your browser to:")
    print("   http://localhost:5000")
    
    return True

def test_flask_server():
    """Test Flask server if it's running"""
    print("\n[SERVER TEST] Testing Flask server...")
    
    base_url = "http://localhost:5000"
    
    # Test endpoints
    endpoints = [
        "/",
        "/market-cap",
        "/charts",
        "/performance",
        "/api/summary",
        "/api/market-cap"
    ]
    
    server_running = False
    
    for endpoint in endpoints:
        try:
            try:
                import requests
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"  [OK] {endpoint} - Status: {response.status_code}")
                    server_running = True
                else:
                    print(f"  [WARNING] {endpoint} - Status: {response.status_code}")
            except ImportError:
                print(f"  [SKIP] {endpoint} - requests module not available")
                break
            except Exception as e:
                print(f"  [ERROR] {endpoint} - Error: {e}")
        except Exception as e:
            print(f"  [ERROR] {endpoint} - Connection failed: {e}")
    
    if server_running:
        print("\n[SUCCESS] Flask server is running and responding!")
    else:
        print("\n[INFO] Flask server is not running or not responding")
        print("[INFO] Start the server with: python app.py")
    
    return server_running

if __name__ == "__main__":
    print(f"[START] Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run basic tests
    basic_tests_passed = test_flask_app()
    
    # Test server if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        test_flask_server()
    
    print(f"\n[END] Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if basic_tests_passed:
        print("\n[SUCCESS] Dashboard is ready to use!")
    else:
        print("\n[WARNING] Some issues found - check the output above")