"""
Example indicator calculator implementations.

These serve as templates for creating custom indicator calculators.
"""
from datetime import date, timedelta
from typing import Dict, Any
from .base import BaseCalculator
from main.models import Ticker, TickerData


class MovingAverageTrendCalculator(BaseCalculator):
    """
    Calculate trend based on moving average comparison.
    
    Compares short-term MA vs long-term MA to determine bullish/bearish trend.
    Returns value between -1.0 (bearish) and 1.0 (bullish).
    
    Config options:
        - ticker: Ticker symbol to analyze (default: 'X:BTCUSD')
        - short_period: Short MA period in days (default: 7)
        - long_period: Long MA period in days (default: 30)
    """
    
    def calculate(self, date: date, **kwargs) -> float:
        """Calculate moving average trend indicator."""
        # Get config
        ticker_symbol = self.config.get('ticker', 'X:BTCUSD')
        short_period = self.config.get('short_period', 7)
        long_period = self.config.get('long_period', 30)
        
        try:
            # Get ticker
            ticker = Ticker.objects.get(ticker=ticker_symbol)
            
            # Get price data for the periods
            end_date = date
            start_date = date - timedelta(days=long_period + 10)  # Extra days for weekends
            
            price_data = TickerData.objects.filter(
                ticker=ticker,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('-date').values_list('close', flat=True)
            
            if len(price_data) < long_period:
                raise ValueError(f"Insufficient data for {ticker_symbol}: need {long_period} days, have {len(price_data)}")
            
            # Calculate moving averages
            short_ma = sum(list(price_data)[:short_period]) / short_period
            long_ma = sum(list(price_data)[:long_period]) / long_period
            
            # Calculate difference as percentage
            diff_percent = ((short_ma - long_ma) / long_ma) * 100
            
            # Normalize to -1.0 to 1.0 range
            # Assume ±10% difference is max (adjust as needed)
            normalized = diff_percent / 10.0
            
            return self.validate_value(normalized)
            
        except Ticker.DoesNotExist:
            raise ValueError(f"Ticker {ticker_symbol} not found")
        except Exception as e:
            raise ValueError(f"Error calculating MA trend: {e}")


class VolatilityCalculator(BaseCalculator):
    """
    Calculate volatility indicator based on price variance.
    
    Returns value between -1.0 (low volatility) and 1.0 (high volatility).
    
    Config options:
        - ticker: Ticker symbol to analyze (default: 'X:BTCUSD')
        - period: Period in days (default: 30)
        - threshold: Volatility threshold for normalization (default: 5.0)
    """
    
    def calculate(self, date: date, **kwargs) -> float:
        """Calculate volatility indicator."""
        ticker_symbol = self.config.get('ticker', 'X:BTCUSD')
        period = self.config.get('period', 30)
        threshold = self.config.get('threshold', 5.0)
        
        try:
            ticker = Ticker.objects.get(ticker=ticker_symbol)
            
            # Get price data
            start_date = date - timedelta(days=period + 10)
            price_data = TickerData.objects.filter(
                ticker=ticker,
                date__gte=start_date,
                date__lte=date
            ).order_by('-date').values_list('close', flat=True)
            
            if len(price_data) < period:
                raise ValueError(f"Insufficient data: need {period} days, have {len(price_data)}")
            
            prices = list(price_data)[:period]
            
            # Calculate standard deviation as percentage of mean
            mean_price = sum(prices) / len(prices)
            variance = sum((p - mean_price) ** 2 for p in prices) / len(prices)
            std_dev = variance ** 0.5
            volatility_percent = (std_dev / mean_price) * 100
            
            # Normalize to -1.0 to 1.0 range (map to 0.0 to 1.0, then shift)
            normalized = (volatility_percent / threshold)
            # Map to -1.0 (low) to 1.0 (high)
            normalized = (normalized * 2) - 1.0
            
            return self.validate_value(normalized)
            
        except Ticker.DoesNotExist:
            raise ValueError(f"Ticker {ticker_symbol} not found")
        except Exception as e:
            raise ValueError(f"Error calculating volatility: {e}")


class SimpleThresholdCalculator(BaseCalculator):
    """
    Simple example calculator that returns a fixed value based on a threshold.
    
    Useful for testing and demonstration.
    
    Config options:
        - threshold: Value to return (default: 0.5)
    """
    
    def calculate(self, date: date, **kwargs) -> float:
        """Return configured threshold value."""
        value = self.config.get('threshold', 0.5)
        return self.validate_value(value)
