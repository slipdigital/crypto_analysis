# Quick Start: Global Liquidity Data Collection

## Step 1: Get Your FREE FRED API Key

1. Go to: https://fred.stlouisfed.org/
2. Click "My Account" → "Sign Up" (if you don't have an account)
3. Once logged in, go to: https://fred.stlouisfed.org/docs/api/api_key.html
4. Click "Request API Key"
5. Fill out the simple form (takes 30 seconds)
6. You'll receive your API key immediately

## Step 2: Add API Key to Config

Edit `config/settings.json` and add your API key:

```json
{
  "fred": {
    "api_key": "paste_your_actual_api_key_here"
  }
}
```

## Step 3: Run the Script

### View Available Series
```bash
.\.venv\Scripts\python.exe collect_global_liquidity.py --list
```

### Collect All Data (First Time)
```bash
.\.venv\Scripts\python.exe collect_global_liquidity.py
```

This will:
- Fetch ALL historical data for 5 key liquidity indicators
- Create the `global_liquidity` table in your database
- Store ~3,000-4,000 data points going back decades
- Show you the latest values

### Update Regularly (Daily/Weekly)
```bash
# Get just the last 30 days (quick update)
.\.venv\Scripts\python.exe collect_global_liquidity.py --days 30
```

## What You're Tracking

1. **M2SL** - US Money Supply (Monthly)
   - The broadest measure of US money in circulation
   - Currently ~$21 trillion

2. **WALCL** - Federal Reserve Balance Sheet (Weekly)
   - Total Fed assets (shows QE/QT in real-time)
   - Currently ~$7 trillion

3. **BOGMBASE** - US Monetary Base (Monthly)
   - Currency + bank reserves
   - Most direct measure of money printing

4. **ECBASSETSW** - European Central Bank (Weekly)
   - ECB balance sheet
   - Currently ~€7 trillion

5. **JPNASSETS** - Bank of Japan (Monthly)
   - BoJ balance sheet
   - Currently ~¥750 trillion

## Why This Matters for Crypto

**Global liquidity drives crypto prices:**

- 🟢 **More liquidity** (QE) → More money → Higher crypto prices
- 🔴 **Less liquidity** (QT) → Less money → Lower crypto prices

**Example:** When the Fed balance sheet (WALCL) expanded rapidly in 2020-2021, Bitcoin went from $7K to $69K. When they started QT in 2022, Bitcoin crashed to $15K.

## Next Steps

Once you have the data collected, you can:

1. **Visualize it** - Add charts to your Flask dashboard
2. **Analyze correlations** - Compare liquidity vs. BTC price
3. **Calculate aggregate** - Sum all central banks for total global liquidity
4. **Track changes** - Monitor week-over-week changes in Fed balance sheet

## Common Issues

**"Error: FRED API key not configured!"**
→ Add your API key to `config/settings.json`

**"ModuleNotFoundError: No module named 'sqlalchemy'"**
→ Use `.\.venv\Scripts\python.exe` instead of `python`

**"No observations found"**
→ Check the series ID spelling, some series may be discontinued

## Data Updates Schedule

- **WALCL** (Fed Assets): Updates every Thursday
- **ECBASSETSW** (ECB Assets): Updates every Friday
- **M2SL** (M2 Money Supply): Updates monthly (~14th)
- **BOGMBASE** (Monetary Base): Updates monthly (~1st)
- **JPNASSETS** (BoJ Assets): Updates monthly

**Recommendation:** Run `--days 30` weekly to catch all updates.
