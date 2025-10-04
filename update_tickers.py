"""
Cryptocurrency Ticker Collector
Fetches all available cryptocurrency tickers from Polygon.io and stores them in a CSV file.
Includes market cap and price information.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests


class CryptoTickerCollector:
    """Collector for all cryptocurrency tickers from Polygon.io"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the ticker collector with configuration"""
        self.config = self._load_config(config_path)
        self.base_url = self.config["api"]["polygon_base_url"]
        self.api_key = self.config["api"]["api_key"]
        self.rate_limit_delay = self.config["api"]["rate_limit_delay"]
        self.max_retries = self.config["api"]["max_retries"]
        self.timeout = self.config["api"]["timeout"]
        
        # Performance optimization settings
        self.max_workers = 10  # Number of concurrent API requests
        self.batch_size = 50  # Process tickers in batches for progress reporting
        
        # Setup logging
        self._setup_logging()
        
        # Create directories
        self._create_directories()
        
        # Validate API key
        if self.api_key == "YOUR_POLYGON_API_KEY":
            self.logger.warning("Please set your Polygon.io API key in config/settings.json")
            self.logger.warning("Run 'python setup_polygon.py' to configure your API key")
        
        self.logger.info("CryptoTickerCollector initialized successfully")
    
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
        
        log_file = os.path.join(
            log_dir, 
            f"ticker_update_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
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
        data_dir = self.config["data"]["data_directory"]
        os.makedirs(data_dir, exist_ok=True)
        self.logger.debug(f"Created/verified directory: {data_dir}")
    
    def _make_api_request(self, endpoint: str, params: Dict = None, skip_delay: bool = False) -> Optional[Dict]:
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
                
                # Rate limiting (can be skipped for concurrent requests)
                if not skip_delay:
                    time.sleep(self.rate_limit_delay)
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"All API request attempts failed for {url}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def get_all_crypto_tickers(self) -> List[Dict]:
        """
        Get all available cryptocurrency tickers from Polygon.io
        Handles pagination to retrieve all tickers
        """
        self.logger.info("Fetching all cryptocurrency tickers from Polygon.io")
        
        all_tickers = []
        next_url = None
        page = 1
        
        while True:
            self.logger.info(f"Fetching page {page} of crypto tickers...")
            
            if next_url:
                # Use the next_url from pagination
                try:
                    params = {'apikey': self.api_key}
                    response = requests.get(next_url, params=params, timeout=self.timeout)
                    response.raise_for_status()
                    data = response.json()
                    time.sleep(self.rate_limit_delay)
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Failed to fetch page {page}: {e}")
                    break
            else:
                # Initial request
                params = {
                    'market': 'crypto',
                    'active': 'true',
                    'limit': 1000,  # Maximum allowed per request
                    'sort': 'ticker',
                    'order': 'asc'
                }
                
                data = self._make_api_request("v3/reference/tickers", params)
            
            if not data or 'results' not in data:
                self.logger.warning(f"No results found on page {page}")
                break
            
            # Add tickers from this page
            page_tickers = data['results']
            all_tickers.extend(page_tickers)
            self.logger.info(f"Retrieved {len(page_tickers)} tickers from page {page}")
            
            # Check for next page
            if 'next_url' in data and data['next_url']:
                next_url = data['next_url']
                page += 1
            else:
                # No more pages
                break
        
        self.logger.info(f"Successfully fetched {len(all_tickers)} total cryptocurrency tickers")
        return all_tickers
    
    def get_ticker_details(self, ticker: str) -> Optional[Dict]:
        """Get detailed information about a specific ticker including market cap"""
        self.logger.debug(f"Fetching details for ticker: {ticker}")
        
        endpoint = f"v3/reference/tickers/{ticker}"
        data = self._make_api_request(endpoint)
        
        if data and 'results' in data:
            return data['results']
        else:
            self.logger.warning(f"Failed to fetch details for ticker: {ticker}")
            return None
    
    def get_previous_close(self, ticker: str) -> Optional[Dict]:
        """Get previous close price for a cryptocurrency"""
        self.logger.debug(f"Fetching previous close for {ticker}")
        
        endpoint = f"v2/aggs/ticker/{ticker}/prev"
        data = self._make_api_request(endpoint)
        
        if data and 'results' in data and len(data['results']) > 0:
            return data['results'][0]
        else:
            self.logger.debug(f"No previous close data for {ticker}")
            return None
    
    def get_ticker_details_batch(self, tickers: List[str]) -> Dict[str, Dict]:
        """
        Get detailed ticker information (including market cap) for multiple tickers using concurrent requests
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary mapping ticker to details data
        """
        self.logger.info(f"Fetching detailed info (including market cap) for {len(tickers)} tickers in parallel...")
        
        results = {}
        
        def fetch_single_details(ticker: str) -> tuple:
            """Fetch details for a single ticker"""
            try:
                endpoint = f"v3/reference/tickers/{ticker}"
                data = self._make_api_request(endpoint, skip_delay=True)
                
                if data and 'results' in data:
                    return (ticker, data['results'])
                else:
                    return (ticker, None)
            except Exception as e:
                self.logger.debug(f"Error fetching details for {ticker}: {e}")
                return (ticker, None)
        
        # Use ThreadPoolExecutor for concurrent API requests
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(fetch_single_details, ticker): ticker 
                for ticker in tickers
            }
            
            # Process completed requests
            completed = 0
            for future in as_completed(future_to_ticker):
                ticker, details_data = future.result()
                results[ticker] = details_data
                completed += 1
                
                # Log progress every 25 tickers
                if completed % 25 == 0:
                    self.logger.info(f"Details fetched: {completed}/{len(tickers)}")
                
                # Small delay to respect rate limits
                time.sleep(0.05)
        
        successful = sum(1 for v in results.values() if v is not None)
        self.logger.info(f"Successfully fetched details for {successful}/{len(tickers)} tickers")
        
        return results
    
    def get_previous_close_batch(self, tickers: List[str]) -> Dict[str, Dict]:
        """Batch fetch previous close data for multiple tickers
            
        Returns:
            Dictionary mapping ticker to price data
        """
        self.logger.info(f"Fetching price data for {len(tickers)} tickers in parallel...")
        
        results = {}
        
        def fetch_single_price(ticker: str) -> tuple:
            """Fetch price for a single ticker"""
            try:
                endpoint = f"v2/aggs/ticker/{ticker}/prev"
                data = self._make_api_request(endpoint, skip_delay=True)
                
                if data and 'results' in data and len(data['results']) > 0:
                    return (ticker, data['results'][0])
                else:
                    return (ticker, None)
            except Exception as e:
                self.logger.debug(f"Error fetching price for {ticker}: {e}")
                return (ticker, None)
        
        # Use ThreadPoolExecutor for concurrent API requests
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_ticker = {
                executor.submit(fetch_single_price, ticker): ticker 
                for ticker in tickers
            }
            
            # Process completed requests
            completed = 0
            for future in as_completed(future_to_ticker):
                ticker, price_data = future.result()
                results[ticker] = price_data
                completed += 1
                
                # Log progress every 25 tickers
                if completed % 25 == 0:
                    self.logger.info(f"Price data fetched: {completed}/{len(tickers)}")
                
                # Small delay to respect rate limits
                time.sleep(0.05)
        
        successful = sum(1 for v in results.values() if v is not None)
        self.logger.info(f"Successfully fetched price data for {successful}/{len(tickers)} tickers")
        
        return results

    def get_crypto_overview_batch(self, crypto_symbols: List[str]) -> Dict[str, Dict]:
        """
        Batch fetch market cap and overview data for crypto symbols.
        Since Polygon.io doesn't have a dedicated market cap endpoint,
        we'll use ticker details which may contain some metadata.
        
        Args:
            crypto_symbols: List of crypto symbols (e.g., ['BTC', 'ETH', 'XRP'])
        
        Returns:
            Dictionary mapping crypto symbol to overview data
        """
        self.logger.info(f"Fetching overview data for {len(crypto_symbols)} crypto symbols...")
        overview_map = {}
        
        # Note: Polygon.io free tier doesn't provide market cap data directly
        # We'll fetch what we can from ticker details
        for idx, symbol in enumerate(crypto_symbols, 1):
            try:
                # Construct ticker format (X:SYMBOLUSD)
                ticker = f"X:{symbol}USD"
                
                # Get ticker details
                endpoint = f"v3/reference/tickers/{ticker}"
                data = self._make_api_request(endpoint)
                
                if data and 'results' in data:
                    overview_map[symbol] = data['results']
                else:
                    overview_map[symbol] = None
                
                if idx % 20 == 0:
                    self.logger.info(f"Fetched overview for {idx}/{len(crypto_symbols)} symbols")
                
            except Exception as e:
                self.logger.warning(f"Failed to fetch overview for {symbol}: {e}")
                overview_map[symbol] = None
        
        self.logger.info(f"Overview data fetch complete. Found data for {sum(1 for v in overview_map.values() if v)} symbols")
        return overview_map

    def enrich_ticker_with_market_data_fast(
        self, 
        ticker: str, 
        crypto_symbol: str, 
        ticker_info: Dict,
        price_data: Optional[Dict],
        overview_data: Optional[Dict]
    ) -> Dict:
        """
        Fast enrichment using pre-fetched batch data.
        
        Args:
            ticker: Full ticker symbol (e.g., 'X:BTCUSD')
            crypto_symbol: Crypto symbol (e.g., 'BTC')
            ticker_info: Basic ticker info from initial fetch
            price_data: Pre-fetched price data
            overview_data: Pre-fetched overview data
        
        Returns:
            Dictionary with enriched market data
        """
        market_data = {
            'current_price': None,
            'market_cap': None,
            'volume': None,
            'price_change_24h': None,
            'last_trade_timestamp': None
        }
        
        try:
            # Extract price data
            if price_data:
                market_data['current_price'] = price_data.get('c')  # close price
                market_data['volume'] = price_data.get('v')  # volume
                market_data['last_trade_timestamp'] = price_data.get('t')  # timestamp
                
                # Calculate 24h price change if we have open and close
                open_price = price_data.get('o')
                close_price = price_data.get('c')
                if open_price and close_price and open_price > 0:
                    market_data['price_change_24h'] = ((close_price - open_price) / open_price) * 100
            
            # Note: Polygon.io doesn't provide market cap in their basic endpoints
            # Market cap would require additional data sources or premium endpoints
            # For now, we'll leave it as None unless found in overview data
            if overview_data:
                # Check if overview data has any market cap field (unlikely for free tier)
                market_data['market_cap'] = overview_data.get('market_cap') or overview_data.get('market_cap_usd')
        
        except Exception as e:
            self.logger.warning(f"Error enriching {ticker}: {e}")
        
        return market_data

    def process_ticker_data(self, tickers: List[Dict], enrich_data: bool = True) -> pd.DataFrame:
        """
        Process raw ticker data into a structured DataFrame
        
        Args:
            tickers: List of ticker dictionaries from Polygon.io
            enrich_data: Whether to fetch additional market data (price, market cap)
        """
        self.logger.info("Processing ticker data...")
        
        # First pass: extract basic info and identify USD pairs that need enrichment
        processed_data = []
        tickers_to_enrich = []
        crypto_symbols_to_fetch = []
        ticker_info_map = {}
        
        total_tickers = len(tickers)
        
        self.logger.info(f"First pass: Processing {total_tickers} tickers...")
        for idx, ticker_info in enumerate(tickers, 1):
            try:
                # Extract relevant information
                ticker = ticker_info.get('ticker', '')
                name = ticker_info.get('name', '')
                market = ticker_info.get('market', '')
                locale = ticker_info.get('locale', '')
                active = ticker_info.get('active', False)
                currency_symbol = ticker_info.get('currency_symbol', '')
                currency_name = ticker_info.get('currency_name', '')
                base_currency_symbol = ticker_info.get('base_currency_symbol', '')
                base_currency_name = ticker_info.get('base_currency_name', '')
                last_updated = ticker_info.get('last_updated_utc', '')
                delisted = ticker_info.get('delisted_utc', '')
                
                # Determine if it's a USD pair
                is_usd_pair = ticker.endswith('USD') or base_currency_symbol == 'USD'
                
                # Extract crypto symbol (e.g., BTC from X:BTCUSD)
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
                    'is_usd_pair': is_usd_pair,
                    'currency_symbol': currency_symbol,
                    'currency_name': currency_name,
                    'base_currency_symbol': base_currency_symbol,
                    'base_currency_name': base_currency_name,
                    'current_price': None,
                    'market_cap': None,
                    'volume_24h': None,
                    'price_change_24h': None,
                    'last_trade_timestamp': None,
                    'last_updated': last_updated,
                    'delisted': delisted,
                    'collected_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                processed_data.append(row)
                
                # Track tickers that need enrichment
                if enrich_data and active and is_usd_pair and crypto_symbol:
                    tickers_to_enrich.append(ticker)
                    ticker_info_map[ticker] = (len(processed_data) - 1, ticker_info, crypto_symbol)
                    if crypto_symbol not in crypto_symbols_to_fetch:
                        crypto_symbols_to_fetch.append(crypto_symbol)
                
            except Exception as e:
                self.logger.warning(f"Error processing ticker {ticker_info.get('ticker', 'unknown')}: {e}")
                continue
        
        self.logger.info(f"First pass complete. Created {len(processed_data)} ticker records.")
        self.logger.info(f"Identified {len(crypto_symbols_to_fetch)} unique crypto symbols to enrich")
        
        # Second pass: batch fetch market data for all USD pairs
        if enrich_data and tickers_to_enrich:
            self.logger.info(f"Enriching {len(tickers_to_enrich)} USD pair tickers with market data...")
            
            # Fetch all price data in parallel
            self.logger.info("Step 1/2: Fetching price data...")
            price_data_map = self.get_previous_close_batch(tickers_to_enrich)
            
            # Fetch market cap/overview data for unique crypto symbols
            self.logger.info(f"Step 2/2: Fetching market cap/overview data for {len(crypto_symbols_to_fetch)} crypto symbols...")
            overview_data_map = self.get_crypto_overview_batch(crypto_symbols_to_fetch)
            
            self.logger.info(f"Merging enriched data into ticker records...")
            # Update processed data with enriched information
            enriched_count = 0
            market_cap_found = 0
            price_found = 0
            
            for ticker in tickers_to_enrich:
                row_idx, ticker_info, crypto_symbol = ticker_info_map[ticker]
                price_data = price_data_map.get(ticker)
                overview_data = overview_data_map.get(crypto_symbol)
                
                market_data = self.enrich_ticker_with_market_data_fast(
                    ticker, crypto_symbol, ticker_info, price_data, overview_data
                )
                
                processed_data[row_idx]['current_price'] = market_data['current_price']
                processed_data[row_idx]['market_cap'] = market_data['market_cap']
                processed_data[row_idx]['volume_24h'] = market_data['volume']
                processed_data[row_idx]['price_change_24h'] = market_data['price_change_24h']
                processed_data[row_idx]['last_trade_timestamp'] = market_data['last_trade_timestamp']
                
                if market_data['market_cap'] is not None:
                    market_cap_found += 1
                if market_data['current_price'] is not None:
                    price_found += 1
                
                enriched_count += 1
                if enriched_count % 50 == 0:
                    self.logger.info(f"Merged data for {enriched_count}/{len(tickers_to_enrich)} tickers (MCap: {market_cap_found}, Price: {price_found})")
            
            self.logger.info(f"Enrichment complete for all {enriched_count} tickers")
            self.logger.info(f"Market cap data found for {market_cap_found}/{enriched_count} tickers ({100*market_cap_found/enriched_count:.1f}%)")
            self.logger.info(f"Price data found for {price_found}/{enriched_count} tickers ({100*price_found/enriched_count:.1f}%)")
            
            # Log warning if very few market caps were found
            if market_cap_found < enriched_count * 0.1:  # Less than 10%
                self.logger.warning(f"⚠️  Only {market_cap_found}/{enriched_count} tickers have market cap data")
                print(f"\n⚠️  WARNING: Limited market cap data available ({market_cap_found}/{enriched_count} tickers)")
        
        self.logger.info("Creating DataFrame from processed data...")
        df = pd.DataFrame(processed_data)
        
        # Sort by market cap (highest first) for USD pairs, then by ticker for others
        if 'market_cap' in df.columns:
            self.logger.info("Sorting tickers by market cap...")
            # Convert market_cap to numeric for proper sorting
            df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
            
            df_usd = df[df['is_usd_pair'] == True].copy()
            df_other = df[df['is_usd_pair'] == False].copy()
            
            df_usd = df_usd.sort_values('market_cap', ascending=False, na_position='last')
            df_other = df_other.sort_values('ticker')
            
            df = pd.concat([df_usd, df_other], ignore_index=True)
        
        self.logger.info(f"Successfully processed {len(df)} tickers")
        
        return df
    
    def _get_last_update_time(self, filename: str = "crypto_tickers.csv") -> Optional[datetime]:
        """
        Get the timestamp of the last ticker update from the CSV file
        
        Returns:
            datetime object of last update, or None if file doesn't exist
        """
        filepath = os.path.join(self.config["data"]["data_directory"], filename)
        
        try:
            if not os.path.exists(filepath):
                self.logger.info(f"No existing ticker file found at {filepath}")
                return None
            
            # Read the CSV file
            df = pd.read_csv(filepath)
            
            if df.empty or 'collected_date' not in df.columns:
                self.logger.warning("CSV file exists but has no collected_date column")
                return None
            
            # Get the most recent collected_date
            last_update_str = df['collected_date'].iloc[0]
            last_update = datetime.strptime(last_update_str, '%Y-%m-%d %H:%M:%S')
            
            self.logger.info(f"Last ticker update was at: {last_update}")
            return last_update
            
        except Exception as e:
            self.logger.warning(f"Error reading last update time: {e}")
            return None
    
    def _needs_update(self, filename: str = "crypto_tickers.csv", hours: int = 24) -> bool:
        """
        Check if the ticker data needs to be updated based on last update time
        
        Args:
            filename: Name of the CSV file to check
            hours: Number of hours before update is needed (default: 24)
        
        Returns:
            True if update is needed, False otherwise
        """
        last_update = self._get_last_update_time(filename)
        
        if last_update is None:
            self.logger.info("No previous update found. Update needed.")
            return True
        
        time_since_update = datetime.now() - last_update
        hours_since_update = time_since_update.total_seconds() / 3600
        
        self.logger.info(f"Time since last update: {hours_since_update:.2f} hours")
        
        if hours_since_update >= hours:
            self.logger.info(f"Update needed (last update was {hours_since_update:.2f} hours ago)")
            return True
        else:
            self.logger.info(f"Update not needed (last update was only {hours_since_update:.2f} hours ago)")
            return False
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = "crypto_tickers.csv"):
        """
        Save ticker data to CSV file
        """
        filepath = os.path.join(self.config["data"]["data_directory"], filename)
        
        try:
            df.to_csv(filepath, index=False)
            self.logger.info(f"Successfully saved ticker data to {filepath}")
            self.logger.info(f"Total tickers saved: {len(df)}")
            
            # Print summary statistics
            self._print_summary(df)
            
        except Exception as e:
            self.logger.error(f"Failed to save ticker data to CSV: {e}")
            raise
    
    def _print_summary(self, df: pd.DataFrame):
        """
        Print summary statistics about the collected tickers
        """
        print("\n" + "="*70)
        print("📊 CRYPTOCURRENCY TICKER COLLECTION SUMMARY")
        print("="*70)
        print(f"📅 Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Total Tickers: {len(df)}")
        print(f"✅ Active Tickers: {df['active'].sum()}")
        print(f"❌ Inactive Tickers: {(~df['active']).sum()}")
        print(f"💵 USD Pairs: {df['is_usd_pair'].sum()}")
        print(f"🌍 Other Pairs: {(~df['is_usd_pair']).sum()}")
        
        # Market cap statistics
        if 'market_cap' in df.columns:
            # Convert market_cap to numeric type, coercing errors to NaN
            df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
            df_with_mcap = df[df['market_cap'].notna()]
            if len(df_with_mcap) > 0:
                total_market_cap = df_with_mcap['market_cap'].sum()
                print(f"\n💰 Market Cap Data:")
                print(f"  • Tickers with Market Cap: {len(df_with_mcap)}")
                print(f"  • Total Market Cap: ${total_market_cap:,.0f}")
                print(f"  • Average Market Cap: ${df_with_mcap['market_cap'].mean():,.0f}")
        
        # Price statistics
        if 'current_price' in df.columns:
            # Convert current_price to numeric type as well
            df['current_price'] = pd.to_numeric(df['current_price'], errors='coerce')
            df_with_price = df[df['current_price'].notna()]
            if len(df_with_price) > 0:
                print(f"\n💵 Price Data:")
                print(f"  • Tickers with Price: {len(df_with_price)}")
                print(f"  • Highest Price: ${df_with_price['current_price'].max():,.2f}")
                print(f"  • Lowest Price: ${df_with_price['current_price'].min():.8f}")
        
        # Top 10 by market cap
        if 'market_cap' in df.columns:
            # Ensure market_cap is numeric before using nlargest
            df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
            top_10 = df[df['market_cap'].notna()].nlargest(10, 'market_cap')
            if len(top_10) > 0:
                print(f"\n🏆 TOP 10 BY MARKET CAP:")
                for i, row in enumerate(top_10.itertuples(), 1):
                    symbol = row.crypto_symbol if row.crypto_symbol else row.ticker
                    price = f"${row.current_price:,.2f}" if pd.notna(row.current_price) else "N/A"
                    mcap = f"${row.market_cap:,.0f}" if pd.notna(row.market_cap) else "N/A"
                    print(f"  {i:2d}. {symbol:8s} ({row.name[:25]:25s}) - {price:>12s} | MCap: {mcap}")
        
        # Top crypto symbols (for USD pairs)
        if 'crypto_symbol' in df.columns:
            usd_pairs = df[df['is_usd_pair'] & (df['crypto_symbol'] != '')]
            if len(usd_pairs) > 0:
                print(f"\n💎 Unique Cryptocurrencies (USD Pairs): {usd_pairs['crypto_symbol'].nunique()}")
        
        # Market breakdown
        if 'market' in df.columns:
            print(f"\n🏪 Market Breakdown:")
            market_counts = df['market'].value_counts()
            for market, count in market_counts.items():
                print(f"  • {market}: {count}")
        
        print("="*70)
        print(f"💾 Data saved to: crypto_data/crypto_tickers.csv")
        print("="*70 + "\n")
    
    def run(self, enrich_data: bool = True, force_update: bool = False):
        """
        Main method to collect and save all crypto tickers
        
        Args:
            enrich_data: Whether to fetch additional market data (slower but more complete)
            force_update: Force update even if last update was less than 24 hours ago
        """
        self.logger.info("Starting crypto ticker collection process")
        
        # Check API key
        if self.api_key == "YOUR_POLYGON_API_KEY":
            self.logger.error("Please set your Polygon.io API key in config/settings.json")
            self.logger.error("Run 'python setup_polygon.py' to configure your API key")
            return
        
        # Check if update is needed (unless forced)
        if not force_update and not self._needs_update():
            print("\n⏭️  Skipping update - data is less than 24 hours old")
            print("💡 Use --force flag to update anyway")
            self.logger.info("Skipping ticker update - data is recent enough")
            return
        
        try:
            # Fetch all tickers
            tickers = self.get_all_crypto_tickers()
            
            if not tickers:
                self.logger.error("No tickers retrieved. Aborting.")
                return
            
            # Process ticker data (with or without enrichment)
            if enrich_data:
                self.logger.info("Enriching ticker data with market cap and prices (this may take a while)...")
            
            df = self.process_ticker_data(tickers, enrich_data=enrich_data)
            
            # Save to CSV
            self.save_to_csv(df)
            
            self.logger.info("Crypto ticker collection completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during ticker collection: {e}")
            raise


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Collect cryptocurrency tickers from Polygon.io'
    )
    parser.add_argument(
        '--no-enrich',
        action='store_true',
        help='Skip enrichment with market cap and price data (faster)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force update even if last update was less than 24 hours ago'
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Cryptocurrency Ticker Collector - Polygon.io")
    print("=" * 70)
    
    if args.no_enrich:
        print("⚡ Quick mode: Skipping market data enrichment")
    else:
        print("💎 Full mode: Including market cap and price data")
    
    if args.force:
        print("🔄 Force mode: Updating regardless of last update time")
    
    print()
    
    try:
        collector = CryptoTickerCollector()
        collector.run(enrich_data=not args.no_enrich, force_update=args.force)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())