"""
Helper functions for creating and managing stock-indicators based indicators.

This module provides convenience functions to make it easy to create
indicators using the stock-indicators package.
"""
from typing import Dict, Any, Optional, List
from datetime import date, timedelta
from main.models import Indicator, IndicatorType
from main.indicators import create_settings, SETTINGS_REGISTRY


def create_stock_indicator(
    title: str,
    indicator_name: str,
    ticker: str = 'X:BTCUSD',
    indicator_type: Optional[IndicatorType] = None,
    description: str = None,
    auto_update: bool = True,
    score_method: str = 'auto',
    **indicator_settings
) -> Indicator:
    """
    Create a new indicator using stock-indicators package.
    
    Args:
        title: Display name for the indicator
        indicator_name: Name of indicator from stock-indicators (e.g., 'rsi', 'macd')
        ticker: Ticker symbol to analyze (default: 'X:BTCUSD')
        indicator_type: IndicatorType instance (optional)
        description: Description of the indicator
        auto_update: Whether to enable auto-updates
        score_method: Scoring method ('auto', 'threshold', 'momentum', 'range', 'custom')
        **indicator_settings: Settings specific to the indicator
    
    Returns:
        Indicator: Created indicator instance
    
    Example:
        >>> create_stock_indicator(
        ...     title='Bitcoin RSI',
        ...     indicator_name='rsi',
        ...     ticker='X:BTCUSD',
        ...     lookback_periods=14,
        ...     oversold_threshold=30.0
        ... )
    """
    # Validate indicator name
    if indicator_name not in SETTINGS_REGISTRY:
        raise ValueError(
            f"Unknown indicator: {indicator_name}. "
            f"Available: {', '.join(SETTINGS_REGISTRY.keys())}"
        )
    
    # Create settings instance to validate parameters
    settings = create_settings(indicator_name, **indicator_settings)
    
    # Build calculator config
    calculator_config = {
        'ticker': ticker,
        'score_method': score_method,
    }
    
    # Generate description if not provided
    if description is None:
        description = f"{indicator_name.upper()} indicator for {ticker}"
    
    # Create indicator
    indicator = Indicator.objects.create(
        title=title,
        description=description,
        calculation_type='stock_indicator',
        stock_indicator_name=indicator_name,
        stock_indicator_settings=settings.to_dict(),
        calculator_config=calculator_config,
        indicator_type=indicator_type,
        auto_update=auto_update,
    )
    
    return indicator


def create_rsi_indicator(
    title: str,
    ticker: str = 'X:BTCUSD',
    lookback_periods: int = 14,
    oversold_threshold: float = 30.0,
    overbought_threshold: float = 70.0,
    **kwargs
) -> Indicator:
    """
    Create an RSI indicator.
    
    Args:
        title: Display name
        ticker: Ticker symbol
        lookback_periods: RSI period (default: 14)
        oversold_threshold: Oversold level (default: 30)
        overbought_threshold: Overbought level (default: 70)
        **kwargs: Additional arguments for create_stock_indicator
    
    Returns:
        Indicator: Created RSI indicator
    """
    return create_stock_indicator(
        title=title,
        indicator_name='rsi',
        ticker=ticker,
        score_method='threshold',
        lookback_periods=lookback_periods,
        oversold_threshold=oversold_threshold,
        overbought_threshold=overbought_threshold,
        **kwargs
    )


def create_macd_indicator(
    title: str,
    ticker: str = 'X:BTCUSD',
    fast_periods: int = 12,
    slow_periods: int = 26,
    signal_periods: int = 9,
    **kwargs
) -> Indicator:
    """
    Create a MACD indicator.
    
    Args:
        title: Display name
        ticker: Ticker symbol
        fast_periods: Fast EMA period (default: 12)
        slow_periods: Slow EMA period (default: 26)
        signal_periods: Signal line period (default: 9)
        **kwargs: Additional arguments for create_stock_indicator
    
    Returns:
        Indicator: Created MACD indicator
    """
    return create_stock_indicator(
        title=title,
        indicator_name='macd',
        ticker=ticker,
        score_method='momentum',
        fast_periods=fast_periods,
        slow_periods=slow_periods,
        signal_periods=signal_periods,
        **kwargs
    )


def create_sma_indicator(
    title: str,
    ticker: str = 'X:BTCUSD',
    lookback_periods: int = 20,
    **kwargs
) -> Indicator:
    """Create a Simple Moving Average indicator."""
    return create_stock_indicator(
        title=title,
        indicator_name='sma',
        ticker=ticker,
        lookback_periods=lookback_periods,
        **kwargs
    )


def create_ema_indicator(
    title: str,
    ticker: str = 'X:BTCUSD',
    lookback_periods: int = 20,
    **kwargs
) -> Indicator:
    """Create an Exponential Moving Average indicator."""
    return create_stock_indicator(
        title=title,
        indicator_name='ema',
        ticker=ticker,
        lookback_periods=lookback_periods,
        **kwargs
    )


