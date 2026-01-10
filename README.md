# Cryptocurrency Data Collection & Analysis System

A comprehensive Python system for collecting, storing, and analyzing cryptocurrency data with macro-economic indicators using the Polygon.io API and Federal Reserve Economic Data (FRED).

## Features

### Cryptocurrency Data
- **Polygon.io Integration**: Professional-grade cryptocurrency data
- **Ticker Management**: Track 600+ crypto tickers with metadata
- **Historical Data**: Fetch up to 2 years of historical OHLCV data
- **Market Cap Tracking**: Import and track market capitalizations
- **Database Storage**: PostgreSQL with SQLAlchemy ORM
- **CSV Storage**: Organized data storage for easy analysis

### Technical Indicators (NEW!)
- **Dynamic Stock-Indicators Integration**: Use any indicator from the stock-indicators Python package
- **13+ Pre-built Indicators**: RSI, MACD, SMA, EMA, Bollinger Bands, Stochastic, ATR, ADX, CCI, Williams %R, OBV, Parabolic SAR, Ichimoku
- **Custom Settings Classes**: Type-safe configuration for each indicator
- **Automatic Scoring**: Converts indicator values to -1.0 to 1.0 scores for easy comparison
- **Helper Functions**: Create indicators with simple one-liners
- **Backward Compatible**: Works alongside existing custom calculators
- **📖 See [STOCK_INDICATORS_QUICKSTART.md](STOCK_INDICATORS_QUICKSTART.md) for quick start guide**

### Macro-Economic Indicators
- **Global Liquidity Tracking**: Monitor central bank balance sheets and money supply
- **FRED API Integration**: Access to Federal Reserve economic data
- **Multi-Currency Support**: Track USD, EUR, and JPY liquidity measures
- **Historical Analysis**: Decades of monetary data for correlation studies

### Web Dashboard
- **Flask Application**: Modern Bootstrap 5 UI
- **Interactive Charts**: Top gainers/losers analysis
- **Filtering & Search**: Find tickers by multiple criteria
- **Data Editing**: Update market cap and other fields
- **Performance Metrics**: Track returns across multiple timeframes

### Automation
- **Robust Error Handling**: Comprehensive error handling and retry logic
- **Rate Limiting**: Optimized for API constraints
- **Data Validation**: Quality checks for collected data
- **Logging**: Detailed logging for monitoring and debugging

## Project Structure

```
crypto_analysis/
├── config/
│   └── settings.json              # Configuration (API keys, DB credentials)
├── crypto_data/
│   ├── crypto_tickers.csv         # Ticker list
│   ├── historical/                # Historical OHLCV data
│   └── daily_snapshots/           # Daily market snapshots
├── flask_app/
│   ├── app.py                     # Flask application
│   ├── templates/                 # HTML templates
│   └── static/                    # CSS and JavaScript
├── models.py                      # SQLAlchemy database models
├── update_tickers.py              # Collect ticker metadata
├── update_ticker_data.py          # Collect historical price data
├── collect_global_liquidity.py   # Collect macro liquidity data
├── check_liquidity_data.py        # Check liquidity data status
├── update_market_caps_from_csv.py # Import market cap data
├── verify_schema.py               # Database schema verification
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Polygon.io API (Recommended)**:
   ```bash
   python setup_polygon.py
   ```
   This interactive script will:
   - Guide you through API key setup
   - Test your connection
   - Optimize settings for your plan

   **Manual Setup Alternative**:
   - Sign up for a free account at [Polygon.io](https://polygon.io/)
   - Get your API key from the dashboard
   - Edit `config/settings.json` and replace `"YOUR_POLYGON_API_KEY"` with your actual API key

4. **Verify configuration**:
   The system comes with a pre-configured `config/settings.json` file optimized for Polygon.io.

## Usage

### Quick Start

**Run data collection once**:
Collects and reports on the top 30 crypto currencies by market cap

```bash
python crypto_collector.py
```

**Run with scheduler (daily collection at 9 AM)**:
```bash
python scheduler.py --mode daily --time 09:00
```

### Detailed Usage

#### 1. Manual Data Collection

```bash
# Collect all data (historical + current snapshot)
python crypto_collector.py

# The script will:
# - Fetch top 30 cryptocurrencies by market cap
# - Download 1 year of historical data for each
# - Save current market snapshot
# - Store everything in organized CSV files
```

#### 2. Scheduled Collection

```bash
# Daily collection at 9:00 AM
python scheduler.py --mode daily --time 09:00

# Weekly collection on Monday at 10:30 AM
python scheduler.py --mode weekly --day monday --time 10:30

# Run once immediately
python scheduler.py --mode once
```

#### 3. Data Management

```bash
# Create data backup
python data_utils.py --action backup

# Restore from backup
python data_utils.py --action restore --backup-path backup_20240827_143022

# Generate summary report
python data_utils.py --action summary

# Export combined data
python data_utils.py --action export --output all_crypto_data.csv
```

#### 4. Market Cap Report Generation

```bash
# Generate comprehensive market cap report (console + CSV + HTML)
python market_cap_report.py

