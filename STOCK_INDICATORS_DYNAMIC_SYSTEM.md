# Dynamic Stock Indicators System

## Overview

The crypto analysis platform now supports dynamic indicator creation using the `stock-indicators` Python package. This allows you to create indicators using any of the technical analysis functions available in the stock-indicators library, with custom settings classes that define the parameters for each indicator.

## Features

- **Dynamic Indicator Types**: Use any indicator from the stock-indicators package without writing custom calculator code
- **Settings Classes**: Pre-built settings classes for common indicators (RSI, MACD, SMA, EMA, Bollinger Bands, Stochastic, etc.)
- **Custom Settings**: Create your own settings classes for new indicators
- **Automatic Scoring**: Built-in methods to convert indicator values to -1.0 to 1.0 scores for comparison
- **Backward Compatible**: Existing custom calculators continue to work alongside stock-indicators

## Architecture

### Components

1. **BaseIndicatorSettings**: Abstract base class for all indicator settings
2. **Concrete Settings Classes**: RSISettings, MACDSettings, SMASettings, etc.
3. **StockIndicatorCalculator**: Adapter that bridges Django models with stock-indicators package
4. **Indicator Model**: Updated with `calculation_type` field to support both custom and stock-indicators

### Data Flow

```
Indicator Model
    └─> calculation_type = 'stock_indicator'
    └─> stock_indicator_name = 'rsi'
    └─> stock_indicator_settings = {'lookback_periods': 14, ...}
         └─> StockIndicatorCalculator
              └─> Loads RSISettings
              └─> Fetches TickerData from database
              └─> Calls stock_indicators.get_rsi()
              └─> Converts result to -1.0 to 1.0 score
              └─> Returns score
```

## Usage Examples

### Example 1: Creating an RSI Indicator

Using the Django admin or API:

```python
from main.models import Indicator, IndicatorType

# Create indicator type (if not exists)
rsi_type, _ = IndicatorType.objects.get_or_create(
    name="Momentum",
    defaults={'description': 'Momentum oscillators', 'color': '#3498db'}
)

# Create RSI indicator using stock-indicators
indicator = Indicator.objects.create(
    title="Bitcoin RSI (14-day)",
    description="RSI indicator for Bitcoin with 14-day period",
    calculation_type='stock_indicator',
    stock_indicator_name='rsi',
    stock_indicator_settings={
        'lookback_periods': 14,
        'oversold_threshold': 30.0,
        'overbought_threshold': 70.0
    },
    calculator_config={
        'ticker': 'X:BTCUSD',
        'score_method': 'threshold',  # Use threshold-based scoring
        'lookback_days': 100  # Fetch 100 days of data
    },
    indicator_type=rsi_type,
    auto_update=True
)

# Calculate value for a specific date
from datetime import date
score = indicator.calculate_value(date=date(2025, 1, 9))
print(f"RSI Score: {score}")  # Returns value between -1.0 and 1.0
```

### Example 2: Creating a MACD Indicator

```python
indicator = Indicator.objects.create(
    title="Ethereum MACD",
    description="MACD indicator for Ethereum",
    calculation_type='stock_indicator',
    stock_indicator_name='macd',
    stock_indicator_settings={
        'fast_periods': 12,
        'slow_periods': 26,
        'signal_periods': 9
    },
    calculator_config={
        'ticker': 'X:ETHUSD',
        'score_method': 'momentum',  # Use momentum-based scoring
    },
    auto_update=True
)
```

### Example 3: Creating a Bollinger Bands Indicator

```python
indicator = Indicator.objects.create(
    title="BTC Bollinger Bands",
    description="Bollinger Bands with 20-day period and 2 standard deviations",
    calculation_type='stock_indicator',
    stock_indicator_name='bollinger_bands',
    stock_indicator_settings={
        'lookback_periods': 20,
        'standard_deviations': 2.0
    },
    calculator_config={
        'ticker': 'X:BTCUSD',
        'score_method': 'range',
    },
    auto_update=True
)
```

### Example 4: Using the Settings Classes Directly

```python
from main.indicators import RSISettings, create_settings

# Method 1: Direct instantiation
rsi_settings = RSISettings(
    lookback_periods=14,
    oversold_threshold=30.0,
    overbought_threshold=70.0
)

# Method 2: Using factory function
macd_settings = create_settings(
    'macd',
    fast_periods=12,
    slow_periods=26,
    signal_periods=9
)

# Convert to dict for storage
settings_dict = rsi_settings.to_dict()
print(settings_dict)
# Output: {'lookback_periods': 14, 'oversold_threshold': 30.0, 'overbought_threshold': 70.0}

# Get calculator config
calc_config = rsi_settings.get_calculator_config()
print(calc_config)
# Output: {
#     'indicator_name': 'rsi',
#     'indicator_settings': {...},
#     'settings_class': 'main.indicators.settings.RSISettings'
# }
```

## Available Indicators

The following indicators from stock-indicators are supported:

| Indicator | Settings Class | Key Parameters |
|-----------|---------------|----------------|
| RSI | RSISettings | lookback_periods, oversold_threshold, overbought_threshold |
| MACD | MACDSettings | fast_periods, slow_periods, signal_periods |
| SMA | SMASettings | lookback_periods |
| EMA | EMASettings | lookback_periods |
| Bollinger Bands | BollingerBandsSettings | lookback_periods, standard_deviations |
| Stochastic | StochasticSettings | lookback_periods, signal_periods, smooth_periods |
| ATR | ATRSettings | lookback_periods |
| ADX | ADXSettings | lookback_periods |
| CCI | CCISettings | lookback_periods, oversold_threshold, overbought_threshold |
| Williams %R | WilliamsRSettings | lookback_periods, oversold_threshold, overbought_threshold |
| OBV | OBVSettings | sma_periods |
| Parabolic SAR | ParabolicSARSettings | acceleration_step, max_acceleration |
| Ichimoku | IchimokuSettings | tenkan_periods, kijun_periods, senkou_span_b_periods |

