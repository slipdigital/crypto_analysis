import pandas as pd
import numpy as np
import os
import glob
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG
import warnings
warnings.filterwarnings('ignore')

class CryptoDataLoader:
    """
    Utility class to load and prepare cryptocurrency data for backtesting
    """
    
    def __init__(self, data_folder='crypto_data/historical'):
        self.data_folder = data_folder
        
    def list_available_cryptos(self):
        """List all available cryptocurrency CSV files"""
        csv_files = glob.glob(os.path.join(self.data_folder, "*.csv"))
        crypto_names = []
        for file in csv_files:
            filename = os.path.basename(file)
            # Extract crypto name from filename (e.g., X_BTCUSD_historical.csv -> BTC)
            if filename.startswith('X_') and filename.endswith('_historical.csv'):
                crypto_name = filename.replace('X_', '').replace('USD_historical.csv', '')
                crypto_names.append((crypto_name, file))
        return crypto_names
    
    def load_crypto_data(self, crypto_file):
        """
        Load cryptocurrency data and format it for backtesting.py
        
        Args:
            crypto_file (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Formatted data with OHLCV columns
        """
        try:
            # Load the data
            df = pd.read_csv(crypto_file)
            
            # Print original columns for debugging
            print(f"Original columns: {list(df.columns)}")
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Common column mappings
            column_mappings = {
                'timestamp': 'Date',
                'date': 'Date', 
                'time': 'Date',
                'datetime': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low', 
                'close': 'Close',
                'volume': 'Volume',
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'c': 'Close',
                'v': 'Volume'
            }
            
            # Rename columns
            for old_col, new_col in column_mappings.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Ensure we have the required columns
            required_cols = ['Open', 'High', 'Low', 'Close']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"Missing required columns: {missing_cols}")
                print(f"Available columns: {list(df.columns)}")
                return None
            
            # Handle Date column
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.set_index('Date')
            else:
                # Try to use index as date
                df.index = pd.to_datetime(df.index)
                df.index.name = 'Date'
            
            # Ensure Volume column exists
            if 'Volume' not in df.columns:
                df['Volume'] = 1000000  # Default volume if not available
            
            # Sort by date
            df = df.sort_index()
            
            # Remove any rows with NaN values in OHLC
            df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
            
            # Ensure proper data types
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"Data loaded successfully: {len(df)} records")
            print(f"Date range: {df.index.min()} to {df.index.max()}")
            print(f"Final columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            print(f"Error loading data from {crypto_file}: {e}")
            return None

class MovingAverageCrossover(Strategy):
    """
    Simple Moving Average Crossover Strategy
    Buy when short MA crosses above long MA
    Sell when short MA crosses below long MA
    """
    
    # Strategy parameters
    short_window = 20
    long_window = 50
    
    def init(self):
        # Calculate moving averages
        self.sma_short = self.I(SMA, self.data.Close, self.short_window)
        self.sma_long = self.I(SMA, self.data.Close, self.long_window)
    
    def next(self):
        # If short MA crosses above long MA, buy
        if crossover(self.sma_short, self.sma_long):
            self.buy()
        
        # If short MA crosses below long MA, sell
        elif crossover(self.sma_long, self.sma_short):
            self.sell()

class RSIStrategy(Strategy):
    """
    RSI-based strategy
    Buy when RSI < 30 (oversold)
    Sell when RSI > 70 (overbought)
    """
    
    rsi_window = 14
    rsi_lower = 30
    rsi_upper = 70
    
    def init(self):
        self.rsi = self.I(self.RSI, self.data.Close, self.rsi_window)
    
    def RSI(self, close, window):
        """Calculate RSI indicator"""
        delta = pd.Series(close).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def next(self):
        if self.rsi[-1] < self.rsi_lower and not self.position:
            self.buy()
        elif self.rsi[-1] > self.rsi_upper and self.position:
            self.sell()

class BuyAndHold(Strategy):
    """
    Simple Buy and Hold strategy for comparison
    """
    
    def init(self):
        pass
    
    def next(self):
        if not self.position:
            self.buy()

class CryptoBacktester:
    """
    Main backtesting class that orchestrates the entire process
    """
    
    def __init__(self, data_folder='crypto_data/historical'):
        self.data_loader = CryptoDataLoader(data_folder)
        self.results = {}
        
    def run_backtest(self, crypto_name, strategy_class, **strategy_params):
        """
        Run backtest for a specific cryptocurrency and strategy
        
        Args:
            crypto_name (str): Name of the cryptocurrency (e.g., 'BTC', 'SOL')
            strategy_class: Strategy class to use
            **strategy_params: Parameters for the strategy
            
        Returns:
            dict: Backtest results
        """
        # Find the data file
        available_cryptos = self.data_loader.list_available_cryptos()
        crypto_file = None
        
        for name, file_path in available_cryptos:
            if name.upper() == crypto_name.upper():
                crypto_file = file_path
                break
        
        if not crypto_file:
            print(f"Cryptocurrency {crypto_name} not found. Available: {[name for name, _ in available_cryptos]}")
            return None
        
        # Load data
        data = self.data_loader.load_crypto_data(crypto_file)
        if data is None:
            return None
        
        # Set strategy parameters
        if strategy_params:
            for param, value in strategy_params.items():
                setattr(strategy_class, param, value)
        
        # Run backtest
        bt = Backtest(data, strategy_class, cash=10000, commission=.002)
        result = bt.run()
        
        # Store results
        key = f"{crypto_name}_{strategy_class.__name__}"
        self.results[key] = {
            'crypto': crypto_name,
            'strategy': strategy_class.__name__,
            'result': result,
            'backtest': bt
        }
        
        return result
    
    def run_multiple_cryptos(self, crypto_list, strategy_class, **strategy_params):
        """
        Run backtest for multiple cryptocurrencies with the same strategy
        
        Args:
            crypto_list (list): List of cryptocurrency names
            strategy_class: Strategy class to use
            **strategy_params: Parameters for the strategy
            
        Returns:
            dict: Results for all cryptocurrencies
        """
        results = {}
        
        for crypto in crypto_list:
            print(f"\n--- Running backtest for {crypto} ---")
            result = self.run_backtest(crypto, strategy_class, **strategy_params)
            if result is not None:
                results[crypto] = result
                print(f"Return: {result['Return [%]']:.2f}%")
                print(f"Sharpe Ratio: {result['Sharpe Ratio']:.2f}")
                print(f"Max Drawdown: {result['Max. Drawdown [%]']:.2f}%")
        
        return results
    
    def compare_strategies(self, crypto_name, strategies):
        """
        Compare multiple strategies on the same cryptocurrency
        
        Args:
            crypto_name (str): Name of the cryptocurrency
            strategies (list): List of strategy classes
            
        Returns:
            pd.DataFrame: Comparison results
        """
        comparison_data = []
        
        for strategy_class in strategies:
            print(f"\n--- Testing {strategy_class.__name__} on {crypto_name} ---")
            result = self.run_backtest(crypto_name, strategy_class)
            
            if result is not None:
                comparison_data.append({
                    'Strategy': strategy_class.__name__,
                    'Return [%]': result['Return [%]'],
                    'Sharpe Ratio': result['Sharpe Ratio'],
                    'Max Drawdown [%]': result['Max. Drawdown [%]'],
                    'Win Rate [%]': result['Win Rate [%]'],
                    'Total Trades': result['# Trades']
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df = comparison_df.sort_values('Return [%]', ascending=False)
            return comparison_df
        
        return None
    
    def show_plot(self, crypto_name, strategy_class):
        """
        Show interactive plot for a specific backtest
        
        Args:
            crypto_name (str): Name of the cryptocurrency
            strategy_class: Strategy class
        """
        key = f"{crypto_name}_{strategy_class.__name__}"
        if key in self.results:
            self.results[key]['backtest'].plot()
        else:
            print(f"No results found for {crypto_name} with {strategy_class.__name__}")
    
    def get_available_cryptos(self):
        """Get list of available cryptocurrencies"""
        return [name for name, _ in self.data_loader.list_available_cryptos()]

def main():
    """
    Example usage of the crypto backtesting framework
    """
    # Initialize backtester
    backtester = CryptoBacktester()
    
    # Show available cryptocurrencies
    available_cryptos = backtester.get_available_cryptos()
    print("Available cryptocurrencies:")
    for crypto in available_cryptos:
        print(f"  - {crypto}")
    
    if not available_cryptos:
        print("No cryptocurrency data found in crypto_data/historical/")
        return
    
    # Test with first few available cryptos
    test_cryptos = available_cryptos[:3] if len(available_cryptos) >= 3 else available_cryptos
    
    print(f"\n=== Testing Moving Average Crossover Strategy ===")
    ma_results = backtester.run_multiple_cryptos(
        test_cryptos, 
        MovingAverageCrossover,
        short_window=20,
        long_window=50
    )
    
    print(f"\n=== Testing RSI Strategy ===")
    rsi_results = backtester.run_multiple_cryptos(
        test_cryptos,
        RSIStrategy,
        rsi_window=14,
        rsi_lower=30,
        rsi_upper=70
    )
    
    # Compare strategies on the first available crypto
    if test_cryptos:
        first_crypto = test_cryptos[0]
        print(f"\n=== Strategy Comparison for {first_crypto} ===")
        comparison = backtester.compare_strategies(
            first_crypto,
            [MovingAverageCrossover, RSIStrategy, BuyAndHold]
        )
        
        if comparison is not None:
            print(comparison.to_string(index=False))
            
            # Show plot for best performing strategy
            best_strategy_name = comparison.iloc[0]['Strategy']
            strategy_map = {
                'MovingAverageCrossover': MovingAverageCrossover,
                'RSIStrategy': RSIStrategy,
                'BuyAndHold': BuyAndHold
            }
            
            if best_strategy_name in strategy_map:
                print(f"\nShowing plot for best strategy: {best_strategy_name}")
                backtester.show_plot(first_crypto, strategy_map[best_strategy_name])

if __name__ == "__main__":
    main()