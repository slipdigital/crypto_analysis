# Quick Start: Stock Indicators Dynamic System

## TL;DR

Create indicators using the stock-indicators package without writing custom code.

## Installation

```bash
cd django_app
pip install stock-indicators
python manage.py makemigrations
python manage.py migrate
```

## Create an Indicator (Python)

```python
from main.models import Indicator

# RSI Example
indicator = Indicator.objects.create(
    title="Bitcoin RSI",
    calculation_type='stock_indicator',
    stock_indicator_name='rsi',
    stock_indicator_settings={
        'lookback_periods': 14,
        'oversold_threshold': 30.0,
        'overbought_threshold': 70.0
    },
    calculator_config={'ticker': 'X:BTCUSD'},
    auto_update=True
)

# Calculate
from datetime import date
score = indicator.calculate_value(date=date.today())
print(f"Score: {score}")  # -1.0 to 1.0
```

## Available Indicators

Quick reference for settings:

```python
# RSI
'rsi' → RSISettings(lookback_periods=14)

# MACD
'macd' → MACDSettings(fast_periods=12, slow_periods=26, signal_periods=9)

# Moving Averages
'sma' → SMASettings(lookback_periods=20)
'ema' → EMASettings(lookback_periods=20)

# Bollinger Bands
'bollinger_bands' → BollingerBandsSettings(lookback_periods=20, standard_deviations=2.0)

# Stochastic
'stoch' → StochasticSettings(lookback_periods=14, signal_periods=3, smooth_periods=3)

# Others
'atr' → ATRSettings(lookback_periods=14)
'adx' → ADXSettings(lookback_periods=14)
'cci' → CCISettings(lookback_periods=20)
'williams_r' → WilliamsRSettings(lookback_periods=14)
'obv' → OBVSettings(sma_periods=None)
```

## Score Methods

Set in `calculator_config`:

```python
calculator_config={
    'ticker': 'X:BTCUSD',
    'score_method': 'threshold',  # or 'momentum', 'range', 'auto'
}
```

- **threshold**: For oscillators (RSI, Stochastic, etc.)
- **momentum**: For trend indicators (MACD, OBV)
- **auto**: Automatically picks best method

## Using Settings Classes

```python
from main.indicators import RSISettings, create_settings

# Direct
settings = RSISettings(lookback_periods=21)

# Factory
settings = create_settings('macd', fast_periods=10, slow_periods=20)

# To dict
config = settings.to_dict()

# From dict
settings = RSISettings.from_dict({'lookback_periods': 14})
```

## Model Fields

### For stock-indicators:
```python
calculation_type = 'stock_indicator'
stock_indicator_name = 'rsi'  # Required
stock_indicator_settings = {...}  # Required
stock_indicator_settings_class = None  # Optional
calculator_config = {...}  # ticker, score_method, etc.
```

### For custom calculators:
```python
calculation_type = 'custom'
calculator_class = 'main.indicators.rsi.RSICalculator'
calculator_config = {...}
```

## Complete Example

```python
from main.models import Indicator, IndicatorType
from datetime import date, timedelta

# Create indicator type
momentum, _ = IndicatorType.objects.get_or_create(
    name="Momentum",
    defaults={'color': '#3498db'}
)

# Create multiple indicators
indicators_config = [
    {
        'title': 'BTC RSI-14',
        'name': 'rsi',
        'settings': {'lookback_periods': 14},
        'score_method': 'threshold'
    },
    {
        'title': 'BTC MACD',
        'name': 'macd',
        'settings': {'fast_periods': 12, 'slow_periods': 26, 'signal_periods': 9},
        'score_method': 'momentum'
    },
    {
        'title': 'BTC SMA-50',
        'name': 'sma',
        'settings': {'lookback_periods': 50},
        'score_method': 'range'
    },
]

for config in indicators_config:
    Indicator.objects.create(
        title=config['title'],
        calculation_type='stock_indicator',
        stock_indicator_name=config['name'],
        stock_indicator_settings=config['settings'],
        calculator_config={
            'ticker': 'X:BTCUSD',
            'score_method': config['score_method']
        },
        indicator_type=momentum,
        auto_update=True
    )

# Calculate all indicators for today
today = date.today()
for indicator in Indicator.objects.filter(calculation_type='stock_indicator'):
    try:
        score = indicator.calculate_value(date=today)
        print(f"{indicator.title}: {score:.3f}")
    except Exception as e:
        print(f"{indicator.title}: Error - {e}")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ImportError | `pip install stock-indicators` |
| Ticker not found | Check `Ticker.objects.filter(ticker='X:BTCUSD')` |
| No data | Check `TickerData.objects.filter(ticker__ticker='X:BTCUSD')` |
| Insufficient data | Increase `calculator_config['lookback_days']` |

## Next Steps

- Read full docs: [STOCK_INDICATORS_DYNAMIC_SYSTEM.md](STOCK_INDICATORS_DYNAMIC_SYSTEM.md)
- Create custom settings classes for new indicators
- Set up auto-update schedules for indicators
- Build dashboards with indicator scores
