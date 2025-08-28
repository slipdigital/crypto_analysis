#!/usr/bin/env python3
"""
Simple script to run cryptocurrency backtests using the crypto_backtest framework
"""

from crypto_backtest import CryptoBacktester, MovingAverageCrossover, RSIStrategy, BuyAndHold
import pandas as pd

def run_single_crypto_test(crypto_name='SOL'):
    """
    Run a comprehensive test on a single cryptocurrency
    """
    print(f"=== Testing {crypto_name} ===")
    
    # Initialize backtester
    backtester = CryptoBacktester()
    
    # Check if crypto is available
    available_cryptos = backtester.get_available_cryptos()
    if crypto_name not in available_cryptos:
        print(f"Cryptocurrency {crypto_name} not found.")
        print(f"Available cryptocurrencies: {available_cryptos}")
        return
    
    # Test Moving Average Crossover Strategy
    print(f"\n--- Moving Average Crossover Strategy ---")
    ma_result = backtester.run_backtest(crypto_name, MovingAverageCrossover)
    if ma_result is not None:
        print(f"Return: {ma_result['Return [%]']:.2f}%")
        print(f"Sharpe Ratio: {ma_result['Sharpe Ratio']:.2f}")
        print(f"Max Drawdown: {ma_result['Max. Drawdown [%]']:.2f}%")
        print(f"Win Rate: {ma_result['Win Rate [%]']:.2f}%")
        print(f"Total Trades: {ma_result['# Trades']}")
    
    # Test RSI Strategy
    print(f"\n--- RSI Strategy ---")
    rsi_result = backtester.run_backtest(crypto_name, RSIStrategy)
    if rsi_result is not None:
        print(f"Return: {rsi_result['Return [%]']:.2f}%")
        print(f"Sharpe Ratio: {rsi_result['Sharpe Ratio']:.2f}")
        print(f"Max Drawdown: {rsi_result['Max. Drawdown [%]']:.2f}%")
        print(f"Win Rate: {rsi_result['Win Rate [%]']:.2f}%")
        print(f"Total Trades: {rsi_result['# Trades']}")
    
    # Test Buy and Hold
    print(f"\n--- Buy and Hold Strategy ---")
    bh_result = backtester.run_backtest(crypto_name, BuyAndHold)
    if bh_result is not None:
        print(f"Return: {bh_result['Return [%]']:.2f}%")
        print(f"Sharpe Ratio: {bh_result['Sharpe Ratio']:.2f}")
        print(f"Max Drawdown: {bh_result['Max. Drawdown [%]']:.2f}%")
    
    # Compare all strategies
    print(f"\n--- Strategy Comparison ---")
    comparison = backtester.compare_strategies(
        crypto_name,
        [MovingAverageCrossover, RSIStrategy, BuyAndHold]
    )
    
    if comparison is not None:
        print(comparison.to_string(index=False))
        
        # Show plot for the best strategy
        best_strategy_name = comparison.iloc[0]['Strategy']
        print(f"\nBest performing strategy: {best_strategy_name}")
        
        # Uncomment the line below to show interactive plot
        # strategy_map = {
        #     'MovingAverageCrossover': MovingAverageCrossover,
        #     'RSIStrategy': RSIStrategy,
        #     'BuyAndHold': BuyAndHold
        # }
        # backtester.show_plot(crypto_name, strategy_map[best_strategy_name])

def run_multiple_crypto_test():
    """
    Run tests on multiple cryptocurrencies
    """
    print("=== Multiple Cryptocurrency Test ===")
    
    # Initialize backtester
    backtester = CryptoBacktester()
    
    # Get available cryptocurrencies
    available_cryptos = backtester.get_available_cryptos()
    print(f"Available cryptocurrencies: {available_cryptos}")
    
    if not available_cryptos:
        print("No cryptocurrency data found!")
        return
    
    # Test with first 5 cryptos (or all if less than 5)
    test_cryptos = available_cryptos[:5] if len(available_cryptos) >= 5 else available_cryptos
    
    print(f"\nTesting with: {test_cryptos}")
    
    # Run Moving Average strategy on multiple cryptos
    print(f"\n--- Moving Average Crossover Results ---")
    ma_results = backtester.run_multiple_cryptos(test_cryptos, MovingAverageCrossover)
    
    # Create summary table
    if ma_results:
        summary_data = []
        for crypto, result in ma_results.items():
            summary_data.append({
                'Crypto': crypto,
                'Return [%]': result['Return [%]'],
                'Sharpe Ratio': result['Sharpe Ratio'],
                'Max Drawdown [%]': result['Max. Drawdown [%]'],
                'Win Rate [%]': result['Win Rate [%]'],
                'Total Trades': result['# Trades']
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values('Return [%]', ascending=False)
        
        print("\n--- Summary Results (Sorted by Return) ---")
        print(summary_df.to_string(index=False))

def main():
    """
    Main function to run various backtesting scenarios
    """
    print("Crypto Backtesting Framework")
    print("=" * 50)
    
    # Initialize backtester to check available data
    backtester = CryptoBacktester()
    available_cryptos = backtester.get_available_cryptos()
    
    if not available_cryptos:
        print("No cryptocurrency data found in crypto_data/historical/")
        print("Please ensure CSV files are present in the correct format.")
        return
    
    print(f"Found {len(available_cryptos)} cryptocurrencies: {available_cryptos}")
    
    # Run single crypto test (Solana if available, otherwise first available)
    test_crypto = 'SOL' if 'SOL' in available_cryptos else available_cryptos[0]
    run_single_crypto_test(test_crypto)
    
    print("\n" + "=" * 50)
    
    # Run multiple crypto test
    run_multiple_crypto_test()

if __name__ == "__main__":
    main()