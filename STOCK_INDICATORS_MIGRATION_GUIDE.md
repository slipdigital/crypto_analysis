# Migration Guide: Upgrading to Stock-Indicators Dynamic System

## Overview

This guide helps you migrate from custom indicator calculators to the new stock-indicators dynamic system.

## Prerequisites

- Django 5.0+
- Python 3.12+
- Existing crypto_analysis project

## Step-by-Step Migration

### Step 1: Install Package

```bash
cd django_app
pip install stock-indicators
```

Or add to requirements.txt:
```
stock-indicators>=1.0.0
```

### Step 2: Run Database Migration

```bash
python manage.py migrate
```

This adds new fields to the Indicator model:
- `calculation_type`
- `stock_indicator_name`
- `stock_indicator_settings`
- `stock_indicator_settings_class`

### Step 3: Verify Installation

Test that imports work:

```python
python -c "from main.indicators import create_rsi_indicator; print('Success!')"
```

### Step 4: Create Your First Stock-Indicator

```python
from main.indicators import create_rsi_indicator

indicator = create_rsi_indicator(
    title="Bitcoin RSI Test",
    ticker='X:BTCUSD',
    lookback_periods=14
)

# Test calculation
from datetime import date
score = indicator.calculate_value(date=date.today())
print(f"Score: {score}")
```

## Migration Scenarios

### Scenario 1: Replacing Custom RSI with Stock-Indicators RSI

**Before (Custom):**
```python
indicator = Indicator.objects.create(
    title="BTC RSI",
    calculator_class='main.indicators.rsi.RSICalculator',
    calculator_config={
        'ticker': 'X:BTCUSD',
        'period': 14,
        'oversold_threshold': 30,
        'overbought_threshold': 70
    }
)
```

**After (Stock-Indicators):**
```python
from main.indicators import create_rsi_indicator

indicator = create_rsi_indicator(
    title="BTC RSI",
    ticker='X:BTCUSD',
    lookback_periods=14,
    oversold_threshold=30.0,
    overbought_threshold=70.0
)
```

### Scenario 2: Batch Migration

If you have many custom indicators to migrate:

```python
from main.models import Indicator
from main.indicators import create_stock_indicator

# Get all custom RSI indicators
custom_rsis = Indicator.objects.filter(
    calculator_class='main.indicators.rsi.RSICalculator'
)

for old_indicator in custom_rsis:
    config = old_indicator.calculator_config
    
    # Create equivalent stock-indicator
    new_indicator = create_stock_indicator(
        title=f"{old_indicator.title} (New)",
        indicator_name='rsi',
        ticker=config.get('ticker', 'X:BTCUSD'),
        lookback_periods=config.get('period', 14),
        oversold_threshold=config.get('oversold_threshold', 30.0),
        overbought_threshold=config.get('overbought_threshold', 70.0),
        indicator_type=old_indicator.indicator_type,
        auto_update=old_indicator.auto_update
    )
    
    print(f"Migrated: {old_indicator.title} -> {new_indicator.title}")
    
    # Optional: Disable old indicator instead of deleting
    old_indicator.auto_update = False
    old_indicator.save()
```

### Scenario 3: Keeping Both Systems

You can run both custom and stock-indicators side by side:

```python
# Custom calculator (existing)
custom_indicator = Indicator.objects.filter(
    calculation_type='custom'
).first()

# Stock-indicator (new)
stock_indicator = Indicator.objects.filter(
    calculation_type='stock_indicator'
).first()

# Both work the same way
from datetime import date
custom_score = custom_indicator.calculate_value(date=date.today())
stock_score = stock_indicator.calculate_value(date=date.today())
```

## Configuration Mapping

### RSI Configuration

| Custom Config | Stock-Indicator Config | Notes |
|--------------|------------------------|-------|
| `period` | `lookback_periods` | Parameter name changed |
| `oversold_threshold` | `oversold_threshold` | Same |
| `overbought_threshold` | `overbought_threshold` | Same |

### MACD Configuration

Stock-indicators uses standard parameters:
```python
{
    'fast_periods': 12,
    'slow_periods': 26,
    'signal_periods': 9
}
```

### Moving Average Configuration

| Custom | Stock-Indicator |
|--------|----------------|
| `short_period` | `lookback_periods` (for single MA) |
| `long_period` | Use separate SMA/EMA indicators |

## Data Migration

If you want to migrate historical IndicatorData:

```python
from main.models import Indicator, IndicatorData

old_indicator = Indicator.objects.get(id=1)  # Old custom indicator
new_indicator = Indicator.objects.get(id=2)  # New stock-indicator

# Copy all historical data
historical_data = IndicatorData.objects.filter(indicator=old_indicator)

for data_point in historical_data:
    IndicatorData.objects.create(
        indicator=new_indicator,
        date=data_point.date,
        value=data_point.value,
        created_at=data_point.created_at,
        updated_at=data_point.updated_at
    )
```

## Testing Migration

