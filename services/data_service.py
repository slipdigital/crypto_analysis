"""
Data Service Layer for Flask Crypto Dashboard
Interfaces with existing cryptocurrency data collection system
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from data_utils import CryptoDataUtils
from market_cap.market_cap_report import MarketCapReportGenerator
from crypto_performance.performance_report import CryptoPerformanceAnalyzer

class CryptoDataService:
    """Service layer for accessing cryptocurrency data"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the data service"""
        self.config_path = config_path
        self.config = self._load_config()
        self.data_utils = CryptoDataUtils(config_path)
        self.market_cap_generator = MarketCapReportGenerator(config_path)
        self.performance_analyzer = CryptoPerformanceAnalyzer(config_path)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {self.config_path}")
            return {
                "data": {
                    "historical_directory": "crypto_data/historical",
                    "snapshots_directory": "crypto_data/daily_snapshots"
                }
            }
    
    def get_available_cryptocurrencies(self) -> List[Dict[str, str]]:
        """Get list of available cryptocurrencies with metadata"""
        try:
            # Get available tickers from historical data
            tickers = self.data_utils.get_available_cryptocurrencies()
            
            # Map tickers to readable names using market cap data
            crypto_list = []
            for ticker in tickers:
                # Convert ticker format for lookup
                lookup_ticker = ticker.replace('_', ':')
                
                # Get symbol and name from market cap generator
                supply_info = self.market_cap_generator.crypto_supply_data.get(lookup_ticker, {})
                symbol = supply_info.get('symbol', ticker.replace('X_', '').replace('USD', ''))
                name = supply_info.get('name', symbol)
                
                crypto_list.append({
                    'ticker': ticker,
                    'symbol': symbol,
                    'name': name,
                    'lookup_ticker': lookup_ticker
                })
            
            return sorted(crypto_list, key=lambda x: x['symbol'])
            
        except Exception as e:
            self.logger.error(f"Error getting available cryptocurrencies: {e}")
            return []
    
    def get_historical_data(self, ticker: str, days: int = 30) -> Optional[pd.DataFrame]:
        """Get historical data for a cryptocurrency"""
        try:
            df = self.data_utils.load_historical_data(ticker)
            if df is not None and days > 0:
                # Get last N days
                df = df.tail(days)
            return df
        except Exception as e:
            self.logger.error(f"Error loading historical data for {ticker}: {e}")
            return None
    
    def get_latest_snapshot(self) -> Optional[pd.DataFrame]:
        """Get the latest market snapshot"""
        try:
            return self.market_cap_generator.load_latest_snapshot()
        except Exception as e:
            self.logger.error(f"Error loading latest snapshot: {e}")
            return None
    
    def get_market_cap_data(self) -> List[Dict]:
        """Get market cap data for all cryptocurrencies"""
        try:
            # Load latest snapshot
            snapshot_df = self.get_latest_snapshot()
            if snapshot_df is None:
                return []
            
            # Calculate market caps
            market_cap_df = self.market_cap_generator.calculate_market_caps(snapshot_df)
            
            # Convert to list of dictionaries
            return market_cap_df.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error getting market cap data: {e}")
            return []
    
    def get_performance_data(self) -> List[Dict]:
        """Get performance analysis data"""
        try:
            # Get top 10 cryptocurrencies by market cap
            top_10_cryptos = self.performance_analyzer.get_top_10_by_market_cap()
            
            if not top_10_cryptos:
                return []
            
            # Analyze performance for each
            analysis_results = []
            for crypto in top_10_cryptos:
                result = self.performance_analyzer.analyze_crypto_performance(crypto)
                if 'error' not in result:
                    analysis_results.append(result)
            
            # Sort by momentum score
            analysis_results.sort(key=lambda x: x['momentum_score'], reverse=True)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error getting performance data: {e}")
            return []
    
    def get_price_data(self, ticker: str, period: str = '30d') -> Dict[str, Any]:
        """Get price data for charts"""
        try:
            # Parse period
            period_days = self._parse_period(period)
            
            # Get historical data
            df = self.get_historical_data(ticker, period_days)
            if df is None or df.empty:
                return {}
            
            # Prepare data for charts
            chart_data = {
                'dates': df['date'].dt.strftime('%Y-%m-%d').tolist(),
                'prices': df['close'].tolist(),
                'volumes': df.get('volume', [0] * len(df)).tolist(),
                'highs': df['high'].tolist(),
                'lows': df['low'].tolist(),
                'opens': df['open'].tolist()
            }
            
            # Calculate additional metrics
            if len(df) > 1:
                latest_price = df['close'].iloc[-1]
                previous_price = df['close'].iloc[-2]
                price_change = latest_price - previous_price
                price_change_percent = (price_change / previous_price) * 100
                
                chart_data.update({
                    'latest_price': latest_price,
                    'price_change': price_change,
                    'price_change_percent': price_change_percent,
                    'period_high': df['high'].max(),
                    'period_low': df['low'].min(),
                    'period_volume': df.get('volume', pd.Series([0])).sum()
                })
            
            return chart_data
            
        except Exception as e:
            self.logger.error(f"Error getting price data for {ticker}: {e}")
            return {}
    
    def _parse_period(self, period: str) -> int:
        """Parse period string to number of days"""
        period_map = {
            '1d': 1,
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365
        }
        return period_map.get(period.lower(), 30)
    
    def get_last_update_time(self) -> Optional[str]:
        """Get the timestamp of the last data update"""
        try:
            snapshot_df = self.get_latest_snapshot()
            if snapshot_df is not None and not snapshot_df.empty:
                return snapshot_df.iloc[0]['date']
            return None
        except Exception as e:
            self.logger.error(f"Error getting last update time: {e}")
            return None
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of available data"""
        try:
            summary = self.data_utils.generate_summary_report()
            
            # Add additional dashboard-specific info
            summary['dashboard_info'] = {
                'last_update': self.get_last_update_time(),
                'available_cryptos_count': len(self.get_available_cryptocurrencies()),
                'has_market_cap_data': len(self.get_market_cap_data()) > 0,
                'has_performance_data': len(self.get_performance_data()) > 0
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting data summary: {e}")
            return {}
    
    def validate_ticker(self, ticker: str) -> bool:
        """Validate if a ticker has available data"""
        try:
            available_cryptos = self.get_available_cryptocurrencies()
            valid_tickers = [crypto['ticker'] for crypto in available_cryptos]
            valid_symbols = [crypto['symbol'] for crypto in available_cryptos]
            
            return ticker in valid_tickers or ticker in valid_symbols
            
        except Exception as e:
            self.logger.error(f"Error validating ticker {ticker}: {e}")
            return False
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict[str, str]]:
        """Get information about a specific ticker"""
        try:
            available_cryptos = self.get_available_cryptocurrencies()
            
            # Search by ticker or symbol
            for crypto in available_cryptos:
                if crypto['ticker'] == ticker or crypto['symbol'] == ticker:
                    return crypto
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting ticker info for {ticker}: {e}")
            return None