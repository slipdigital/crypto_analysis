"""
Example script demonstrating the stock-indicators dynamic system.

This script shows how to create and use indicators with the stock-indicators package.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import date, timedelta
from main.models import Indicator, IndicatorType
from main.indicators import (
    create_rsi_indicator,
    create_macd_indicator,
    create_sma_indicator,
    batch_create_indicators,
    get_indicator_score_summary,
)


def example_1_create_single_indicator():
    """Example 1: Create a single RSI indicator."""
    print("\n=== Example 1: Create Single RSI Indicator ===")
    
    # Get or create indicator type
    momentum, _ = IndicatorType.objects.get_or_create(
        name="Momentum",
        defaults={'description': 'Momentum oscillators', 'color': '#3498db'}
    )
    
    # Create RSI indicator
    rsi = create_rsi_indicator(
        title="Bitcoin RSI-14",
        ticker='X:BTCUSD',
        lookback_periods=14,
        oversold_threshold=30.0,
        overbought_threshold=70.0,
        indicator_type=momentum,
        auto_update=True
    )
    
    print(f"Created: {rsi.title}")
    print(f"Type: {rsi.calculation_type}")
    print(f"Indicator: {rsi.stock_indicator_name}")
    print(f"Settings: {rsi.stock_indicator_settings}")
    
    return rsi


def example_2_calculate_indicator():
    """Example 2: Calculate indicator value."""
    print("\n=== Example 2: Calculate Indicator Value ===")
    
    # Get the RSI indicator
    try:
        rsi = Indicator.objects.get(title="Bitcoin RSI-14")
    except Indicator.DoesNotExist:
        print("RSI indicator not found. Run example 1 first.")
        return
    
    # Calculate for today
    today = date.today()
    try:
        score = rsi.calculate_value(date=today)
        print(f"Date: {today}")
        print(f"Score: {score:.3f}")
        
        # Interpret the score
        if score > 0.5:
            sentiment = "Very Bullish (Oversold)"
        elif score > 0:
            sentiment = "Bullish"
        elif score > -0.5:
            sentiment = "Bearish"
        else:
            sentiment = "Very Bearish (Overbought)"
        
        print(f"Sentiment: {sentiment}")
        
    except Exception as e:
        print(f"Error calculating: {e}")


def example_3_batch_create():
    """Example 3: Create multiple indicators at once."""
    print("\n=== Example 3: Batch Create Indicators ===")
    
    # Get or create indicator type
    trend, _ = IndicatorType.objects.get_or_create(
        name="Trend",
        defaults={'description': 'Trend indicators', 'color': '#2ecc71'}
    )
    
    # Define indicator configurations
    configs = [
        {
            'title': 'BTC MACD Standard',
            'indicator_name': 'macd',
            'fast_periods': 12,
            'slow_periods': 26,
            'signal_periods': 9
        },
        {
            'title': 'BTC SMA-50',
            'indicator_name': 'sma',
            'lookback_periods': 50
        },
        {
            'title': 'BTC EMA-20',
            'indicator_name': 'ema',
            'lookback_periods': 20
        },
    ]
    
    # Create all indicators
    indicators = batch_create_indicators(
        ticker='X:BTCUSD',
        indicator_configs=configs,
        indicator_type=trend
    )
    
    print(f"Created {len(indicators)} indicators:")
    for ind in indicators:
        print(f"  - {ind.title} ({ind.stock_indicator_name})")


def example_4_indicator_summary():
    """Example 4: Get overall indicator summary."""
    print("\n=== Example 4: Indicator Score Summary ===")
    
    try:
        summary = get_indicator_score_summary('X:BTCUSD')
        
        print(f"Ticker: {summary['ticker']}")
        print(f"Date: {summary['date']}")
        print(f"Overall Score: {summary['overall_score']:.3f}")
        print(f"Overall Sentiment: {summary['overall_sentiment']}")
        print(f"\nBreakdown:")
        print(f"  Bullish: {summary['bullish_count']}")
        print(f"  Neutral: {summary['neutral_count']}")
        print(f"  Bearish: {summary['bearish_count']}")
        
        print(f"\nIndividual Indicators:")
        for ind in summary['indicators']:
            print(f"  {ind['title']}: {ind['score']:.3f} ({ind['sentiment']})")
            
    except Exception as e:
        print(f"Error getting summary: {e}")


def example_5_custom_settings():
    """Example 5: Using settings classes directly."""
    print("\n=== Example 5: Using Settings Classes ===")
    
    from main.indicators import RSISettings, create_settings
    
    # Method 1: Direct instantiation
    rsi_settings = RSISettings(
        lookback_periods=21,
        oversold_threshold=25.0,
        overbought_threshold=75.0
    )
    
    print("RSI Settings (direct):")
    print(f"  Settings: {rsi_settings}")
    print(f"  As dict: {rsi_settings.to_dict()}")
    print(f"  Indicator name: {rsi_settings.get_indicator_name()}")
    
    # Method 2: Using factory
    macd_settings = create_settings(
        'macd',
        fast_periods=10,
        slow_periods=20,
        signal_periods=8
    )
    
    print("\nMACD Settings (factory):")
    print(f"  Settings: {macd_settings}")
    print(f"  Calculator config: {macd_settings.get_calculator_config()}")


def example_6_multiple_tickers():
    """Example 6: Create indicators for multiple tickers."""
    print("\n=== Example 6: Multiple Tickers ===")
    
    tickers = ['X:BTCUSD', 'X:ETHUSD']
    
    for ticker in tickers:
        print(f"\nCreating RSI for {ticker}...")
        try:
            rsi = create_rsi_indicator(
                title=f"{ticker} RSI-14",
                ticker=ticker,
                lookback_periods=14
            )
            print(f"  Created: {rsi.title}")
            
            # Calculate current score
            score = rsi.calculate_value(date=date.today())
            print(f"  Current score: {score:.3f}")
            
        except Exception as e:
            print(f"  Error: {e}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Stock-Indicators Dynamic System Examples")
    print("=" * 60)
    
    # Run examples
    example_1_create_single_indicator()
    example_2_calculate_indicator()
    example_3_batch_create()
    example_4_indicator_summary()
    example_5_custom_settings()
    # example_6_multiple_tickers()  # Uncomment if you have multiple tickers
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