def create_bollinger_bands_indicator(
    title: str,
    ticker: str = 'X:BTCUSD',
    lookback_periods: int = 20,
    standard_deviations: float = 2.0,
    **kwargs
) -> Indicator:
    """Create a Bollinger Bands indicator."""
    return create_stock_indicator(
        title=title,
        indicator_name='bollinger_bands',
        ticker=ticker,
        lookback_periods=lookback_periods,
        standard_deviations=standard_deviations,
        **kwargs
    )


def create_stochastic_indicator(
    title: str,
    ticker: str = 'X:BTCUSD',
    lookback_periods: int = 14,
    signal_periods: int = 3,
    smooth_periods: int = 3,
    **kwargs
) -> Indicator:
    """Create a Stochastic Oscillator indicator."""
    return create_stock_indicator(
        title=title,
        indicator_name='stoch',
        ticker=ticker,
        score_method='threshold',
        lookback_periods=lookback_periods,
        signal_periods=signal_periods,
        smooth_periods=smooth_periods,
        **kwargs
    )


def calculate_indicator_for_date_range(
    indicator: Indicator,
    start_date: date,
    end_date: date,
    save_to_db: bool = True
) -> List[Dict[str, Any]]:
    """
    Calculate indicator values for a date range.
    
    Args:
        indicator: Indicator instance
        start_date: Start date
        end_date: End date
        save_to_db: Whether to save results to IndicatorData table
    
    Returns:
        List of dicts with 'date' and 'value' keys
    """
    from main.models import IndicatorData
    from django.utils import timezone
    
    results = []
    current_date = start_date
    
    while current_date <= end_date:
        try:
            value = indicator.calculate_value(date=current_date)
            
            results.append({
                'date': current_date,
                'value': value
            })
            
            # Save to database if requested
            if save_to_db:
                timestamp = timezone.now().isoformat()
                IndicatorData.objects.update_or_create(
                    indicator=indicator,
                    date=current_date,
                    defaults={
                        'value': value,
                        'updated_at': timestamp
                    }
                )
        except Exception as e:
            # Skip dates with errors (e.g., no data available)
            pass
        
        current_date += timedelta(days=1)
    
    return results


def batch_create_indicators(
    ticker: str,
    indicator_configs: List[Dict[str, Any]],
    indicator_type: Optional[IndicatorType] = None
) -> List[Indicator]:
    """
    Create multiple indicators at once.
    
    Args:
        ticker: Ticker symbol for all indicators
        indicator_configs: List of config dicts with 'title', 'indicator_name', and settings
        indicator_type: IndicatorType to assign to all indicators
    
    Returns:
        List of created Indicator instances
    
    Example:
        >>> configs = [
        ...     {'title': 'BTC RSI-14', 'indicator_name': 'rsi', 'lookback_periods': 14},
        ...     {'title': 'BTC MACD', 'indicator_name': 'macd'},
        ...     {'title': 'BTC SMA-50', 'indicator_name': 'sma', 'lookback_periods': 50},
        ... ]
        >>> indicators = batch_create_indicators('X:BTCUSD', configs)
    """
    indicators = []
    
    for config in indicator_configs:
        title = config.pop('title')
        indicator_name = config.pop('indicator_name')
        
        indicator = create_stock_indicator(
            title=title,
            indicator_name=indicator_name,
            ticker=ticker,
            indicator_type=indicator_type,
            **config
        )
        indicators.append(indicator)
    
    return indicators


def get_indicator_score_summary(
    ticker: str,
    target_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Get a summary of all indicator scores for a ticker.
    
    Args:
        ticker: Ticker symbol
        target_date: Date to calculate for (default: today)
    
    Returns:
        Dict with indicator scores and overall sentiment
    
    Example:
        >>> summary = get_indicator_score_summary('X:BTCUSD')
        >>> print(summary['overall_score'])
        >>> print(summary['indicators'])
    """
    if target_date is None:
        target_date = date.today()
    
    # Get all indicators for this ticker
    indicators = Indicator.objects.filter(
        calculation_type='stock_indicator',
        calculator_config__ticker=ticker
    )
    
    scores = []
    indicator_details = []
    
    for indicator in indicators:
        try:
            score = indicator.calculate_value(date=target_date)
            scores.append(score)
            indicator_details.append({
                'title': indicator.title,
                'indicator_name': indicator.stock_indicator_name,
                'score': score,
                'sentiment': _score_to_sentiment(score)
            })
        except Exception as e:
            # Skip indicators that fail
            pass
    
    # Calculate overall score
    overall_score = sum(scores) / len(scores) if scores else 0.0
    
    return {
        'ticker': ticker,
        'date': target_date,
        'overall_score': overall_score,
        'overall_sentiment': _score_to_sentiment(overall_score),
        'indicator_count': len(scores),
        'indicators': indicator_details,
        'bullish_count': sum(1 for s in scores if s > 0.3),
        'bearish_count': sum(1 for s in scores if s < -0.3),
        'neutral_count': sum(1 for s in scores if -0.3 <= s <= 0.3),
    }


def _score_to_sentiment(score: float) -> str:
    """Convert numeric score to sentiment label."""
    if score >= 0.6:
        return 'Very Bullish'
    elif score >= 0.2:
        return 'Bullish'
    elif score >= -0.2:
        return 'Neutral'
    elif score >= -0.6:
        return 'Bearish'
    else:
        return 'Very Bearish'
