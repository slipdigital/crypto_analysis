# Global Liquidity Data Collection

This module collects global liquidity data from the Federal Reserve Economic Data (FRED) API, which provides free access to key monetary aggregates and central bank balance sheet data.

## Overview

Global liquidity is a critical macro indicator for cryptocurrency markets. When central banks expand their balance sheets (quantitative easing), it typically correlates with rising crypto prices. When they contract (quantitative tightening), crypto markets often decline.

## Setup

### 1. Get a FRED API Key

1. Visit https://fred.stlouisfed.org/
2. Create a free account
3. Request an API key at https://fred.stlouisfed.org/docs/api/api_key.html
4. Add your API key to `config/settings.json`:

```json
{
  "fred": {
    "api_key": "your_actual_api_key_here"
  }
}
```

### 2. Create Database Table

The script will automatically create the `global_liquidity` table when first run, but you can also use the verify schema tool:

```bash
python verify_schema.py
```

## Tracked Series

The script collects the following key liquidity indicators:

| Series ID | Name | Description | Frequency |
|-----------|------|-------------|-----------|
| M2SL | US M2 Money Supply | Cash, checking, savings deposits, and money market securities | Monthly |
| WALCL | Federal Reserve Total Assets | All assets held by the Fed (balance sheet size) | Weekly |
| BOGMBASE | US Monetary Base | Currency in circulation plus bank reserves | Monthly |
| ECBASSETSW | European Central Bank Assets | Total ECB balance sheet | Weekly |
| JPNASSETS | Bank of Japan Total Assets | Total BoJ balance sheet | Monthly |

## Usage

### List Available Series

```bash
python collect_global_liquidity.py --list
```

### Collect All Series (Full History)

```bash
python collect_global_liquidity.py
```

This fetches all available historical data for all configured series.

### Collect Specific Series

```bash
python collect_global_liquidity.py --series M2SL WALCL
```

### Collect Recent Data Only

```bash
# Last 90 days
python collect_global_liquidity.py --days 90

# Last 365 days
python collect_global_liquidity.py --days 365
```

### Use Custom API Key

```bash
python collect_global_liquidity.py --api-key YOUR_API_KEY_HERE
```

## Database Schema

The `global_liquidity` table stores:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| series_id | String | FRED series identifier (e.g., M2SL) |
| series_name | String | Human-readable name |
| date | Date | Observation date |
| value | Float | Value in billions |
| units | String | Units (e.g., "Billions of Dollars") |
| frequency | String | Data frequency (Monthly, Weekly, etc.) |
| collected_at | String | When data was collected (ISO format) |

**Unique Constraint:** (series_id, date) - prevents duplicate entries

## Examples

### Initial Collection

```bash
# Collect all historical data for all series
python collect_global_liquidity.py
```

Expected output:
```
Collecting global liquidity data...
Date range: All available to 2025-10-14
Series: M2SL, WALCL, BOGMBASE, ECBASSETSW, JPNASSETS
================================================================================
Fetching M2SL...
  Retrieved 852 observations for M2SL
  M2SL: Inserted 852, Updated 0
Fetching WALCL...
  Retrieved 650 observations for WALCL
  WALCL: Inserted 650, Updated 0
...
================================================================================
Collection complete!
Total records inserted: 3500
Total records updated: 0

Latest values:
--------------------------------------------------------------------------------
M2SL         (2025-09-01): 21,432.50 Billions of Dollars
WALCL        (2025-10-09): 7,123.45 Billions of Dollars
...
```

### Regular Updates

```bash
# Update with last 30 days of data
python collect_global_liquidity.py --days 30
```

### Monitoring Federal Reserve Balance Sheet

```bash
# Track Fed balance sheet only
python collect_global_liquidity.py --series WALCL
```

## API Rate Limits

FRED API is free and generous:
- **120 requests per 60 seconds**
- No daily limits for registered users
- Real-time data updates

The script makes one request per series, so it's very efficient.

## Next Steps

### 1. Schedule Regular Updates

Add to your scheduler or cron:

```bash
# Update daily
python collect_global_liquidity.py --days 7
```

### 2. Create Visualizations

The data is now ready for charting in your Flask dashboard:
- Plot global liquidity vs. total crypto market cap
- Show correlations between M2 growth and BTC price
- Compare central bank balance sheet expansions

### 3. Calculate Aggregate Global Liquidity

You can sum M2SL, ECBASSETSW, JPNASSETS (after currency conversion) to get total global liquidity.

## Troubleshooting

### API Key Error

```
Error: FRED API key not configured!
```

**Solution:** Add your API key to `config/settings.json` or use `--api-key` argument

### No Data Retrieved

```
Retrieved 0 observations for SERIES_ID
```

**Possible causes:**
- Invalid series ID
- Series discontinued
- API rate limit (wait 60 seconds)
- Network issues

### Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:** Ensure PostgreSQL is running and config/settings.json has correct credentials

## Additional Resources

- **FRED API Documentation:** https://fred.stlouisfed.org/docs/api/
- **FRED Series Search:** https://fred.stlouisfed.org/
- **Global Liquidity Research:** Search for "central bank balance sheets" or "global M2"

## Data Interpretation

### M2 Money Supply (M2SL)
- **Rising M2:** More money in circulation → typically bullish for assets
- **Falling M2:** Money supply contracting → typically bearish

### Federal Reserve Assets (WALCL)
- **Expanding balance sheet:** Quantitative easing (QE) → printing money
- **Contracting balance sheet:** Quantitative tightening (QT) → reducing money supply

### Combined Effect
When all major central banks (Fed, ECB, BoJ, PBoC) expand simultaneously, it creates the most favorable environment for risk assets like crypto.
