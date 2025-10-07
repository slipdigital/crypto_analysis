"""
Cryptocurrency Data Collector - Polygon.io API Version
Collects daily data for top cryptocurrencies using Polygon.io API
Data source dynamically loaded from crypto_tickers.csv
"""

import requests
import pandas as pd
import json
import logging
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import csv

from base_collector import BasePolygonCollector


class CryptoDataCollector(BasePolygonCollector):
    """Main class for collecting cryptocurrency data from Polygon.io API"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the collector with configuration"""
        super().__init__(config_path)
        self.config = self._load_config(config_path)
        self.base_url = self.config["api"]["polygon_base_url"]
        self.api_key = self.config["api"]["api_key"]
        self.rate_limit_delay = self.config["api"]["rate_limit_delay"]
        self.max_retries = self.config["api"]["max_retries"]
        self.timeout = self.config["api"]["timeout"]
        
        # Setup logging
        self._setup_logging()
        
        # Create directories
        self._create_directories()
        
        # Load major cryptos from CSV
        self.major_cryptos = self._load_major_cryptos()
        
        # Validate API key
        if self.api_key == "YOUR_POLYGON_API_KEY":
            self.logger.warning("Please set your Polygon.io API key in config/settings.json")
            self.logger.warning("Run 'python setup_polygon.py' to configure your API key")
        
        self.logger.info("CryptoDataCollector (Polygon.io) initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {config_path}")
    
    def _load_major_cryptos(self) -> List[str]:
        """Load major cryptocurrency symbols from crypto_tickers.csv"""
        try:
            # Try different possible paths for the CSV file
            possible_paths = [
                "crypto_data/crypto_tickers.csv",
                os.path.join(self.config.get("data", {}).get("data_directory", "crypto_data"), "crypto_tickers.csv")
            ]
            
            ticker_df = None
            for path in possible_paths:
                if os.path.exists(path):
                    ticker_df = pd.read_csv(path)
                    self.logger.info(f"Loaded cryptocurrency list from: {path}")
                    break
            
            if ticker_df is None:
                # Fallback to a minimal default list if CSV not found
                self.logger.warning("crypto_tickers.csv not found. Using minimal default crypto list.")
                return ['BTC', 'ETH', 'XRP', 'ADA', 'SOL']
            
            # Filter for active USD pairs only
            if 'active' in ticker_df.columns and 'is_usd_pair' in ticker_df.columns and 'crypto_symbol' in ticker_df.columns:
                active_usd_cryptos = ticker_df[
                    (ticker_df['active'] == True) & 
                    (ticker_df['is_usd_pair'] == True) & 
                    (ticker_df['crypto_symbol'].notna()) &
                    (ticker_df['crypto_symbol'] != '')
                ]
                
                # Extract unique crypto symbols and return as list
                crypto_list = active_usd_cryptos['crypto_symbol'].unique().tolist()
                
                if len(crypto_list) > 0:
                    self.logger.info(f"Loaded {len(crypto_list)} active cryptocurrencies from CSV")
                    return crypto_list
                else:
                    self.logger.warning("No active cryptocurrencies found in CSV. Using defaults.")
                    return ['BTC', 'ETH', 'XRP', 'ADA', 'SOL']
            else:
                # If expected columns don't exist, try to extract from ticker column
                self.logger.warning("Expected columns not found in CSV. Attempting to parse tickers.")
                crypto_symbols = set()
                
                if 'ticker' in ticker_df.columns:
                    for ticker in ticker_df['ticker']:
                        if isinstance(ticker, str) and ticker.startswith('X:') and ticker.endswith('USD'):
                            symbol = ticker.replace('X:', '').replace('USD', '')
                            if symbol and len(symbol) <= 10:  # Reasonable symbol length
                                crypto_symbols.add(symbol)
                
                if crypto_symbols:
                    crypto_list = list(crypto_symbols)
                    self.logger.info(f"Extracted {len(crypto_list)} crypto symbols from tickers")
                    return crypto_list
                else:
                    self.logger.warning("Could not extract crypto symbols. Using defaults.")
                    return ['BTC', 'ETH', 'XRP', 'ADA', 'SOL']
                    
        except Exception as e:
            self.logger.warning(f"Error loading major cryptos from CSV: {e}")
            self.logger.info("Using minimal default crypto list")
            return ['BTC', 'ETH', 'XRP', 'ADA', 'SOL']

    def get_crypto_tickers(self) -> List[str]:
        """Get available cryptocurrency tickers from Polygon.io"""
        self.logger.info("Fetching available cryptocurrency tickers")
        
        params = {
            'market': 'crypto',
            'active': 'true',
            'limit': 1000
        }
        
        data = self._make_api_request("v3/reference/tickers", params)
        
        if data and 'results' in data:
            # Filter for USD pairs using dynamically loaded major cryptos list
            crypto_tickers = []
            
            for ticker_info in data['results']:
                ticker = ticker_info.get('ticker', '')
                # Look for X:CRYPTOUSD format for major cryptocurrencies
                if ticker.startswith('X:') and ticker.endswith('USD'):
                    crypto_symbol = ticker.replace('X:', '').replace('USD', '')
                    if crypto_symbol in self.major_cryptos:
                        crypto_tickers.append(ticker)
            
            # If we don't have enough major cryptos from the list, add any USD crypto pairs
            if len(crypto_tickers) < self.config["data"]["top_n_cryptos"]:
                self.logger.info(f"Found {len(crypto_tickers)} from major list, fetching additional USD pairs...")
                for ticker_info in data['results']:
                    ticker = ticker_info.get('ticker', '')
                    if (ticker.startswith('X:') and ticker.endswith('USD') and 
                        ticker not in crypto_tickers and 
                        len(ticker) <= 12):  # Reasonable length filter
                        crypto_tickers.append(ticker)
                        if len(crypto_tickers) >= self.config["data"]["top_n_cryptos"]:
                            break
            
            self.logger.info(f"Found {len(crypto_tickers)} cryptocurrency tickers")
            return crypto_tickers[:self.config["data"]["top_n_cryptos"]]
        else:
            self.logger.error("Failed to fetch cryptocurrency tickers")
            return []

def main():
    CryptoDataCollector().get_crypto_tickers()

if __name__ == "__main__":
    main()
