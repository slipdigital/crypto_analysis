"""
Cryptocurrency Data Collector - Polygon.io API Version
Collects daily data for top 30 cryptocurrencies using Polygon.io API
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


class CryptoDataCollector:
    """Main class for collecting cryptocurrency data from Polygon.io API"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the collector with configuration"""
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
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.config["data"]["logs_directory"]
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"crypto_collector_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=getattr(logging, self.config["logging"]["level"]),
            format=self.config["logging"]["format"],
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _create_directories(self):
        """Create necessary directories for data storage"""
        directories = [
            self.config["data"]["data_directory"],
            self.config["data"]["historical_directory"],
            self.config["data"]["snapshots_directory"],
            self.config["data"]["logs_directory"]
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.debug(f"Created/verified directory: {directory}")
    
    def _load_major_cryptos(self) -> List[str]:
        """Load major cryptocurrency symbols from JSON file"""
        json_file_path = os.path.join("crypto_data", "major_crypto_currencies.json")
        
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
                major_cryptos = data.get('major_cryptos', [])
                self.logger.info(f"Loaded {len(major_cryptos)} major cryptocurrencies from {json_file_path}")
                return major_cryptos
        except FileNotFoundError:
            self.logger.warning(f"Major crypto currencies file not found: {json_file_path}")
            # Fallback to hardcoded list
            fallback_cryptos = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LTC', 'BCH', 'LINK', 'XLM', 'DOGE',
                              'UNI', 'AAVE', 'ALGO', 'ATOM', 'AVAX', 'SOL', 'MATIC', 'FTT', 'NEAR', 'MANA',
                              'SAND', 'CRV', 'SUSHI', 'COMP', 'YFI', 'SNX', 'MKR', 'BAT', 'ZRX', 'ENJ']
            self.logger.info(f"Using fallback list of {len(fallback_cryptos)} major cryptocurrencies")
            return fallback_cryptos
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in major crypto currencies file: {e}")
            # Fallback to hardcoded list
            fallback_cryptos = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LTC', 'BCH', 'LINK', 'XLM', 'DOGE',
                              'UNI', 'AAVE', 'ALGO', 'ATOM', 'AVAX', 'SOL', 'MATIC', 'FTT', 'NEAR', 'MANA',
                              'SAND', 'CRV', 'SUSHI', 'COMP', 'YFI', 'SNX', 'MKR', 'BAT', 'ZRX', 'ENJ']
            self.logger.info(f"Using fallback list of {len(fallback_cryptos)} major cryptocurrencies")
            return fallback_cryptos
    
    def _make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with retry logic and rate limiting"""
        if params is None:
            params = {}
        
        # Add API key to parameters
        params['apikey'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Making API request to: {url} (attempt {attempt + 1})")
                
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"All API request attempts failed for {url}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def get_crypto_tickers(self) -> List[str]:
        """Get available cryptocurrency tickers from Polygon.io"""
        self.logger.info("Fetching available cryptocurrency tickers")
        
        # Load major cryptocurrencies from JSON file
        major_cryptos = self._load_major_cryptos()
        
        params = {
            'market': 'crypto',
            'active': 'true',
            'limit': 1000
        }
        
        data = self._make_api_request("v3/reference/tickers", params)
        
        if data and 'results' in data:
            # Filter for major USD pairs only
            crypto_tickers = []
            
            for ticker_info in data['results']:
                ticker = ticker_info.get('ticker', '')
                # Look for X:CRYPTOUSD format for major cryptocurrencies
                if ticker.startswith('X:') and ticker.endswith('USD'):
                    crypto_symbol = ticker.replace('X:', '').replace('USD', '')
                    if crypto_symbol in major_cryptos:
                        crypto_tickers.append(ticker)
            
            # If we don't have enough major cryptos, add any USD crypto pairs
            if len(crypto_tickers) < self.config["data"]["top_n_cryptos"]:
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
    
    def get_ticker_details(self, ticker: str) -> Optional[Dict]:
        """Get detailed information about a specific ticker"""
        self.logger.debug(f"Fetching details for ticker: {ticker}")
        
        endpoint = f"v3/reference/tickers/{ticker}"
        data = self._make_api_request(endpoint)
        
        if data and 'results' in data:
            return data['results']
        else:
            self.logger.warning(f"Failed to fetch details for ticker: {ticker}")
            return None
    
    def get_previous_close(self, ticker: str) -> Optional[Dict]:
        """Get previous close price for a cryptocurrency (more reliable than last trade)"""
        self.logger.debug(f"Fetching previous close for {ticker}")
        
        endpoint = f"v2/aggs/ticker/{ticker}/prev"
        data = self._make_api_request(endpoint)
        
        if data and 'results' in data and len(data['results']) > 0:
            return data['results'][0]
        else:
            self.logger.warning(f"Failed to fetch previous close for {ticker}")
            return None
    
    def get_daily_bars(self, ticker: str, from_date: str, to_date: str) -> Optional[Dict]:
        """Get daily OHLCV data for a cryptocurrency"""
        self.logger.debug(f"Fetching daily bars for {ticker} from {from_date} to {to_date}")
        
        endpoint = f"v2/aggs/ticker/{ticker}/range/1/day/{from_date}/{to_date}"
        params = {
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000
        }
        
        data = self._make_api_request(endpoint, params)
        
        if data and 'results' in data:
            self.logger.debug(f"Successfully fetched {len(data['results'])} daily bars for {ticker}")
            return data
        else:
            self.logger.warning(f"Failed to fetch daily bars for {ticker}")
            return None
    
    def get_historical_data(self, ticker: str, days: int = None) -> Optional[Dict]:
        """Get historical market data for a specific cryptocurrency"""
        if days is None:
            days = self.config["data"]["historical_days"]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        return self.get_daily_bars(ticker, from_date, to_date)
    
    def _validate_data(self, data: Dict, data_type: str) -> bool:
        """Validate data quality and completeness"""
        if not data:
            self.logger.warning(f"Empty data received for {data_type}")
            return False
        
        if data_type == "ticker_data":
            required_fields = ['ticker', 'name']
            for field in required_fields:
                if field not in data or data[field] is None:
                    self.logger.warning(f"Missing or null field '{field}' in ticker data")
                    return False
        
        elif data_type == "price_data":
            required_fields = ['c']  # close price field in Polygon.io
            for field in required_fields:
                if field not in data or data[field] is None:
                    self.logger.warning(f"Missing or null field '{field}' in price data")
                    return False
        
        elif data_type == "historical_data":
            required_fields = ['results']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.logger.warning(f"Missing or empty field '{field}' in historical data")
                    return False
        
        return True
    
    def save_historical_data_to_csv(self, ticker: str, ticker_details: Dict, historical_data: Dict):
        """Save historical data to CSV file"""
        # Clean ticker name for filename
        clean_ticker = ticker.replace(':', '_').replace('/', '_')
        filename = f"{clean_ticker}_historical.csv"
        filepath = os.path.join(self.config["data"]["historical_directory"], filename)
        
        # Prepare data for CSV
        results = historical_data['results']
        
        # Create DataFrame
        df_data = []
        for bar in results:
            timestamp = bar['t']  # timestamp in milliseconds
            date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            
            row = {
                'date': date,
                'ticker': ticker,
                'ticker_name': ticker_details.get('name', ticker),
                'open': bar.get('o', 0),
                'high': bar.get('h', 0),
                'low': bar.get('l', 0),
                'close': bar.get('c', 0),
                'volume': bar.get('v', 0),
                'volume_weighted_price': bar.get('vw', 0),
                'number_of_transactions': bar.get('n', 0)
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        self.logger.info(f"Saved historical data for {ticker} to {filepath}")
    
    def save_daily_snapshot_to_csv(self, crypto_data: List[Dict]):
        """Save daily market snapshot to CSV file"""
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{today}_snapshot.csv"
        filepath = os.path.join(self.config["data"]["snapshots_directory"], filename)
        
        # Prepare data for CSV
        df_data = []
        for i, crypto in enumerate(crypto_data, 1):
            ticker = crypto['ticker']
            details = crypto.get('details', {})
            price_data = crypto.get('price_data', {})
            
            row = {
                'date': today,
                'rank': i,
                'ticker': ticker,
                'ticker_name': details.get('name', ticker),
                'current_price': price_data.get('c', 0),  # close price
                'open_price': price_data.get('o', 0),
                'high_price': price_data.get('h', 0),
                'low_price': price_data.get('l', 0),
                'volume': price_data.get('v', 0),
                'volume_weighted_price': price_data.get('vw', 0),
                'number_of_transactions': price_data.get('n', 0),
                'timestamp': price_data.get('t', 0),
                'market_status': details.get('market_status', ''),
                'type': details.get('type', ''),
                'active': details.get('active', False),
                'currency_name': details.get('currency_name', ''),
                'base_currency_symbol': details.get('base_currency_symbol', ''),
                'base_currency_name': details.get('base_currency_name', '')
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        self.logger.info(f"Saved daily snapshot to {filepath}")
    
    def collect_all_data(self):
        """Main method to collect both historical and current data"""
        self.logger.info("Starting comprehensive data collection using Polygon.io API")
        
        # Check API key
        if self.api_key == "YOUR_POLYGON_API_KEY":
            self.logger.error("Please set your Polygon.io API key in config/settings.json")
            self.logger.error("Run 'python setup_polygon.py' to configure your API key")
            return
        
        # Get cryptocurrency tickers
        crypto_tickers = self.get_crypto_tickers()
        
        if not crypto_tickers:
            self.logger.error("Failed to fetch cryptocurrency tickers. Aborting collection.")
            return
        
        self.logger.info(f"Processing {len(crypto_tickers)} cryptocurrency tickers")
        
        # Collect data for each cryptocurrency
        crypto_data = []
        
        for i, ticker in enumerate(crypto_tickers, 1):
            self.logger.info(f"Processing {ticker} ({i}/{len(crypto_tickers)})")
            
            # Get ticker details
            ticker_details = self.get_ticker_details(ticker)
            if not ticker_details or not self._validate_data(ticker_details, "ticker_data"):
                self.logger.warning(f"Invalid ticker details for {ticker}, skipping")
                continue
            
            # Get current price (using previous close as it's more reliable)
            price_data = self.get_previous_close(ticker)
            if not price_data or not self._validate_data(price_data, "price_data"):
                self.logger.warning(f"Invalid price data for {ticker}, using placeholder")
                price_data = {'c': 0, 'o': 0, 'h': 0, 'l': 0, 'v': 0, 'vw': 0, 'n': 0, 't': 0}
            
            # Store for snapshot
            crypto_info = {
                'ticker': ticker,
                'details': ticker_details,
                'price_data': price_data
            }
            crypto_data.append(crypto_info)
            
            # Collect historical data if enabled
            if self.config["collection"]["collect_historical"]:
                # Check if historical data already exists
                clean_ticker = ticker.replace(':', '_').replace('/', '_')
                filename = f"{clean_ticker}_historical.csv"
                filepath = os.path.join(self.config["data"]["historical_directory"], filename)
                
                if os.path.exists(filepath) and not self.config["collection"]["update_existing"]:
                    self.logger.info(f"Historical data for {ticker} already exists, skipping")
                    continue
                
                # Get historical data
                historical_data = self.get_historical_data(ticker)
                
                if historical_data and self._validate_data(historical_data, "historical_data"):
                    self.save_historical_data_to_csv(ticker, ticker_details, historical_data)
                else:
                    self.logger.warning(f"Failed to get valid historical data for {ticker}")
        
        # Save daily snapshot if enabled
        if self.config["collection"]["collect_snapshots"] and crypto_data:
            self.save_daily_snapshot_to_csv(crypto_data)
        
        self.logger.info("Data collection completed successfully")


def main():
    """Main function to run the crypto data collector"""
    try:
        collector = CryptoDataCollector()
        collector.collect_all_data()
    except Exception as e:
        logging.error(f"Fatal error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()