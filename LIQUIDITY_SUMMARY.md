# Global Liquidity Data Collection - Summary

## 📊 What You've Got

I've created a complete system for collecting and tracking global liquidity data from the Federal Reserve Economic Data (FRED) API.

## 🚀 Quick Start

1. **Get a FREE FRED API key** (takes 2 minutes):
   - Visit: https://fred.stlouisfed.org/docs/api/api_key.html
   - Sign up and request key
   - Add to `config/settings.json`:
   ```json
   {
     "fred": {
       "api_key": "your_key_here"
     }
   }
   ```

2. **Collect data** (one-time, ~1 minute):
   ```bash
   .\.venv\Scripts\python.exe collect_global_liquidity.py
   ```

3. **Check status**:
   ```bash
   .\.venv\Scripts\python.exe check_liquidity_data.py
   ```

## 📁 Files Created

1. **`collect_global_liquidity.py`** - Main data collection script
   - Fetches data from FRED API
   - Stores in PostgreSQL database
   - Supports full history or incremental updates

2. **`check_liquidity_data.py`** - Status checker
   - Shows what data you have
   - Latest values and trends
   - Update recommendations

3. **`models.py`** - Updated with `GlobalLiquidity` model
   - New table: `global_liquidity`
   - Stores time series data for each indicator

4. **Documentation**:
   - `GLOBAL_LIQUIDITY_README.md` - Detailed guide
   - `QUICKSTART_LIQUIDITY.md` - Quick reference
   - `LIQUIDITY_SUMMARY.md` - This file

## 📈 Data Tracked

| Series | Name | Updates |
|--------|------|---------|
| M2SL | US M2 Money Supply | Monthly |
| WALCL | Fed Balance Sheet | Weekly (Thu) |
| BOGMBASE | US Monetary Base | Monthly |
| ECBASSETSW | ECB Balance Sheet | Weekly (Fri) |
| JPNASSETS | Bank of Japan Assets | Monthly |

## 💡 Why This Matters

Global liquidity is THE key macro indicator for crypto:

- **2020-2021**: Fed balance sheet ↑ → Bitcoin $7K → $69K
- **2022**: Fed QT (quantitative tightening) → Bitcoin crashes to $15K
- **2023-2024**: Liquidity stabilizes → Bitcoin recovers

**When money printer go brrrr → crypto go up 🚀**

## 🔧 Usage Examples

### List available series
```bash
.\.venv\Scripts\python.exe collect_global_liquidity.py --list
```

### Collect everything (first time)
```bash
.\.venv\Scripts\python.exe collect_global_liquidity.py
```

### Regular updates (weekly)
```bash
.\.venv\Scripts\python.exe collect_global_liquidity.py --days 30
```

### Check current data
```bash
.\.venv\Scripts\python.exe check_liquidity_data.py
```

Output example:
```
================================================================================
GLOBAL LIQUIDITY DATA STATUS
================================================================================

Total records: 3,542
Series tracked: 5

--------------------------------------------------------------------------------

✅ M2SL: US M2 Money Supply
   Records: 852
   Date range: 1959-01-01 to 2025-09-01
   Latest value: 21,432.50 Billions of Dollars
   Last updated: 13 days ago
   30-day change: 📈 +45.20 (+0.21%)

✅ WALCL: Federal Reserve Total Assets
   Records: 650
   Date range: 2002-12-18 to 2025-10-09
   Latest value: 7,123.45 Billions of Dollars
   Last updated: 5 days ago
   30-day change: 📉 -12.30 (-0.17%)
...
```

## 🎯 Next Steps

### 1. Automate Updates
Add to your update script or scheduler:
```python
# In your scheduler or update_all_data.py
import subprocess
subprocess.run([r".\.venv\Scripts\python.exe", "collect_global_liquidity.py", "--days", "30"])
```

### 2. Add to Flask Dashboard
Create a new page showing:
- Current global liquidity levels
- Historical charts
- Correlation with crypto market cap
- Fed balance sheet vs. Bitcoin price

### 3. Calculate Aggregate Liquidity
Sum all major central banks (with currency conversion):
```python
# Pseudo-code
total_liquidity_usd = M2SL + WALCL + (ECBASSETSW * EUR_USD_rate) + (JPNASSETS * JPY_USD_rate)
```

### 4. Build Alerts
Set up notifications when:
- Fed balance sheet changes >1% week-over-week
- M2 money supply accelerates/decelerates
- Global liquidity crosses key thresholds

## 📊 Database Schema

```sql
CREATE TABLE global_liquidity (
    id SERIAL PRIMARY KEY,
    series_id VARCHAR NOT NULL,      -- e.g., 'M2SL'
    series_name VARCHAR,              -- e.g., 'US M2 Money Supply'
    date DATE NOT NULL,               -- Observation date
    value FLOAT,                      -- Value in billions
    units VARCHAR,                    -- e.g., 'Billions of Dollars'
    frequency VARCHAR,                -- e.g., 'Monthly'
    collected_at VARCHAR,             -- ISO timestamp
    UNIQUE(series_id, date)
);
```

## 🔍 Advanced Analysis Ideas

1. **Liquidity vs. Bitcoin Price**
   - Overlay WALCL with BTC price
   - Calculate correlation coefficient
   - Identify lead/lag relationship

2. **Global Liquidity Index**
   - Combine all central banks into single metric
   - Normalize to 100 = Jan 2020
   - Track growth rate

3. **Rate of Change**
   - Plot week-over-week changes in Fed balance sheet
   - Highlight acceleration/deceleration periods
   - Compare to crypto market volatility

4. **Macro Dashboard**
   - Global liquidity (left axis)
   - Total crypto market cap (right axis)
   - Correlation metric at top

## 📚 Resources

- **FRED API Docs**: https://fred.stlouisfed.org/docs/api/
- **Get API Key**: https://fred.stlouisfed.org/docs/api/api_key.html
- **Browse Series**: https://fred.stlouisfed.org/
- **Fed Balance Sheet**: Search FRED for "WALCL"
- **M2 Money Supply**: Search FRED for "M2SL"

## ⚙️ Configuration

All settings in `config/settings.json`:

```json
{
  "fred": {
    "api_key": "YOUR_KEY_HERE",
    "comment": "Get free key from https://fred.stlouisfed.org/docs/api/api_key.html"
  },
  "postgres": {
    "host": "localhost",
    "port": 5432,
    "database": "crypto_tpi",
    "username": "postgres",
    "password": "123123"
  }
}
```

## 🐛 Troubleshooting

**"FRED API key not configured"**
→ Add key to `config/settings.json`

**"relation 'global_liquidity' does not exist"**
→ Run the script once to create the table: `collect_global_liquidity.py`

**"ModuleNotFoundError: No module named 'sqlalchemy'"**
→ Use `.\.venv\Scripts\python.exe` not just `python`

**Rate limit error**
→ FRED allows 120 requests/minute, script only makes 5, so this shouldn't happen

## 📞 Support

- Check `GLOBAL_LIQUIDITY_README.md` for detailed documentation
- Check `QUICKSTART_LIQUIDITY.md` for step-by-step guide
- FRED API issues: https://fred.stlouisfed.org/docs/api/

---

**You now have a complete macro analysis layer for your crypto dashboard!** 🎉
