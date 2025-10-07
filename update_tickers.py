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

from base_collector import BasePolygonCollector


class CryptoTickerCollector(BasePolygonCollector):
    """Collector for all cryptocurrency tickers from Polygon.io"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the ticker collector with configuration"""
        super().__init__(config_path)
        
        # Performance optimization settings
        self.max_workers = 10  # Number of concurrent API requests
        self.batch_size = 50  # Process tickers in batches for progress reporting
        
        self.logger.info("CryptoTickerCollector initialized successfully")
    
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