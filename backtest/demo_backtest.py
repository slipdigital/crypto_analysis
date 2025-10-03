#!/usr/bin/env python3
"""
Demo script showing advanced backtesting features including visualizations
"""

from backtest.crypto_backtest import CryptoBacktester, MovingAverageCrossover, RSIStrategy, BuyAndHold
import pandas as pd

def demo_single_crypto_detailed(crypto='BTC'):
    """
    Detailed analysis of a single cryptocurrency
    """
    print(f"=== Detailed Analysis: {crypto} ===")
    
    backtester = CryptoBacktester()
    
    # Check if crypto is available
    available_cryptos = backtester.get_available_cryptos()
    if crypto not in available_cryptos:
        print(f"Cryptocurrency {crypto} not found. Using first available: {available_cryptos[0]}")
        crypto = available_cryptos[0]
    
    print(f"\nTesting {crypto} with different strategy parameters...")
    
    # Test Moving Average with different parameters
    print("\n--- Moving Average Strategy Optimization ---")
    ma_results = []
    
    # Test different MA combinations
    ma_combinations = [
        (10, 20), (20, 50), (50, 100), (5, 15), (15, 30)
    ]
    
    for short, long in ma_combinations:
        result = backtester.run_backtest(crypto, MovingAverageCrossover, 
                                       short_window=short, long_window=long)
        if result is not None:
            ma_results.append({
                'Short_MA': short,
                'Long_MA': long,
                'Return': result['Return [%]'],
                'Sharpe': result['Sharpe Ratio'],
                'Max_DD': result['Max. Drawdown [%]'],
                'Trades': result['# Trades']
            })
    
    if ma_results:
        ma_df = pd.DataFrame(ma_results)
        ma_df = ma_df.sort_values('Return', ascending=False)
        print("Moving Average Parameter Optimization:")
        print(ma_df.to_string(index=False))
        
        best_ma = ma_df.iloc[0]
        print(f"\nBest MA combination: {int(best_ma['Short_MA'])}/{int(best_ma['Long_MA'])} "
              f"with {best_ma['Return']:.2f}% return")
    
    # Test RSI with different parameters
    print("\n--- RSI Strategy Optimization ---")
    rsi_results = []
    
    # Test different RSI parameters
    rsi_combinations = [
        (14, 30, 70), (14, 25, 75), (21, 30, 70), (7, 20, 80), (14, 35, 65)
    ]
    
    for window, lower, upper in rsi_combinations:
        result = backtester.run_backtest(crypto, RSIStrategy,
                                       rsi_window=window, rsi_lower=lower, rsi_upper=upper)
        if result is not None:
            rsi_results.append({
                'RSI_Window': window,
                'Lower': lower,
                'Upper': upper,
                'Return': result['Return [%]'],
                'Sharpe': result['Sharpe Ratio'],
                'Max_DD': result['Max. Drawdown [%]'],
                'Trades': result['# Trades']
            })
    
    if rsi_results:
        rsi_df = pd.DataFrame(rsi_results)
        rsi_df = rsi_df.sort_values('Return', ascending=False)
        print("RSI Parameter Optimization:")
        print(rsi_df.to_string(index=False))
        
        best_rsi = rsi_df.iloc[0]
        print(f"\nBest RSI combination: {int(best_rsi['RSI_Window'])}-period RSI "
              f"with {int(best_rsi['Lower'])}/{int(best_rsi['Upper'])} levels, "
              f"{best_rsi['Return']:.2f}% return")