# Generate short-term performance analysis report
python performance_report.py

# The reports will:
# - Calculate market cap for each cryptocurrency
# - Sort by market cap (highest first)
# - Analyze short-term price performance and momentum
# - Display formatted console output
# - Save CSV reports with detailed metrics
# - Show market insights and performance rankings
```

## 📊 Market Cap Report Features

The system includes a comprehensive market cap report generator that creates professional reports listing cryptocurrencies ordered by market cap:

**Report Formats:**
- **Console Display**: Formatted table with rankings and insights
- **CSV Export**: Detailed data for spreadsheet analysis
- **HTML Report**: Professional web-ready format with styling

**Key Features:**
- Automatic market cap calculation (Price × Circulating Supply)
- Sorting by market cap (highest first)
- Market insights (Bitcoin dominance, top 10 share)
- Professional formatting with currency symbols
- Multiple export formats

**Sample Console Output:**
```
🏆 CRYPTOCURRENCY MARKET CAP REPORT
📅 Report Date: 2025-08-27
📊 Total Cryptocurrencies: 30
💰 Total Market Cap: $3.18T

Rank Symbol   Name                      Price        Market Cap
#1   BTC      Bitcoin                   $111,788.01  $2.21T
#2   ETH      Ethereum                  $4,601.64    $554.50B
#3   XRP      Ripple                    $3.02        $168.96B
#4   SOL      Solana                    $195.87      $92.06B
#5   DOGE     Dogecoin                  $0.22        $31.97B

🥇 TOP 10 BY MARKET CAP:
  1. BTC (Bitcoin) - $2.21T
  2. ETH (Ethereum) - $554.50B
  3. XRP (Ripple) - $168.96B
  4. SOL (Solana) - $92.06B
  5. DOGE (Dogecoin) - $31.97B
  6. ADA (Cardano) - $30.33B
  7. LINK (Chainlink) - $13.41B
  8. XLM (Stellar) - $11.45B
  9. BCH (Bitcoin Cash) - $10.91B
  10. AVAX (Avalanche) - $9.91B

📈 MARKET INSIGHTS:
  • Bitcoin Dominance: 69.6%
  • Top 10 Market Cap Share: 98.7%
  • Highest Price: BTC at $111,788.01
```

## 🚀 Performance Analysis Features

The system includes a sophisticated performance analyzer that identifies the fastest-growing cryptocurrencies among the top 10 by market cap:

**Performance Analysis:**
```bash
# Generate short-term performance report
python performance_report.py
```

**Key Metrics:**
- **Multiple Time Periods**: 1d, 3d, 7d, 14d, 30d analysis
- **Momentum Score**: Weighted combination of growth, trend strength, and volatility
- **Trend Strength**: Measures consistency of price direction (0-100%)
- **Volatility Analysis**: Daily price volatility calculations
- **Performance Ranking**: Sorted by momentum score (fastest growing first)

**Sample Performance Output:**
```
🚀 CRYPTOCURRENCY SHORT-TERM PERFORMANCE REPORT
📅 Analysis Date: 2025-08-27
📊 Cryptocurrencies Analyzed: 10
⏱️  Analysis Periods: 1d, 3d, 7d, 14d, 30d

Rank Symbol   Name                 Price        1d       3d       7d       14d      30d      Momentum
#1   SOL      Solana               $195.87      +6.14%   +0.93%   +10.61%  +2.57%   +13.53%  9.8
#2   BTC      Bitcoin              $111,788.01  +0.14%   -1.35%   -2.04%   -9.22%   -5.11%   9.3
#3   XLM      Stellar              $0.39        -2.22%   -5.33%   -4.57%   -14.44%  -7.93%   7.9

🏆 TOP 3 FASTEST GROWING (Short-term):
  1. SOL (Solana) - +3.54% avg (1-3d)
  2. BTC (Bitcoin) - -0.60% avg (1-3d)
  3. XLM (Stellar) - -3.78% avg (1-3d)

📈 PERFORMANCE INSIGHTS:
  • Best 7-day performer: SOL (+10.61%)
  • Most volatile (7d): ETH (7.2% daily volatility)
  • Positive 7-day performers: 4/10