### 1. Verify Calculations Match

```python
from datetime import date, timedelta

old_indicator = Indicator.objects.get(title="Old RSI")
new_indicator = Indicator.objects.get(title="New RSI")

# Test for multiple dates
test_dates = [date.today() - timedelta(days=i) for i in range(7)]

for test_date in test_dates:
    old_score = old_indicator.calculate_value(date=test_date)
    new_score = new_indicator.calculate_value(date=test_date)
    
    diff = abs(old_score - new_score)
    status = "✓" if diff < 0.01 else "✗"
    
    print(f"{status} {test_date}: Old={old_score:.3f}, New={new_score:.3f}, Diff={diff:.3f}")
```

### 2. Performance Testing

```python
import time

def benchmark_indicator(indicator, num_calculations=10):
    start = time.time()
    
    for i in range(num_calculations):
        test_date = date.today() - timedelta(days=i)
        indicator.calculate_value(date=test_date)
    
    elapsed = time.time() - start
    return elapsed / num_calculations

old_time = benchmark_indicator(old_indicator)
new_time = benchmark_indicator(new_indicator)

print(f"Old calculator: {old_time*1000:.2f}ms per calculation")
print(f"New calculator: {new_time*1000:.2f}ms per calculation")
```

## Rollback Plan

If you need to rollback:

### 1. Keep Custom Calculators

Don't delete custom calculator files until you're confident in migration.

### 2. Database Rollback

```bash
# Revert migration
python manage.py migrate main 0002_previous_migration

# Or mark as not auto-update
Indicator.objects.filter(calculation_type='stock_indicator').update(auto_update=False)
```

### 3. Switch Back

```python
# Disable stock-indicators
stock_indicators = Indicator.objects.filter(calculation_type='stock_indicator')
stock_indicators.update(auto_update=False)

# Re-enable custom calculators
custom_indicators = Indicator.objects.filter(calculation_type='custom')
custom_indicators.update(auto_update=True)
```

## Common Issues

### Issue 1: Import Error

**Error:** `ModuleNotFoundError: No module named 'stock_indicators'`

**Solution:**
```bash
pip install stock-indicators
```

### Issue 2: Different Results

**Problem:** Stock-indicator gives different values than custom calculator

**Cause:** Different calculation methods or periods

**Solution:** 
- Verify period mappings (e.g., `period` vs `lookback_periods`)
- Check that both use same smoothing method
- RSI calculation can vary slightly between implementations

### Issue 3: Missing Data

**Error:** `ValueError: No data available for X:BTCUSD`

**Solution:**
```python
# Check that ticker exists and has data
from main.models import Ticker, TickerData

ticker = Ticker.objects.get(ticker='X:BTCUSD')
data_count = TickerData.objects.filter(ticker=ticker).count()
print(f"Data points: {data_count}")

# If missing, fetch data first
```

### Issue 4: Performance Issues

**Problem:** Stock-indicator calculations are slow

**Solution:**
```python
# Increase lookback_days to fetch more data at once
indicator.calculator_config['lookback_days'] = 200
indicator.save()

# Or implement caching
```

## Best Practices

1. **Test in Development First**: Don't migrate production indicators without testing
2. **Migrate Gradually**: Start with one indicator type at a time
3. **Keep Old Data**: Don't delete historical IndicatorData
4. **Compare Results**: Verify calculations match before switching
5. **Document Changes**: Note any differences in calculation methods
6. **Monitor Performance**: Track calculation times after migration

## Post-Migration Checklist

- [ ] All indicators migrated or plan documented
- [ ] Calculations verified against test dates
- [ ] Performance is acceptable
- [ ] Auto-update schedules updated
- [ ] Documentation updated with new indicator configs
- [ ] Team trained on new system
- [ ] Old custom calculators archived or documented
- [ ] Admin interface updated for new fields

## Support Resources

- Full Documentation: [STOCK_INDICATORS_DYNAMIC_SYSTEM.md](STOCK_INDICATORS_DYNAMIC_SYSTEM.md)
- Quick Reference: [STOCK_INDICATORS_QUICKSTART.md](STOCK_INDICATORS_QUICKSTART.md)
- Examples: [example_stock_indicators.py](django_app/example_stock_indicators.py)
- stock-indicators Docs: https://python.stockindicators.dev/

## Getting Help

If you encounter issues during migration:

1. Check error messages carefully
2. Review the troubleshooting section in main docs
3. Verify your data availability
4. Test with simple examples first
5. Compare configurations between old and new

## Timeline Recommendation

**Week 1: Setup and Testing**
- Install package
- Run migrations
- Create test indicators
- Verify calculations

**Week 2: Limited Migration**
- Migrate 1-2 indicator types
- Monitor for issues
- Gather feedback

**Week 3: Full Migration**
- Migrate remaining indicators
- Update documentation
- Train team

**Week 4: Optimization**
- Tune performance
- Add new indicators
- Remove old calculators (if desired)
