# Cryptocurrency Backtesting Framework

A comprehensive backtesting system for cryptocurrency trading strategies using the `backtesting.py` library. This framework can test any cryptocurrency data available in CSV format within the `crypto_data` folder.

## Features

- **Multiple Trading Strategies**: Moving Average Crossover, RSI-based, and Buy & Hold strategies
- **Multi-Cryptocurrency Support**: Test strategies across all available cryptocurrencies
- **Performance Metrics**: Return, Sharpe Ratio, Max Drawdown, Win Rate, and more
- **Strategy Comparison**: Compare multiple strategies on the same cryptocurrency
- **Interactive Visualizations**: Generate interactive plots for backtest results
- **Flexible Data Loading**: Automatically handles different CSV formats and column names

## Installation

Make sure you have the required dependencies installed:

```bash
pip install backtesting pandas numpy matplotlib seaborn
```

## Quick Start

### 1. Basic Usage

Run the example script to test Solana and other cryptocurrencies:

```bash
python run_crypto_backtest.py
```

### 2. Custom Backtesting

```python
from crypto_backtest import CryptoBacktester, MovingAverageCrossover, RSIStrategy, BuyAndHold

# Initialize backtester
backtester = CryptoBacktester()

# Test a single cryptocurrency with Moving Average strategy
result = backtester.run_backtest('SOL', MovingAverageCrossover)
print(f"Return: {result['Return [%]']:.2f}%")

# Compare multiple strategies on Bitcoin
comparison = backtester.compare_strategies('BTC', [MovingAverageCrossover, RSIStrategy, BuyAndHold])
print(comparison)

# Test multiple cryptocurrencies with the same strategy
cryptos = ['BTC', 'ETH', 'SOL', 'ADA']
results = backtester.run_multiple_cryptos(cryptos, MovingAverageCrossover)
```

## Available Strategies

### 1. Moving Average Crossover
- **Signal**: Buy when short MA crosses above long MA, sell when short MA crosses below long MA
- **Parameters**: 
  - `short_window` (default: 20)
  - `long_window` (default: 50)

### 2. RSI Strategy
- **Signal**: Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)
- **Parameters**:
  - `rsi_window` (default: 14)
  - `rsi_lower` (default: 30)
  - `rsi_upper` (default: 70)

### 3. Buy and Hold
- **Signal**: Buy at the beginning and hold throughout the period
- **Use**: Benchmark strategy for comparison

## Data Format

The framework automatically handles CSV files with the following column formats:

### Required Columns (any of these names):
- **Date/Time**: `date`, `timestamp`, `time`, `datetime`
- **Open**: `open`, `o`
- **High**: `high`, `h`
- **Low**: `low`, `l`
- **Close**: `close`, `c`
- **Volume**: `volume`, `v` (optional, will use default if missing)

### Example CSV Structure:
```csv
date,open,high,low,close,volume
2024-01-01,100.0,105.0,98.0,103.0,1000000
2024-01-02,103.0,108.0,101.0,106.0,1200000
```

## Performance Metrics

The framework provides comprehensive performance metrics:

- **Return [%]**: Total return percentage
- **Sharpe Ratio**: Risk-adjusted return measure
- **Max Drawdown [%]**: Maximum peak-to-trough decline
- **Win Rate [%]**: Percentage of profitable trades
- **Total Trades**: Number of trades executed
- **Volatility**: Annualized volatility
- **Calmar Ratio**: Return to max drawdown ratio

## Example Results

```
=== Testing SOL ===

--- Moving Average Crossover Strategy ---
Return: -23.55%
Sharpe Ratio: -0.31
Max Drawdown: -47.46%
Win Rate: 33.33%
Total Trades: 3

--- Strategy Comparison ---
              Strategy  Return [%]  Sharpe Ratio  Max Drawdown [%]  Win Rate [%]  Total Trades
            BuyAndHold   44.45%      0.30         -59.60%          100.00%       1
MovingAverageCrossover  -23.55%     -0.31        -47.46%          33.33%        3
           RSIStrategy  -52.29%     -1.02        -65.22%          0.00%         9
```

## Advanced Usage

### Custom Strategy Parameters

```python
# Custom Moving Average parameters
result = backtester.run_backtest('BTC', MovingAverageCrossover, 
                                short_window=10, long_window=30)

# Custom RSI parameters
result = backtester.run_backtest('ETH', RSIStrategy,
                                rsi_window=21, rsi_lower=25, rsi_upper=75)
```

### Interactive Plots

```python
# Show interactive plot for the best strategy
backtester.show_plot('SOL', MovingAverageCrossover)
```

### Creating Custom Strategies

```python
from backtesting import Strategy
from backtesting.lib import crossover

class CustomStrategy(Strategy):
    param1 = 10
    param2 = 20
    
    def init(self):
        # Initialize indicators
        self.indicator = self.I(some_indicator, self.data.Close, self.param1)
    
    def next(self):
        # Define trading logic
        if some_condition:
            self.buy()
        elif some_other_condition:
            self.sell()

# Use custom strategy
result = backtester.run_backtest('BTC', CustomStrategy)
```

## Available Cryptocurrencies

The framework automatically detects all CSV files in the `crypto_data/historical/` folder. Current available cryptocurrencies include:

- Bitcoin (BTC)
- Ethereum (ETH) 
- Solana (SOL)
- Cardano (ADA)
- And 25+ others

To see all available cryptocurrencies:

```python
backtester = CryptoBacktester()
print(backtester.get_available_cryptos())
```

## File Structure

```
crypto_backtest.py          # Main backtesting framework
run_crypto_backtest.py      # Example usage script
crypto_data/
  historical/
    X_BTCUSD_historical.csv  # Bitcoin data
    X_SOLUSD_historical.csv  # Solana data
    ...                      # Other cryptocurrency data
```

## Tips for Better Results

1. **Strategy Parameters**: Experiment with different parameters for each strategy
2. **Time Periods**: Consider different time periods for analysis
3. **Risk Management**: Implement stop-loss and take-profit levels
4. **Multiple Timeframes**: Test strategies on different timeframes
5. **Walk-Forward Analysis**: Use rolling windows for more robust testing
6. **Transaction Costs**: Consider realistic commission rates (default: 0.2%)

## Troubleshooting

### Common Issues:

1. **"No cryptocurrency data found"**: Ensure CSV files are in `crypto_data/historical/`
2. **"Missing required columns"**: Check that CSV has OHLC data with proper column names
3. **"Data loading error"**: Verify CSV format and date column format

### Data Requirements:

- Minimum 50+ data points for meaningful results
- Consistent date format
- No missing values in OHLC data
- Proper numeric format for price data

## Contributing

To add new strategies:

1. Create a new class inheriting from `Strategy`
2. Implement `init()` and `next()` methods
3. Add to the strategy comparison in `run_crypto_backtest.py`

## License

This framework is provided as-is for educational and research purposes.