## Score Methods

The system converts indicator values to scores between -1.0 and 1.0 for easy comparison:

### 1. Threshold Method (for oscillators)

Used for: RSI, Stochastic, CCI, Williams %R

- **1.0** (Very Bullish): Indicator is oversold (e.g., RSI < 30)
- **0.0** (Neutral): Indicator is at neutral level (e.g., RSI = 50)
- **-1.0** (Very Bearish): Indicator is overbought (e.g., RSI > 70)

### 2. Momentum Method (for trend indicators)

Used for: MACD, OBV

- **Positive**: Indicator shows upward momentum
- **Negative**: Indicator shows downward momentum
- Magnitude indicates strength of trend

### 3. Range Method (for bounded indicators)

Used for: Bollinger Bands, other range-based indicators

- Normalizes indicator value to -1.0 to 1.0 range based on expected bounds

### 4. Auto Method (default)

Automatically selects the best scoring method based on indicator type.

## Creating Custom Settings Classes

You can create your own settings classes for new indicators:

```python
from dataclasses import dataclass
from main.indicators.settings import BaseIndicatorSettings

@dataclass
class CustomIndicatorSettings(BaseIndicatorSettings):
    """Settings for a custom indicator."""
    
    # Define your parameters
    period: int = 20
    threshold: float = 0.5
    some_option: str = 'default'
    
    def get_indicator_name(self) -> str:
        """Return the stock-indicators function name."""
        return "custom_indicator"  # e.g., 'some_indicator'
```

Then register it in the SETTINGS_REGISTRY:

```python
from main.indicators.settings import SETTINGS_REGISTRY
from .my_custom_settings import CustomIndicatorSettings

SETTINGS_REGISTRY['custom_indicator'] = CustomIndicatorSettings
```

## Database Migration

After adding the new fields to the Indicator model, create and run a migration:

```bash
cd django_app
python manage.py makemigrations
python manage.py migrate
```

The migration will add these fields to the `indicators` table:
- `calculation_type` (default: 'custom')
- `stock_indicator_name`
- `stock_indicator_settings_class`
- `stock_indicator_settings`

Existing indicators will continue to work with `calculation_type='custom'`.

## Admin Integration

Update your Django admin to support the new fields:

```python
from django.contrib import admin
from .models import Indicator

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ['title', 'calculation_type', 'stock_indicator_name', 'auto_update']
    list_filter = ['calculation_type', 'auto_update', 'indicator_type']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'url', 'indicator_type')
        }),
        ('Calculation Type', {
            'fields': ('calculation_type',)
        }),
        ('Custom Calculator (for calculation_type=custom)', {
            'fields': ('calculator_class', 'calculator_config'),
            'classes': ('collapse',)
        }),
        ('Stock-Indicators (for calculation_type=stock_indicator)', {
            'fields': (
                'stock_indicator_name',
                'stock_indicator_settings_class',
                'stock_indicator_settings'
            ),
            'classes': ('collapse',)
        }),
        ('Options', {
            'fields': ('auto_update',)
        }),
    )
```

## Testing

Test your new indicators:

```python
from datetime import date, timedelta
from main.models import Indicator

# Get indicator
indicator = Indicator.objects.get(title="Bitcoin RSI (14-day)")

# Test calculation
today = date.today()
score = indicator.calculate_value(date=today)
print(f"Score for {today}: {score}")

# Test multiple dates
for i in range(7):
    test_date = today - timedelta(days=i)
    try:
        score = indicator.calculate_value(date=test_date)
        print(f"{test_date}: {score:.3f}")
    except Exception as e:
        print(f"{test_date}: Error - {e}")
```

## Troubleshooting

### ImportError: stock-indicators package not installed

```bash
pip install stock-indicators
```

### ValueError: Ticker not found

Ensure the ticker exists in your database:
```python
from main.models import Ticker
ticker = Ticker.objects.get(ticker='X:BTCUSD')
```

### ValueError: No data available

Check that you have historical price data:
```python
from main.models import TickerData
data_count = TickerData.objects.filter(ticker__ticker='X:BTCUSD').count()
print(f"Data points: {data_count}")
```

### ValueError: Insufficient data

Increase `lookback_days` in calculator_config:
```python
indicator.calculator_config['lookback_days'] = 200
indicator.save()
```

## Best Practices

1. **Use descriptive titles**: "Bitcoin RSI (14-day)" instead of just "RSI"
2. **Document settings**: Add description explaining the parameters used
3. **Test before auto_update**: Calculate manually first, then enable auto_update
4. **Monitor performance**: Some indicators require significant historical data
5. **Use appropriate score_method**: Match the scoring method to indicator type
6. **Version your settings**: If changing parameters, consider creating a new indicator

## Future Enhancements

Potential additions to the system:

- [ ] Batch calculation for multiple dates
- [ ] Caching of intermediate results
- [ ] Custom score functions per indicator
- [ ] Composite indicators (combining multiple indicators)
- [ ] Visualization of indicator scores over time
- [ ] Alert system for threshold crossings
- [ ] Performance optimization for large datasets

## References

- [stock-indicators Documentation](https://python.stockindicators.dev/)
- [Stock Indicators GitHub](https://github.com/DaveSkender/Stock.Indicators)
- Technical Analysis Guides for each indicator
