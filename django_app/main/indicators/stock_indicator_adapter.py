"""
Stock-indicators package adapter calculator.

This module provides a dynamic calculator that can use any indicator from
the stock-indicators package with custom settings classes.
"""
from datetime import date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseCalculator
from .settings import BaseIndicatorSettings, get_settings_class, SETTINGS_REGISTRY
from main.models import Ticker, TickerData


class StockIndicatorCalculator(BaseCalculator):
    """
    Dynamic calculator that uses the stock-indicators package.
    
    This calculator can compute any indicator from the stock-indicators package
    by dynamically loading the appropriate indicator function and applying
    custom settings.
    
    Config options:
        - ticker: Ticker symbol to analyze (default: 'X:BTCUSD')
        - indicator_name: Name of the indicator from stock-indicators (e.g., 'rsi', 'macd')
        - indicator_settings: Dict of settings specific to the indicator
        - settings_class: Optional path to custom settings class
        - score_method: How to convert indicator to score ('range', 'threshold', 'momentum', 'custom')
        - custom_score_function: Custom function path for scoring
        - lookback_days: Additional days to fetch for calculation buffer (default: 100)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the calculator with configuration."""
        super().__init__(config)
        
        # Import stock-indicators
        try:
            from stock_indicators import indicators
            self.stock_indicators = indicators
        except ImportError:
            raise ImportError(
                "stock-indicators package not installed. "
                "Install with: pip install stock-indicators"
            )
    
    def calculate(self, date: date, **kwargs) -> float:
        """
        Calculate indicator value using stock-indicators package.
        
        Args:
            date: The date to calculate for
            **kwargs: Additional arguments
            
        Returns:
            float: Indicator score between -1.0 and 1.0
        """
        # Get config
        ticker_symbol = self.config.get('ticker', 'X:BTCUSD')
        indicator_name = self.config.get('indicator_name')
        
        if not indicator_name:
            raise ValueError("indicator_name must be specified in config")
        
        # Get or create settings
        settings = self._get_settings()
        
        # Get price data
        quotes = self._get_quotes(ticker_symbol, date)
        
        # Calculate indicator
        indicator_results = self._calculate_indicator(indicator_name, quotes, settings)
        
        # Convert to score
        score = self._convert_to_score(indicator_results, date, settings)
        
        return self.validate_value(score)
    
    def _get_settings(self) -> BaseIndicatorSettings:
        """
        Get or create indicator settings from config.
        
        Returns:
            BaseIndicatorSettings: Settings instance
        """
        indicator_name = self.config.get('indicator_name')
        indicator_settings = self.config.get('indicator_settings', {})
        settings_class_path = self.config.get('settings_class')
        
        # If custom settings class specified, import it
        if settings_class_path:
            from importlib import import_module
            module_path, class_name = settings_class_path.rsplit('.', 1)
            module = import_module(module_path)
            settings_class = getattr(module, class_name)
            return settings_class.from_dict(indicator_settings)
        
        # Otherwise use built-in settings
        if indicator_name not in SETTINGS_REGISTRY:
            raise ValueError(f"Unknown indicator: {indicator_name}")
        
        settings_class = get_settings_class(indicator_name)
        return settings_class.from_dict(indicator_settings)
    
    def _get_quotes(self, ticker_symbol: str, end_date: date) -> List[Dict[str, Any]]:
        """
        Get price quotes from database in format required by stock-indicators.
        
        Args:
            ticker_symbol: Ticker symbol
            end_date: End date for data
            
        Returns:
            List of quote dictionaries with keys: date, open, high, low, close, volume
        """
        try:
            ticker = Ticker.objects.get(ticker=ticker_symbol)
        except Ticker.DoesNotExist:
            raise ValueError(f"Ticker {ticker_symbol} not found")
        
        # Get sufficient data for calculation
        lookback_days = self.config.get('lookback_days', 100)
        start_date = end_date - timedelta(days=lookback_days)
        
        # Fetch data
        ticker_data = TickerData.objects.filter(
            ticker=ticker,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date').values('date', 'open', 'high', 'low', 'close', 'volume')
        
        if not ticker_data:
            raise ValueError(f"No data available for {ticker_symbol}")
        
        # Convert to stock-indicators format
        quotes = []
        for data in ticker_data:
            quotes.append({
                'date': data['date'],
                'open': float(data['open']) if data['open'] is not None else None,
                'high': float(data['high']) if data['high'] is not None else None,
                'low': float(data['low']) if data['low'] is not None else None,
                'close': float(data['close']) if data['close'] is not None else None,
                'volume': float(data['volume']) if data['volume'] is not None else None,
            })
        
        return quotes
    
    def _calculate_indicator(
        self, 
        indicator_name: str, 
        quotes: List[Dict[str, Any]], 
        settings: BaseIndicatorSettings
    ) -> List[Any]:
        """
        Calculate indicator using stock-indicators package.
        
        Args:
            indicator_name: Name of indicator
            quotes: Price data
            settings: Indicator settings
            
        Returns:
            List of indicator results
        """
        # Get indicator function from stock-indicators
        # Map our names to stock-indicators function names
        indicator_map = {
            'rsi': 'get_rsi',
            'macd': 'get_macd',
            'sma': 'get_sma',
            'ema': 'get_ema',
            'bollinger_bands': 'get_bollinger_bands',
            'stoch': 'get_stoch',
            'atr': 'get_atr',
            'adx': 'get_adx',
            'cci': 'get_cci',
            'williams_r': 'get_williams_r',
            'obv': 'get_obv',
            'psar': 'get_psar',
            'ichimoku': 'get_ichimoku',
        }
        
        func_name = indicator_map.get(indicator_name)
        if not func_name:
            raise ValueError(f"Indicator {indicator_name} not supported")
        
        if not hasattr(self.stock_indicators, func_name):
            raise ValueError(f"Function {func_name} not found in stock-indicators")
        
        indicator_func = getattr(self.stock_indicators, func_name)
        
        # Get settings as dict (excluding None values)
        params = settings.to_dict()
        
        # Call indicator function
        try:
            results = indicator_func(quotes, **params)
            return list(results)
        except Exception as e:
            raise ValueError(f"Error calculating {indicator_name}: {e}")
    
    def _convert_to_score(
        self, 
        results: List[Any], 
        target_date: date,
        settings: BaseIndicatorSettings
    ) -> float:
        """
        Convert indicator results to a score between -1.0 and 1.0.
        
        Args:
            results: Indicator calculation results
            target_date: Date to get score for
            settings: Indicator settings
            
        Returns:
            float: Score between -1.0 and 1.0
        """
        # Find result for target date
        result = None
        for r in reversed(results):
            if hasattr(r, 'date') and r.date == target_date:
                result = r
                break
        
        if result is None:
            raise ValueError(f"No indicator result for date {target_date}")
        
        # Get score method
        score_method = self.config.get('score_method', 'auto')
        
        if score_method == 'auto':
            # Automatically determine best scoring method based on indicator
            score_method = self._get_auto_score_method(settings.get_indicator_name())
        
        if score_method == 'threshold':
            return self._score_threshold(result, settings)
        elif score_method == 'range':
            return self._score_range(result, settings)
        elif score_method == 'momentum':
            return self._score_momentum(results, target_date, settings)
        elif score_method == 'custom':
            return self._score_custom(result, settings)
        else:
            raise ValueError(f"Unknown score_method: {score_method}")
    
    def _get_auto_score_method(self, indicator_name: str) -> str:
        """Automatically determine best scoring method for indicator."""
        threshold_indicators = ['rsi', 'stoch', 'cci', 'williams_r']
        momentum_indicators = ['macd', 'obv']
        
        if indicator_name in threshold_indicators:
            return 'threshold'
        elif indicator_name in momentum_indicators:
            return 'momentum'
        else:
            return 'range'
    
    def _score_threshold(self, result: Any, settings: BaseIndicatorSettings) -> float:
        """
        Score based on overbought/oversold thresholds.
        
        Used for oscillators like RSI, Stochastic, CCI, Williams %R.
        """
        # Get the primary value from result
        if hasattr(result, 'rsi'):
            value = result.rsi
        elif hasattr(result, 'oscillator'):
            value = result.oscillator
        elif hasattr(result, 'cci'):
            value = result.cci
        elif hasattr(result, 'williams_r'):
            value = result.williams_r
        else:
            raise ValueError("Cannot determine indicator value from result")
        
        if value is None:
            raise ValueError("Indicator value is None")
        
        # Get thresholds from settings
        oversold = getattr(settings, 'oversold_threshold', 30)
        overbought = getattr(settings, 'overbought_threshold', 70)
        neutral = (oversold + overbought) / 2
        
        # Convert to score
        if value <= oversold:
            return 1.0  # Oversold = bullish
        elif value >= overbought:
            return -1.0  # Overbought = bearish
        elif value < neutral:
            # Between oversold and neutral
            return (neutral - value) / (neutral - oversold)
        else:
            # Between neutral and overbought
            return -(value - neutral) / (overbought - neutral)
    
    def _score_range(self, result: Any, settings: BaseIndicatorSettings) -> float:
        """
        Score based on value range normalization.
        
        Used for indicators with predictable ranges.
        """
        # This is a simple implementation - can be customized per indicator
        # For now, return 0.0 as placeholder
        return 0.0
    
    def _score_momentum(
        self, 
        results: List[Any], 
        target_date: date,
        settings: BaseIndicatorSettings
    ) -> float:
        """
        Score based on momentum/trend direction.
        
        Used for indicators like MACD, OBV that show trend.
        """
        # Find current and previous results
        current_idx = None
        for i, r in enumerate(results):
            if hasattr(r, 'date') and r.date == target_date:
                current_idx = i
                break
        
        if current_idx is None or current_idx == 0:
            return 0.0
        
        current = results[current_idx]
        previous = results[current_idx - 1]
        
        # For MACD
        if hasattr(current, 'macd') and hasattr(current, 'signal'):
            if current.macd is None or current.signal is None:
                return 0.0
            
            # Score based on MACD vs Signal line
            diff = current.macd - current.signal
            # Normalize to reasonable range (assume ±5 is significant)
            normalized = diff / 5.0
            return max(-1.0, min(1.0, normalized))
        
        # For OBV - compare trend
        if hasattr(current, 'obv'):
            if current.obv is None or previous.obv is None:
                return 0.0
            
            change = current.obv - previous.obv
            # Normalize based on absolute values
            if abs(previous.obv) > 0:
                pct_change = change / abs(previous.obv)
                # Assume ±10% is significant
                normalized = pct_change * 10
                return max(-1.0, min(1.0, normalized))
        
        return 0.0
    
    def _score_custom(self, result: Any, settings: BaseIndicatorSettings) -> float:
        """Score using custom function specified in config."""
        custom_func_path = self.config.get('custom_score_function')
        if not custom_func_path:
            raise ValueError("custom_score_function not specified in config")
        
        from importlib import import_module
        module_path, func_name = custom_func_path.rsplit('.', 1)
        module = import_module(module_path)
        score_func = getattr(module, func_name)
        
        return score_func(result, settings, self.config)
    
    def get_description(self) -> str:
        """Get description of this calculator."""
        indicator_name = self.config.get('indicator_name', 'unknown')
        return f"Stock-Indicators calculator for {indicator_name}"
