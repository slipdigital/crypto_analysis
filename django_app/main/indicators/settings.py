"""
Indicator settings classes for stock-indicators package integration.

These classes define the configuration for different technical indicators
from the stock-indicators package. Each settings class contains the parameters
needed to calculate a specific indicator.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class BaseIndicatorSettings(ABC):
    """
    Base class for indicator settings.
    
    All indicator settings should inherit from this class and define
    their specific parameters as dataclass fields.
    """
    
    @abstractmethod
    def get_indicator_name(self) -> str:
        """
        Get the name of the indicator in stock-indicators package.
        
        Returns:
            str: The indicator name (e.g., 'rsi', 'macd', 'sma')
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of settings
        """
        result = asdict(self)
        # Remove None values to use defaults
        return {k: v for k, v in result.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create settings instance from dictionary.
        
        Args:
            data: Dictionary containing settings parameters
            
        Returns:
            BaseIndicatorSettings: Settings instance
        """
        # Filter to only fields that exist in the dataclass
        import inspect
        sig = inspect.signature(cls)
        filtered_data = {k: v for k, v in data.items() if k in sig.parameters}
        return cls(**filtered_data)
    
    def get_calculator_config(self) -> Dict[str, Any]:
        """
        Get configuration dictionary for the calculator.
        
        Returns:
            Dict[str, Any]: Configuration for StockIndicatorCalculator
        """
        return {
            'indicator_name': self.get_indicator_name(),
            'indicator_settings': self.to_dict(),
            'settings_class': f"{self.__class__.__module__}.{self.__class__.__name__}"
        }


@dataclass
class RSISettings(BaseIndicatorSettings):
    """
    Settings for RSI (Relative Strength Index) indicator.
    
    RSI measures momentum and identifies overbought/oversold conditions.
    """
    lookback_periods: int = 14  # Standard RSI period
    
    # Interpretation thresholds (for score conversion)
    oversold_threshold: float = 30.0
    overbought_threshold: float = 70.0
    
    def get_indicator_name(self) -> str:
        return "rsi"


@dataclass
class MACDSettings(BaseIndicatorSettings):
    """
    Settings for MACD (Moving Average Convergence Divergence) indicator.
    
    MACD shows the relationship between two moving averages.
    """
    fast_periods: int = 12
    slow_periods: int = 26
    signal_periods: int = 9
    
    def get_indicator_name(self) -> str:
        return "macd"


@dataclass
class SMASettings(BaseIndicatorSettings):
    """
    Settings for SMA (Simple Moving Average) indicator.
    
    SMA calculates the average price over a specified period.
    """
    lookback_periods: int = 20
    
    def get_indicator_name(self) -> str:
        return "sma"


@dataclass
class EMASettings(BaseIndicatorSettings):
    """
    Settings for EMA (Exponential Moving Average) indicator.
    
    EMA gives more weight to recent prices.
    """
    lookback_periods: int = 20
    
    def get_indicator_name(self) -> str:
        return "ema"


@dataclass
class BollingerBandsSettings(BaseIndicatorSettings):
    """
    Settings for Bollinger Bands indicator.
    
    Bollinger Bands show volatility and potential price levels.
    """
    lookback_periods: int = 20
    standard_deviations: float = 2.0
    
    def get_indicator_name(self) -> str:
        return "bollinger_bands"


@dataclass
class StochasticSettings(BaseIndicatorSettings):
    """
    Settings for Stochastic Oscillator indicator.
    
    Stochastic measures momentum by comparing closing price to price range.
    """
    lookback_periods: int = 14
    signal_periods: int = 3
    smooth_periods: int = 3
    
    # Interpretation thresholds
    oversold_threshold: float = 20.0
    overbought_threshold: float = 80.0
    
    def get_indicator_name(self) -> str:
        return "stoch"


@dataclass
class ATRSettings(BaseIndicatorSettings):
    """
    Settings for ATR (Average True Range) indicator.
    
    ATR measures market volatility.
    """
    lookback_periods: int = 14
    
    def get_indicator_name(self) -> str:
        return "atr"


