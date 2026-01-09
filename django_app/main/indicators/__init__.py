"""
Indicator calculators package.

This package provides:
- BaseCalculator: Abstract base class for custom indicator calculators
- Custom calculator implementations (RSI, Moving Average, Volatility, etc.)
- StockIndicatorCalculator: Dynamic adapter for stock-indicators package
- Settings classes for configuring stock-indicators
- Helper functions for easy indicator creation
"""

from .base import BaseCalculator
from .stock_indicator_adapter import StockIndicatorCalculator
from .settings import (
    BaseIndicatorSettings,
    RSISettings,
    MACDSettings,
    SMASettings,
    EMASettings,
    BollingerBandsSettings,
    StochasticSettings,
    ATRSettings,
    ADXSettings,
    CCISettings,
    WilliamsRSettings,
    OBVSettings,
    ParabolicSARSettings,
    IchimokuSettings,
    create_settings,
    get_settings_class,
    SETTINGS_REGISTRY,
)
from .helpers import (
    create_stock_indicator,
    create_rsi_indicator,
    create_macd_indicator,
    create_sma_indicator,
    create_ema_indicator,
    create_bollinger_bands_indicator,
    create_stochastic_indicator,
    calculate_indicator_for_date_range,
    batch_create_indicators,
    get_indicator_score_summary,
)

__all__ = [
    # Base classes
    'BaseCalculator',
    'StockIndicatorCalculator',
    'BaseIndicatorSettings',
    
    # Settings classes
    'RSISettings',
    'MACDSettings',
    'SMASettings',
    'EMASettings',
    'BollingerBandsSettings',
    'StochasticSettings',
    'ATRSettings',
    'ADXSettings',
    'CCISettings',
    'WilliamsRSettings',
    'OBVSettings',
    'ParabolicSARSettings',
    'IchimokuSettings',
    'create_settings',
    'get_settings_class',
    'SETTINGS_REGISTRY',
    
    # Helper functions
    'create_stock_indicator',
    'create_rsi_indicator',
    'create_macd_indicator',
    'create_sma_indicator',
    'create_ema_indicator',
    'create_bollinger_bands_indicator',
    'create_stochastic_indicator',
    'calculate_indicator_for_date_range',
    'batch_create_indicators',
    'get_indicator_score_summary',
]