def demo_portfolio_analysis():
    """
    Analyze multiple cryptocurrencies as a portfolio
    """
    print("\n=== Portfolio Analysis ===")
    
    backtester = CryptoBacktester()
    available_cryptos = backtester.get_available_cryptos()
    
    # Select top cryptocurrencies for analysis
    major_cryptos = ['BTC', 'ETH', 'SOL', 'ADA', 'LINK', 'AVAX', 'DOT', 'UNI']
    test_cryptos = [crypto for crypto in major_cryptos if crypto in available_cryptos]
    
    if len(test_cryptos) < 3:
        test_cryptos = available_cryptos[:5]  # Use first 5 if major cryptos not available
    
    print(f"Analyzing portfolio of: {test_cryptos}")
    
    # Test each crypto with the best performing strategy (usually Buy & Hold for crypto)
    portfolio_results = []
    
    for crypto in test_cryptos:
        print(f"\nAnalyzing {crypto}...")
        
        # Test all strategies
        strategies = [MovingAverageCrossover, RSIStrategy, BuyAndHold]
        crypto_results = {}
        
        for strategy in strategies:
            result = backtester.run_backtest(crypto, strategy)
            if result is not None:
                crypto_results[strategy.__name__] = {
                    'Return': result['Return [%]'],
                    'Sharpe': result['Sharpe Ratio'],
                    'Max_DD': result['Max. Drawdown [%]']
                }
        
        # Find best strategy for this crypto
        if crypto_results:
            best_strategy = max(crypto_results.keys(), 
                              key=lambda x: crypto_results[x]['Return'])
            best_result = crypto_results[best_strategy]
            
            portfolio_results.append({
                'Crypto': crypto,
                'Best_Strategy': best_strategy,
                'Return': best_result['Return'],
                'Sharpe': best_result['Sharpe'],
                'Max_DD': best_result['Max_DD']
            })
    
    if portfolio_results:
        portfolio_df = pd.DataFrame(portfolio_results)
        portfolio_df = portfolio_df.sort_values('Return', ascending=False)
        
        print("\n--- Portfolio Performance Summary ---")
        print(portfolio_df.to_string(index=False))
        
        # Calculate portfolio statistics
        avg_return = portfolio_df['Return'].mean()
        avg_sharpe = portfolio_df['Sharpe'].mean()
        worst_dd = portfolio_df['Max_DD'].min()
        
        print(f"\n--- Portfolio Statistics ---")
        print(f"Average Return: {avg_return:.2f}%")
        print(f"Average Sharpe Ratio: {avg_sharpe:.2f}")
        print(f"Worst Max Drawdown: {worst_dd:.2f}%")
        print(f"Best Performer: {portfolio_df.iloc[0]['Crypto']} ({portfolio_df.iloc[0]['Return']:.2f}%)")
        print(f"Worst Performer: {portfolio_df.iloc[-1]['Crypto']} ({portfolio_df.iloc[-1]['Return']:.2f}%)")

def demo_risk_analysis():
    """
    Demonstrate risk analysis across different cryptocurrencies
    """
    print("\n=== Risk Analysis ===")
    
    backtester = CryptoBacktester()
    available_cryptos = backtester.get_available_cryptos()
    
    # Test a few cryptos with Buy & Hold to analyze pure asset risk
    test_cryptos = available_cryptos[:8] if len(available_cryptos) >= 8 else available_cryptos
    
    risk_results = []
    
    for crypto in test_cryptos:
        result = backtester.run_backtest(crypto, BuyAndHold)
        if result is not None:
            risk_results.append({
                'Crypto': crypto,
                'Return': result['Return [%]'],
                'Volatility': result.get('Volatility [%]', 0),
                'Sharpe': result['Sharpe Ratio'],
                'Max_DD': result['Max. Drawdown [%]'],
                'Calmar': result.get('Calmar Ratio', 0)
            })
    
    if risk_results:
        risk_df = pd.DataFrame(risk_results)
        
        print("Risk-Return Analysis (Buy & Hold):")
        print(risk_df.to_string(index=False))
        
        # Risk categories
        print(f"\n--- Risk Categories ---")
        high_return = risk_df[risk_df['Return'] > risk_df['Return'].quantile(0.75)]
        low_risk = risk_df[risk_df['Max_DD'] > risk_df['Max_DD'].quantile(0.25)]  # Less negative DD = lower risk
        high_sharpe = risk_df[risk_df['Sharpe'] > risk_df['Sharpe'].quantile(0.75)]
        
        print(f"High Return Assets: {list(high_return['Crypto'])}")
        print(f"Lower Risk Assets: {list(low_risk['Crypto'])}")
        print(f"High Sharpe Ratio Assets: {list(high_sharpe['Crypto'])}")

def main():
    """
    Run comprehensive backtesting demo
    """
    print("Cryptocurrency Backtesting Framework - Advanced Demo")
    print("=" * 60)
    
    # Initialize and check available data
    backtester = CryptoBacktester()
    available_cryptos = backtester.get_available_cryptos()
    
    if not available_cryptos:
        print("No cryptocurrency data found!")
        return
    
    print(f"Found {len(available_cryptos)} cryptocurrencies")
    
    # Demo 1: Detailed single crypto analysis
    demo_crypto = 'BTC' if 'BTC' in available_cryptos else available_cryptos[0]
    demo_single_crypto_detailed(demo_crypto)
    
    # Demo 2: Portfolio analysis
    demo_portfolio_analysis()
    
    # Demo 3: Risk analysis
    demo_risk_analysis()
    
    print(f"\n{'='*60}")
    print("Demo completed! Check the results above for insights.")
    print("\nTo generate interactive plots, uncomment the plot lines in crypto_backtest.py")
    print("and run: backtester.show_plot('BTC', MovingAverageCrossover)")

if __name__ == "__main__":
    main()