@dataclass
class ADXSettings(BaseIndicatorSettings):
    """
    Settings for ADX (Average Directional Index) indicator.
    
    ADX measures trend strength (not direction).
    """
    lookback_periods: int = 14
    
    def get_indicator_name(self) -> str:
        return "adx"


@dataclass
class CCISettings(BaseIndicatorSettings):
    """
    Settings for CCI (Commodity Channel Index) indicator.
    
    CCI identifies cyclical trends and overbought/oversold conditions.
    """
    lookback_periods: int = 20
    
    # Interpretation thresholds
    oversold_threshold: float = -100.0
    overbought_threshold: float = 100.0
    
    def get_indicator_name(self) -> str:
        return "cci"


@dataclass
class WilliamsRSettings(BaseIndicatorSettings):
    """
    Settings for Williams %R indicator.
    
    Williams %R measures overbought/oversold levels.
    """
    lookback_periods: int = 14
    
    # Interpretation thresholds
    oversold_threshold: float = -80.0
    overbought_threshold: float = -20.0
    
    def get_indicator_name(self) -> str:
        return "williams_r"


@dataclass
class OBVSettings(BaseIndicatorSettings):
    """
    Settings for OBV (On-Balance Volume) indicator.
    
    OBV relates volume to price changes.
    """
    sma_periods: Optional[int] = None  # Optional SMA of OBV
    
    def get_indicator_name(self) -> str:
        return "obv"


@dataclass
class ParabolicSARSettings(BaseIndicatorSettings):
    """
    Settings for Parabolic SAR (Stop and Reverse) indicator.
    
    Parabolic SAR identifies potential reversals in price direction.
    """
    acceleration_step: float = 0.02
    max_acceleration: float = 0.2
    
    def get_indicator_name(self) -> str:
        return "psar"


@dataclass
class IchimokuSettings(BaseIndicatorSettings):
    """
    Settings for Ichimoku Cloud indicator.
    
    Ichimoku provides support/resistance levels and momentum.
    """
    tenkan_periods: int = 9
    kijun_periods: int = 26
    senkou_span_b_periods: int = 52
    
    def get_indicator_name(self) -> str:
        return "ichimoku"


# Registry of available settings classes
SETTINGS_REGISTRY = {
    'rsi': RSISettings,
    'macd': MACDSettings,
    'sma': SMASettings,
    'ema': EMASettings,
    'bollinger_bands': BollingerBandsSettings,
    'stochastic': StochasticSettings,
    'atr': ATRSettings,
    'adx': ADXSettings,
    'cci': CCISettings,
    'williams_r': WilliamsRSettings,
    'obv': OBVSettings,
    'parabolic_sar': ParabolicSARSettings,
    'ichimoku': IchimokuSettings,
}


def get_settings_class(indicator_name: str):
    """
    Get the settings class for a specific indicator.
    
    Args:
        indicator_name: Name of the indicator
        
    Returns:
        Type[BaseIndicatorSettings]: The settings class
        
    Raises:
        ValueError: If indicator name is not found
    """
    if indicator_name not in SETTINGS_REGISTRY:
        raise ValueError(
            f"Unknown indicator: {indicator_name}. "
            f"Available indicators: {', '.join(SETTINGS_REGISTRY.keys())}"
        )
    return SETTINGS_REGISTRY[indicator_name]


def create_settings(indicator_name: str, **kwargs) -> BaseIndicatorSettings:
    """
    Create settings instance for a specific indicator.
    
    Args:
        indicator_name: Name of the indicator
        **kwargs: Settings parameters
        
    Returns:
        BaseIndicatorSettings: Settings instance
        
    Example:
        >>> settings = create_settings('rsi', lookback_periods=14)
        >>> settings = create_settings('macd', fast_periods=12, slow_periods=26)
    """
    settings_class = get_settings_class(indicator_name)
    return settings_class(**kwargs)