```

## Data Structure

### Historical Data Files
Location: `crypto_data/historical/`
Format: `{ticker}_historical.csv`

Columns:
- `date`: Date (YYYY-MM-DD)
- `ticker`: Cryptocurrency ticker (e.g., "X:BTCUSD")
- `ticker_name`: Full name (e.g., "Bitcoin")
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume
- `volume_weighted_price`: Volume weighted average price
- `number_of_transactions`: Number of transactions

### Daily Snapshot Files
Location: `crypto_data/daily_snapshots/`
Format: `{YYYY-MM-DD}_snapshot.csv`

Columns:
- `date`: Snapshot date
- `rank`: Processing order
- `ticker`: Cryptocurrency ticker
- `ticker_name`: Full name
- `current_price`: Current price
- `size`: Trade size
- `exchange`: Exchange identifier
- `timestamp`: Trade timestamp
- `market_status`: Market status
- `type`: Ticker type
- `active`: Whether ticker is active
- `currency_name`: Currency name
- `base_currency_symbol`: Base currency symbol
- `base_currency_name`: Base currency name

## Configuration

Edit `config/settings.json` to customize:

```json
{
  "api": {
    "polygon_base_url": "https://api.polygon.io",
    "api_key": "YOUR_POLYGON_API_KEY",  # Your Polygon.io API key
    "rate_limit_delay": 0.2,            # Delay between API calls (seconds)
    "max_retries": 3,                   # Maximum retry attempts
    "timeout": 30                       # Request timeout (seconds)
  },
  "data": {
    "top_n_cryptos": 30,         # Number of crypto tickers to track
    "historical_days": 365       # Days of historical data to fetch
  },
  "collection": {
    "collect_historical": true,   # Enable historical data collection
    "collect_snapshots": true,    # Enable daily snapshots
    "update_existing": true       # Update existing data files
  }
}
```

## API Information

This system uses the **Polygon.io API**:
- **Rate Limit**: Varies by plan (free tier: 5 calls per minute)
- **Historical Data**: Extensive historical data available
- **API Key Required**: Free tier available with registration
- **Professional Grade**: High-quality financial data

### API Endpoints Used:
- `/v3/reference/tickers` - Available cryptocurrency tickers
- `/v3/reference/tickers/{ticker}` - Ticker details
- `/v2/last/trade/{ticker}` - Current price data
- `/v2/aggs/ticker/{ticker}/range/1/day/{from}/{to}` - Historical OHLCV data

## Data Analysis Examples

### Load Historical Data
```python
from data_utils import CryptoDataUtils

utils = CryptoDataUtils()

# Load Bitcoin historical data (using Polygon.io ticker format)
btc_data = utils.load_historical_data('X:BTCUSD')
print(btc_data.head())

# Load today's market snapshot
snapshot = utils.load_daily_snapshot()
print(snapshot.head())
```

### Portfolio Analysis
```python
# Calculate portfolio metrics for crypto tickers with weights
metrics = utils.calculate_portfolio_metrics(
    ['X:BTCUSD', 'X:ETHUSD', 'X:ADAUSD'],
    [0.4, 0.4, 0.2]  # 40% BTC, 40% ETH, 20% ADA
)
print(metrics)
```

## Logging

Logs are stored in `crypto_data/logs/` with daily rotation:
- **File**: `crypto_collector_YYYYMMDD.log`
- **Console**: Real-time output during execution
- **Levels**: INFO, WARNING, ERROR, DEBUG

## Error Handling

The system includes robust error handling:
- **API Failures**: Automatic retry with exponential backoff
- **Rate Limiting**: Built-in delays to respect API limits
- **Data Validation**: Checks for missing or invalid data
- **File Operations**: Safe file handling with backup options
- **Network Issues**: Timeout handling and connection retries

## Automation Setup

### Linux/macOS (Cron)
Add to crontab for daily collection at 9 AM:
```bash
crontab -e
# Add this line:
0 9 * * * cd /path/to/project && python scheduler.py --mode once
```

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to daily at 9:00 AM
4. Set action to start program: `python`
5. Add arguments: `scheduler.py --mode once`
6. Set start in: `/path/to/project`

## Troubleshooting

### Common Issues

**1. API Rate Limiting**
- Increase `rate_limit_delay` in config
- Reduce `top_n_cryptos` if needed

**2. Network Timeouts**
- Increase `timeout` value in config
- Check internet connection

**3. Missing Data**
- Check logs for specific errors
- Verify API endpoint availability
- Run data validation: `python data_utils.py --action summary`

**4. Disk Space**
- Monitor `crypto_data/` directory size
- Use backup/cleanup utilities regularly

### Log Analysis
```bash
# View recent logs
tail -f crypto_data/logs/crypto_collector_$(date +%Y%m%d).log

# Search for errors
grep "ERROR" crypto_data/logs/*.log

# Check API call success rate
grep "API request" crypto_data/logs/*.log | wc -l
```

## Performance

### Expected Data Volumes
- **Historical Data**: ~50KB per cryptocurrency per year
- **Daily Snapshots**: ~5KB per day
- **Total for 30 cryptos**: ~1.5MB historical + ~1.8MB/year snapshots

### Collection Times
- **Initial Setup**: 5-10 minutes (historical data for 30 cryptos)
- **Daily Updates**: 1-2 minutes (snapshots only)
- **API Calls**: ~60 calls for full collection (within rate limits)

## Contributing

To extend the system:

1. **Add New Data Sources**: Modify `crypto_collector.py`
2. **Custom Analysis**: Extend `data_utils.py`
3. **New Schedulers**: Enhance `scheduler.py`
4. **Configuration**: Update `config/settings.json`

## License

This project is open source. Use and modify as needed for your cryptocurrency analysis requirements.

## Support

For issues or questions:
1. Check the logs in `crypto_data/logs/`
2. Review the configuration in `config/settings.json`
3. Run diagnostic: `python data_utils.py --action summary`
4. Verify API connectivity manually

---

**Happy Crypto Analysis! 🚀📈**