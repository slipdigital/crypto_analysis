"""
Cryptocurrency Data Collector - Demo Version
Provides sample data for testing when Polygon.io API is not available
"""

import pandas as pd
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random


class CryptoDataCollectorDemo:
    """Demo version of crypto data collector with sample data"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize the demo collector"""
        self.config = self._load_config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Create directories
        self._create_directories()
        
        # Sample cryptocurrency data
        self.sample_cryptos = [
            {'ticker': 'X:BTCUSD', 'name': 'Bitcoin', 'symbol': 'BTC'},
            {'ticker': 'X:ETHUSD', 'name': 'Ethereum', 'symbol': 'ETH'},
            {'ticker': 'X:XRPUSD', 'name': 'XRP', 'symbol': 'XRP'},
            {'ticker': 'X:ADAUSD', 'name': 'Cardano', 'symbol': 'ADA'},
            {'ticker': 'X:DOTUSD', 'name': 'Polkadot', 'symbol': 'DOT'},
            {'ticker': 'X:LTCUSD', 'name': 'Litecoin', 'symbol': 'LTC'},
            {'ticker': 'X:BCHUSD', 'name': 'Bitcoin Cash', 'symbol': 'BCH'},
            {'ticker': 'X:LINKUSD', 'name': 'Chainlink', 'symbol': 'LINK'},
            {'ticker': 'X:XLMUSD', 'name': 'Stellar', 'symbol': 'XLM'},
            {'ticker': 'X:DOGEUSD', 'name': 'Dogecoin', 'symbol': 'DOGE'},
            {'ticker': 'X:UNIUSD', 'name': 'Uniswap', 'symbol': 'UNI'},
            {'ticker': 'X:AAVEUSD', 'name': 'Aave', 'symbol': 'AAVE'},
            {'ticker': 'X:ALGOUSD', 'name': 'Algorand', 'symbol': 'ALGO'},
            {'ticker': 'X:ATOMUSD', 'name': 'Cosmos', 'symbol': 'ATOM'},
            {'ticker': 'X:AVAXUSD', 'name': 'Avalanche', 'symbol': 'AVAX'},
            {'ticker': 'X:SOLUSD', 'name': 'Solana', 'symbol': 'SOL'},
            {'ticker': 'X:MATICUSD', 'name': 'Polygon', 'symbol': 'MATIC'},
            {'ticker': 'X:FTTUSD', 'name': 'FTX Token', 'symbol': 'FTT'},
            {'ticker': 'X:NEARUSD', 'name': 'NEAR Protocol', 'symbol': 'NEAR'},
            {'ticker': 'X:MANAUSD', 'name': 'Decentraland', 'symbol': 'MANA'},
            {'ticker': 'X:SANDUSD', 'name': 'The Sandbox', 'symbol': 'SAND'},
            {'ticker': 'X:CRVUSD', 'name': 'Curve DAO Token', 'symbol': 'CRV'},
            {'ticker': 'X:SUSHIUSD', 'name': 'SushiSwap', 'symbol': 'SUSHI'},
            {'ticker': 'X:COMPUSD', 'name': 'Compound', 'symbol': 'COMP'},
            {'ticker': 'X:YFIUSD', 'name': 'yearn.finance', 'symbol': 'YFI'},
            {'ticker': 'X:SNXUSD', 'name': 'Synthetix', 'symbol': 'SNX'},
            {'ticker': 'X:MKRUSD', 'name': 'Maker', 'symbol': 'MKR'},
            {'ticker': 'X:BATUSD', 'name': 'Basic Attention Token', 'symbol': 'BAT'},
            {'ticker': 'X:ZRXUSD', 'name': '0x', 'symbol': 'ZRX'},
            {'ticker': 'X:ENJUSD', 'name': 'Enjin Coin', 'symbol': 'ENJ'}
        ]
        
        self.logger.info("CryptoDataCollector (Demo Mode) initialized successfully")
    
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
        
        log_file = os.path.join(log_dir, f"crypto_collector_demo_{datetime.now().strftime('%Y%m%d')}.log")
        
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
    
    def _generate_sample_price_data(self, base_price: float, days: int = 365) -> List[Dict]:
        """Generate sample historical price data"""
        data = []
        current_price = base_price
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            
            # Simulate price movement (random walk with slight upward trend)
            change_percent = random.uniform(-0.05, 0.06)  # -5% to +6% daily change
            current_price *= (1 + change_percent)
            
            # Ensure price doesn't go negative
            current_price = max(current_price, 0.01)
            
            # Generate OHLCV data
            open_price = current_price * random.uniform(0.98, 1.02)
            close_price = current_price
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.05)
            low_price = min(open_price, close_price) * random.uniform(0.95, 1.0)
            volume = random.uniform(1000000, 10000000)
            
            bar = {
                't': int(date.timestamp() * 1000),  # timestamp in milliseconds
                'o': round(open_price, 6),
                'h': round(high_price, 6),
                'l': round(low_price, 6),
                'c': round(close_price, 6),
                'v': int(volume),
                'vw': round((open_price + high_price + low_price + close_price) / 4, 6),
                'n': random.randint(1000, 5000)
            }
            data.append(bar)
        
        return data
    
    def get_crypto_tickers(self) -> List[str]:
        """Get sample cryptocurrency tickers"""
        self.logger.info("Generating sample cryptocurrency tickers")
        
        tickers = [crypto['ticker'] for crypto in self.sample_cryptos[:self.config["data"]["top_n_cryptos"]]]
        self.logger.info(f"Generated {len(tickers)} sample cryptocurrency tickers")
        return tickers
    
    def get_ticker_details(self, ticker: str) -> Optional[Dict]:
        """Get sample ticker details"""
        for crypto in self.sample_cryptos:
            if crypto['ticker'] == ticker:
                return {
                    'ticker': ticker,
                    'name': crypto['name'],
                    'market_status': 'open',
                    'type': 'crypto',
                    'active': True,
                    'currency_name': crypto['name'],
                    'base_currency_symbol': crypto['symbol'],
                    'base_currency_name': crypto['name']
                }
        return None
    
    def get_previous_close(self, ticker: str) -> Optional[Dict]:
        """Generate sample previous close data"""
        # Base prices for different cryptocurrencies
        base_prices = {
            'X:BTCUSD': 45000, 'X:ETHUSD': 3000, 'X:XRPUSD': 0.5, 'X:ADAUSD': 0.8,
            'X:DOTUSD': 25, 'X:LTCUSD': 150, 'X:BCHUSD': 400, 'X:LINKUSD': 15,
            'X:XLMUSD': 0.3, 'X:DOGEUSD': 0.08, 'X:UNIUSD': 20, 'X:AAVEUSD': 200,
            'X:ALGOUSD': 1.5, 'X:ATOMUSD': 30, 'X:AVAXUSD': 80, 'X:SOLUSD': 100,
            'X:MATICUSD': 1.2, 'X:FTTUSD': 25, 'X:NEARUSD': 12, 'X:MANAUSD': 2.5,
            'X:SANDUSD': 3.0, 'X:CRVUSD': 4.0, 'X:SUSHIUSD': 8.0, 'X:COMPUSD': 300,
            'X:YFIUSD': 25000, 'X:SNXUSD': 10, 'X:MKRUSD': 2000, 'X:BATUSD': 0.6,
            'X:ZRXUSD': 0.8, 'X:ENJUSD': 1.5
        }
        
        base_price = base_prices.get(ticker, 10.0)
        current_price = base_price * random.uniform(0.8, 1.2)  # ±20% variation
        
        return {
            'c': round(current_price, 6),
            'o': round(current_price * random.uniform(0.98, 1.02), 6),
            'h': round(current_price * random.uniform(1.0, 1.05), 6),
            'l': round(current_price * random.uniform(0.95, 1.0), 6),
            'v': random.randint(1000000, 10000000),
            'vw': round(current_price, 6),
            'n': random.randint(1000, 5000),
            't': int(datetime.now().timestamp() * 1000)
        }
    
    def get_historical_data(self, ticker: str, days: int = None) -> Optional[Dict]:
        """Generate sample historical data"""
        if days is None:
            days = self.config["data"]["historical_days"]
        
        # Get base price for this ticker
        base_prices = {
            'X:BTCUSD': 45000, 'X:ETHUSD': 3000, 'X:XRPUSD': 0.5, 'X:ADAUSD': 0.8,
            'X:DOTUSD': 25, 'X:LTCUSD': 150, 'X:BCHUSD': 400, 'X:LINKUSD': 15,
            'X:XLMUSD': 0.3, 'X:DOGEUSD': 0.08, 'X:UNIUSD': 20, 'X:AAVEUSD': 200,
            'X:ALGOUSD': 1.5, 'X:ATOMUSD': 30, 'X:AVAXUSD': 80, 'X:SOLUSD': 100,
            'X:MATICUSD': 1.2, 'X:FTTUSD': 25, 'X:NEARUSD': 12, 'X:MANAUSD': 2.5,
            'X:SANDUSD': 3.0, 'X:CRVUSD': 4.0, 'X:SUSHIUSD': 8.0, 'X:COMPUSD': 300,
            'X:YFIUSD': 25000, 'X:SNXUSD': 10, 'X:MKRUSD': 2000, 'X:BATUSD': 0.6,
            'X:ZRXUSD': 0.8, 'X:ENJUSD': 1.5
        }
        
        base_price = base_prices.get(ticker, 10.0)
        results = self._generate_sample_price_data(base_price, days)
        
        return {
            'ticker': ticker,
            'queryCount': len(results),
            'resultsCount': len(results),
            'adjusted': True,
            'results': results
        }
    
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
        self.logger.info(f"Saved sample historical data for {ticker} to {filepath}")
    
    def save_daily_snapshot_to_csv(self, crypto_data: List[Dict]):
        """Save daily market snapshot to CSV file"""
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"{today}_demo_snapshot.csv"
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
                'current_price': price_data.get('c', 0),
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
        self.logger.info(f"Saved sample daily snapshot to {filepath}")
    
    def collect_all_data(self):
        """Main method to collect sample data"""
        self.logger.info("Starting sample data collection (Demo Mode)")
        
        # Get cryptocurrency tickers
        crypto_tickers = self.get_crypto_tickers()
        
        self.logger.info(f"Processing {len(crypto_tickers)} sample cryptocurrency tickers")
        
        # Collect data for each cryptocurrency
        crypto_data = []
        
        for i, ticker in enumerate(crypto_tickers, 1):
            self.logger.info(f"Processing {ticker} ({i}/{len(crypto_tickers)})")
            
            # Get ticker details
            ticker_details = self.get_ticker_details(ticker)
            
            # Get current price
            price_data = self.get_previous_close(ticker)
            
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
                
                if historical_data:
                    self.save_historical_data_to_csv(ticker, ticker_details, historical_data)
        
        # Save daily snapshot if enabled
        if self.config["collection"]["collect_snapshots"] and crypto_data:
            self.save_daily_snapshot_to_csv(crypto_data)
        
        self.logger.info("Sample data collection completed successfully")


def main():
    """Main function to run the demo crypto data collector"""
    try:
        collector = CryptoDataCollectorDemo()
        collector.collect_all_data()
        print("\n🎉 Demo data collection completed!")
        print("📁 Check the crypto_data/ directory for sample files")
        print("💡 This demo generates realistic sample data for testing")
    except Exception as e:
        logging.error(f"Fatal error in demo execution: {e}")
        raise


if __name__ == "__main__":
    main()