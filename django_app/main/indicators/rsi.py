"""
RSI (Relative Strength Index) calculator for indicators.

RSI is a momentum oscillator that measures the speed and magnitude of price changes.
Traditional interpretation:
  - RSI < 30: Oversold (bullish signal)
  - RSI > 70: Overbought (bearish signal)
  - RSI = 50: Neutral
"""
from datetime import date, timedelta
from typing import List
from .base import BaseCalculator
from main.models import Ticker, TickerData


class RSICalculator(BaseCalculator):
    """
    Calculate RSI and convert to indicator score.
    
    Maps RSI values to -1.0 to 1.0 range:
      - RSI 30 or below (oversold) = 1.0 (very bullish)
      - RSI 50 (neutral) = 0.0
      - RSI 70 or above (overbought) = -1.0 (very bearish)
    
    Config options:
        - ticker: Ticker symbol to analyze (default: 'X:BTCUSD')
        - period: RSI period in days (default: 14)
        - oversold_threshold: RSI oversold level (default: 30)
        - overbought_threshold: RSI overbought level (default: 70)
    """
    
    def calculate(self, date: date, **kwargs) -> float:
        """Calculate RSI indicator score."""
        # Get config
        ticker_symbol = self.config.get('ticker', 'X:BTCUSD')
        period = self.config.get('period', 14)
        oversold = self.config.get('oversold_threshold', 30)
        overbought = self.config.get('overbought_threshold', 70)
        
        try:
            # Get ticker
            ticker = Ticker.objects.get(ticker=ticker_symbol)
            
            # Get price data - need period + 1 days for RSI calculation
            start_date = date - timedelta(days=period + 20)  # Extra for weekends
            
            price_data = TickerData.objects.filter(
                ticker=ticker,
                date__gte=start_date,
                date__lte=date
            ).order_by('date').values_list('close', flat=True)
            
            if len(price_data) < period + 1:
                raise ValueError(
                    f"Insufficient data for {ticker_symbol}: need {period + 1} days, have {len(price_data)}"
                )
            
            # Calculate RSI
            prices = list(price_data)
            rsi = self._calculate_rsi(prices, period)
            
            # Convert RSI to indicator score (-1.0 to 1.0)
            score = self._rsi_to_score(rsi, oversold, overbought)
            
            return self.validate_value(score)
            
        except Ticker.DoesNotExist:
            raise ValueError(f"Ticker {ticker_symbol} not found")
        except Exception as e:
            raise ValueError(f"Error calculating RSI: {e}")
    
    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """
        Calculate RSI using the standard formula.
        
        Args:
            prices: List of closing prices (oldest to newest)
            period: RSI period (typically 14)
            
        Returns:
            float: RSI value (0-100)
        """
        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        # Calculate initial average gain/loss
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Calculate smoothed averages using Wilder's smoothing
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        # Calculate RSI
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        return rsi
    
    def _rsi_to_score(self, rsi: float, oversold: float, overbought: float) -> float:
        """
        Convert RSI value to indicator score between -1.0 and 1.0.
        
        Mapping:
          - RSI <= oversold (30) → +1.0 (very bullish)
          - RSI = 50 (neutral) → 0.0
          - RSI >= overbought (70) → -1.0 (very bearish)
        
        Args:
            rsi: RSI value (0-100)
            oversold: Oversold threshold
            overbought: Overbought threshold
            
        Returns:
            float: Score between -1.0 and 1.0
        """
        neutral = 50.0
        
        if rsi <= oversold:
            # Oversold = bullish signal
            return 1.0
        elif rsi >= overbought:
            # Overbought = bearish signal
            return -1.0
        elif rsi < neutral:
            # Between oversold and neutral: map to 0.0 to 1.0
            # Linear interpolation
            return (neutral - rsi) / (neutral - oversold)
        else:
            # Between neutral and overbought: map to 0.0 to -1.0
            # Linear interpolation
            return -(rsi - neutral) / (overbought - neutral)
    
    def get_description(self) -> str:
        """Get description of this calculator."""
        return "RSI (Relative Strength Index) calculator with oversold/overbought scoring"
