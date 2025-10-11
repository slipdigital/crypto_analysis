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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup

from base_collector import BasePolygonCollector
from models import Ticker, Base


class CryptoTickerCollector(BasePolygonCollector):
    def get_coingecko_id_map(self) -> Dict[str, str]:
        """
        Fetch all CoinGecko coins and build a symbol-to-id map (lowercase).
        Returns:
            Dict mapping symbol (lowercase) to CoinGecko id
        """
        import requests
        url = "https://api.coingecko.com/api/v3/coins/list"
        try:
            response = requests.get(url)
            response.raise_for_status()
            coins = response.json()
            # Map symbol to id, prefer first occurrence
            symbol_to_id = {}
            for coin in coins:
                symbol = coin.get('symbol', '').lower()
                cg_id = coin.get('id', '')
                if symbol and cg_id and symbol not in symbol_to_id:
                    symbol_to_id[symbol] = cg_id
            return symbol_to_id
        except Exception as e:
            self.logger.error(f"Failed to fetch CoinGecko coin list: {e}")
            return {}

    def get_coingecko_market_cap(self, cg_id: str) -> Optional[float]:
        """
        Fetch market cap for a CoinGecko id.
        Args:
            cg_id: CoinGecko id (e.g., 'bitcoin')
        Returns:
            Market cap as float or None
        """
        import requests
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            'vs_currency': 'usd',
            'ids': cg_id
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                return data[0].get('market_cap')
            else:
                self.logger.warning(f"No market cap data found for {cg_id} on CoinGecko")
                return None
        except Exception as e:
            self.logger.error(f"CoinGecko API request failed: {e}")
            return None

    def get_coingecko_market_cap_scrape(self, symbol: str) -> float:
        """
        Scrape market cap for a crypto symbol from coingecko.com
        Args:
            symbol: Crypto symbol (e.g., 'BTC', 'ETH')
        Returns:
            Market cap as float or None
        """
        import requests
        url = f"https://www.coingecko.com/en/coins/{symbol.lower()}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            # Find the market cap value (CoinGecko uses data-coin-market-cap)
            market_cap_tag = soup.find("span", {"data-target": "price.market_cap"})
            if market_cap_tag:
                market_cap_text = market_cap_tag.text.replace("$","").replace(",","").strip()
                try:
                    return float(market_cap_text)
                except Exception:
                    return None
            # Fallback: try to find by label
            for label in soup.find_all("span", class_="tw-text-gray-500"):
                if "Market Cap" in label.text:
                    parent = label.find_parent("div")
                    if parent:
                        value = parent.find("span", class_="no-wrap")
                        if value:
                            market_cap_text = value.text.replace("$","").replace(",","").strip()
                            try:
                                return float(market_cap_text)
                            except Exception:
                                return None
            return None
        except Exception as e:
            self.logger.warning(f"Web scraping CoinGecko failed for {symbol}: {e}")
            return None
    """Collector for all cryptocurrency tickers from Polygon.io"""
    
    def setup_db(self):
        """
        Set up SQLAlchemy engine and session for local Postgres database using credentials from config.
        """
        pg_cfg = self.config.get("postgres", {})
        db_url = f"postgresql+psycopg2://{pg_cfg.get('username','postgres')}:{pg_cfg.get('password','123123')}@{pg_cfg.get('host','localhost')}:{pg_cfg.get('port',5432)}/{pg_cfg.get('database','crypto_tpi')}"
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the ticker collector with configuration"""
        super().__init__(config_path)
        
        # Performance optimization settings
        self.max_workers = 10  # Number of concurrent API requests
        self.batch_size = 50  # Process tickers in batches for progress reporting
        
        self.logger.info("CryptoTickerCollector initialized successfully")
        self.setup_db()
    
    def _create_directories(self):
        """Create the necessary directories for data storage"""
        # Call the parent method first
        super()._create_directories()
        
        # Add any additional directories specific to ticker collector
        data_dir = self.config["data"]["data_directory"]
        os.makedirs(data_dir, exist_ok=True)
        self.logger.debug(f"Created/verified directory: {data_dir}")

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
        """
        Get previous close price for a cryptocurrency
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dictionary with price data or None if unavailable
        """
        self.logger.debug(f"Fetching previous close for {ticker}")
        
        endpoint = f"v2/aggs/ticker/{ticker}/prev"
        
        try:
            data = self._make_api_request(endpoint)
            
            if data and 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                
                # Validate that essential price fields exist
                if not self._validate_data(result, "price_data"):
                    self.logger.warning(f"Invalid price data structure for {ticker}")
                    return None
                
                return result
            else:
                self.logger.debug(f"No previous close data for {ticker}")
                return None
                
        except Exception as e:
            self.logger.error(f"Unexpected error fetching previous close for {ticker}: {e}")
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
        """Batch fetches previous close data for multiple tickers
            
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

    def get_top100_market_caps(self) -> dict:
        """
        Scrape the CoinGecko homepage for the top 100 crypto market caps.
        Returns:
            Dict mapping symbol (uppercase) to market cap (float)
        """
        import requests
        from bs4 import BeautifulSoup
        url = "https://www.coingecko.com/"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            # Find all table rows in the top 100 table
            rows = soup.find_all("tr")
            market_caps = {}
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 8:
                    continue
                # Symbol is usually in the third column (index 2)
                symbol_candidates = cols[2].find_all(text=True)
                symbol = None
                for candidate in symbol_candidates:
                    candidate = candidate.strip().upper()
                    if candidate.isalpha() and len(candidate) <= 6:
                        symbol = candidate
                        break
                if not symbol:
                    continue
                # Market cap is usually in the eighth column (index 7)
                mcap_text = cols[7].get_text().replace("$","").replace(",","").replace("--","").strip()
                try:
                    market_cap = float(mcap_text)
                except Exception:
                    continue
                market_caps[symbol] = market_cap
            return market_caps
        except Exception as e:
            self.logger.warning(f"Failed to scrape top 100 market caps from CoinGecko: {e}")
            return {}

    def get_crypto_overview_batch(self, crypto_symbols: list) -> dict:
        """
        Batch fetch market cap and overview data for crypto symbols using CoinGecko homepage scrape.
        Args:
            crypto_symbols: List of crypto symbols (e.g., ['BTC', 'ETH', 'XRP'])
        Returns:
            Dictionary mapping crypto symbol to overview data (market_cap field)
        """
        self.logger.info(f"Scraping CoinGecko homepage for top 100 market caps...")
        top100_caps = self.get_top100_market_caps()
        overview_map = {}
        for symbol in crypto_symbols:
            mcap = top100_caps.get(symbol.upper())
            overview_map[symbol] = {'market_cap': mcap} if mcap is not None else None
        self.logger.info(f"Top 100 market cap scrape complete. Found data for {sum(1 for v in overview_map.values() if v)} symbols")
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
            
            # Extract market_cap from ticker_info or overview_data if present
            if ticker_info and 'market_cap' in ticker_info:
                market_data['market_cap'] = ticker_info['market_cap']
            elif overview_data and 'market_cap' in overview_data:
                market_data['market_cap'] = overview_data['market_cap']
        
        except Exception as e:
            self.logger.warning(f"Error enriching {ticker}: {e}")
        
        return market_data

    def process_ticker_data(self, tickers: List[Dict], enrich_data: bool = True, market_cap_only: bool = False) -> pd.DataFrame:
        """
        Process raw ticker data into a structured DataFrame
        
        Args:
            tickers: List of ticker dictionaries from Polygon.io
            enrich_data: Whether to fetch additional market data (price, market cap)
            market_cap_only: If True, only update market cap (skip price enrichment)
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
    
    def _get_last_update_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last ticker update from the database
        Returns:
            datetime object of last update, or None if no records exist
        """
        session = self.Session()
        try:
            last_ticker = session.query(Ticker).order_by(Ticker.collected_date.desc()).first()
            if last_ticker and last_ticker.collected_date:
                self.logger.info(f"Last ticker update was at: {last_ticker.collected_date}")
                return last_ticker.collected_date
            else:
                self.logger.info("No existing ticker records found in database")
                return None
        except Exception as e:
            self.logger.warning(f"Error reading last update time from database: {e}")
            return None
        finally:
            session.close()

    def _needs_update(self, hours: int = 24) -> bool:
        """
        Check if the ticker data needs to be updated based on last update time in the database
        Args:
            hours: Number of hours before update is needed (default: 24)
        Returns:
            True if update is needed, False otherwise
        """
        last_update = self._get_last_update_time()
        if last_update is None:
            self.logger.info("No previous update found in database. Update needed.")
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
    
    def save_to_db(self, df: pd.DataFrame):
        """
        Save ticker data to local Postgres database using SQLAlchemy ORM.
        """
        session = self.Session()
        try:
            for row in df.to_dict(orient='records'):
                ticker_obj = session.query(Ticker).filter_by(ticker=row['ticker']).first()
                if ticker_obj:
                    for key, value in row.items():
                        setattr(ticker_obj, key, value)
                else:
                    ticker_obj = Ticker(**row)
                    session.add(ticker_obj)
            session.commit()
            self.logger.info(f"Successfully saved {len(df)} tickers to database.")
            self._print_summary(df)
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to save ticker data to database: {e}")
            raise
        finally:
            session.close()
    
    def update_market_caps_only(self, df: pd.DataFrame):
        """
        Update only the market cap field for tickers in the database.
        """
        session = self.Session()
        try:
            for row in df.to_dict(orient='records'):
                ticker_obj = session.query(Ticker).filter_by(ticker=row['ticker']).first()
                if ticker_obj and row.get('market_cap') is not None:
                    ticker_obj.market_cap = row['market_cap']
            session.commit()
            self.logger.info(f"Successfully updated market cap for {len(df)} tickers in database.")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to update market cap in database: {e}")
            raise
        finally:
            session.close()

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
        print(f"💾 Data saved")
        print("="*70 + "\n")

    def run(self, enrich_data: bool = True, force_update: bool = False, top10: bool = False,
            single_ticker: Optional[str] = None, market_cap_only: bool = False):
        self.logger.info("Starting crypto ticker collection process")

        # Skip last_updated check if single_ticker is set
        if not single_ticker and not force_update and not self._needs_update():
            print("\n⏭️  Skipping update - data is less than 24 hours old")
            print("💡 Use --force flag to update anyway")
            self.logger.info("Skipping ticker update - data is recent enough")
            return

        try:
            if single_ticker:
                self.logger.info(f"Updating only single ticker: {single_ticker}")
                tickers = [self.get_ticker_details(single_ticker)]
                tickers = [t for t in tickers if t]  # Remove None if not found
            else:
                tickers = self.get_all_crypto_tickers()
                if not tickers:
                    self.logger.error("No tickers retrieved. Aborting.")
                    return
                if top10:
                    tickers = tickers[:10]
                    self.logger.info("Limiting collection to the first 10 cryptocurrencies")

            df = self.process_ticker_data(tickers, enrich_data=enrich_data, market_cap_only=market_cap_only)
            if market_cap_only:
                self.update_market_caps_only(df)
            else:
                self.save_to_db(df)
            self.logger.info("Crypto ticker collection completed successfully")

        except Exception as e:
            self.logger.error(f"Error during ticker collection: {e}")
            raise


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Collect cryptocurrency tickers from Polygon.io and save to crypto_tickers.csv'
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
    parser.add_argument(
        '--ticker',
        type=str,
        help='Update only a single ticker (e.g., X:BTCUSD)'
    )
    parser.add_argument(
        '--market-cap-only',
        action='store_true',
        help='Update only market cap data for tickers in the database'
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
    
    if args.market_cap_only:
        print("🟢 Market Cap Only mode: Only updating market cap data")
    
    print()
    
    try:
        collector = CryptoTickerCollector()
        collector.run(
            enrich_data=not args.no_enrich,
            force_update=args.force,
            top10=args.top10 if hasattr(args, 'top10') else False,
            single_ticker=args.ticker,
            market_cap_only=args.market_cap_only
        )
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())