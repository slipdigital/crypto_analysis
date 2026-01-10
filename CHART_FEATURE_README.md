# Stock Chart View - Feature Documentation

## Overview

Added a professional stock-style chart view for each cryptocurrency ticker with interactive candlestick, line, and volume charts.

## Features

### 📊 Chart Types

1. **Candlestick Chart** (Default)
   - Shows OHLC (Open, High, Low, Close) data
   - Green candles = price increased
   - Red candles = price decreased
   - Ideal for technical analysis

2. **Line Chart**
   - Simple closing price line
   - Shaded area underneath
   - Good for trend overview

3. **Volume Chart**
   - Bar chart showing trading volume
   - Color-coded by price direction
   - Always visible below price chart

### ⏰ Time Ranges

Quick selection buttons:
- **7D** - Last 7 days
- **30D** - Last 30 days (1 month)
- **90D** - Last 90 days (3 months) - Default
- **180D** - Last 180 days (6 months)
- **1Y** - Last 365 days (1 year)
- **2Y** - Last 730 days (2 years)

### 📈 Statistics Cards

Real-time calculated statistics:
- **Current Price** - Most recent closing price
- **Period High** - Highest price in selected range
- **Period Low** - Lowest price in selected range
- **Change** - Percentage change from start to end of period
- **Average Volume** - Mean trading volume
- **Date Range** - Actual dates shown in chart

### 🎨 Interactive Features

- **Hover tooltips** - Detailed price info on hover
- **Responsive design** - Works on all screen sizes
- **Smooth animations** - Professional chart transitions
- **Color coding**:
  - Green = positive/bullish
  - Red = negative/bearish
  - Blue = neutral/info

## How to Access

### From Ticker List
1. Navigate to home page: http://localhost:5000/
2. Find any ticker with data
3. Click the **green chart icon** (<i class="bi bi-graph-up"></i>) in the Actions column

### From Ticker Detail Page
1. Go to any ticker detail page
2. Click the **"View Chart"** button at the top

### Direct URL
```
http://localhost:5000/ticker/{TICKER_SYMBOL}/chart
```

Example:
```
http://localhost:5000/ticker/X:BTCUSD/chart
http://localhost:5000/ticker/X:ETHUSD/chart?days=180
```

## Technical Implementation

### Backend (`app.py`)

New route added:
```python
@app.route('/ticker/<ticker_symbol>/chart')
def ticker_chart(ticker_symbol):
    # Fetches ticker metadata and historical OHLCV data
    # Supports ?days=X query parameter
    # Returns data availability info
```

### Frontend (`ticker_chart.html`)

**Dependencies:**
- Chart.js 4.4.0 - Main charting library
- chartjs-chart-financial 0.1.1 - Candlestick chart support
- Bootstrap 5 - UI framework
- Bootstrap Icons - Icons

**Key JavaScript Functions:**
- `createCandlestickChart()` - Renders candlestick view
- `createLineChart()` - Renders line chart view
- `createVolumeChart()` - Renders volume bars
- `calculateStats()` - Computes statistics
- `showChart(type)` - Switches between chart types
- `formatPrice()` - Formats prices with proper decimals
- `formatVolume()` - Formats volume (K, M, B)

## Usage Examples

### View Bitcoin Chart (Last 90 Days)
```
http://localhost:5000/ticker/X:BTCUSD/chart
```

### View Ethereum Chart (Last Year)
```
http://localhost:5000/ticker/X:ETHUSD/chart?days=365
```

### View Cardano Chart (Last Week)
```
http://localhost:5000/ticker/X:ADAUSD/chart?days=7
```

## UI Components

### Navigation Buttons
- **Back to All Tickers** - Returns to main list
- **Ticker Details** - Goes to detail page
- Time range buttons (7D, 30D, 90D, 180D, 1Y, 2Y)
- Chart type buttons (Candlestick, Line, Volume)

### Charts
1. **Main Price Chart** - 500px height
2. **Volume Chart** - 200px height (always shown)

### Statistics Section
- 4 stat cards showing key metrics
- 3 additional info cards (avg volume, date range, market cap)

### Data Availability Card
Shows full data range available for the ticker

## Styling

**Custom CSS:**
- `.chart-container` - Responsive chart wrapper
- `.stats-card` - Colored left border on stat cards
- `.positive` - Green text for gains
- `.negative` - Red text for losses
- `.time-range-btn` - Compact button spacing

**Color Scheme:**
- Primary: Blue (#0d6efd)
- Success/Bullish: Green (#198754)
- Danger/Bearish: Red (#dc3545)
- Warning: Yellow (#ffc107)

## Data Requirements

The chart requires:
- Ticker exists in `tickers` table
- Historical data exists in `ticker_data` table
- Minimum fields: date, open, high, low, close, volume

**If no data exists:**
- Shows warning message
- Displays data availability info (if any)
- No charts rendered

## Performance Considerations

- Efficient queries with date filtering
- Data sorted in Python (not DB) for chart.js
- Canvas rendering (hardware accelerated)
- Lazy loading of chart libraries
- Only loads data for requested time range

## Future Enhancements

Potential additions:
- Technical indicators (MA, RSI, MACD, Bollinger Bands)
- Comparison with other tickers
- Export chart as image
- Custom date range picker
- Intraday data (if available)
- Drawing tools
- Multiple timeframes on one view
- Save favorite chart configurations

## Troubleshooting

**Chart not showing:**
- Check browser console for JavaScript errors
- Verify ticker has data in `ticker_data` table
- Ensure Chart.js CDN is accessible

**Data points missing:**
- Some days may have no trading data
- Check `update_ticker_data.py` collection status
- Verify date range has historical data

**Performance issues:**
- Use shorter time ranges (7D, 30D)
- Reduce number of data points
- Close other browser tabs

## Integration Points

**Related Files:**
- `flask_app/app.py` - Route handler
- `flask_app/templates/ticker_chart.html` - Chart page
- `flask_app/templates/ticker_detail.html` - Link to chart
- `flask_app/templates/tickers.html` - Chart icon in table
- `models.py` - TickerData model

**Database Tables:**
- `tickers` - Ticker metadata
- `ticker_data` - Historical OHLCV data

## API Examples

### Get Chart Page
```http
GET /ticker/X:BTCUSD/chart HTTP/1.1
Host: localhost:5000
```

### Get Chart with Time Range
```http
GET /ticker/X:BTCUSD/chart?days=30 HTTP/1.1
Host: localhost:5000
```

## Testing Checklist

- [ ] Chart loads for ticker with data
- [ ] All time ranges work (7D, 30D, 90D, 180D, 1Y, 2Y)
- [ ] Can switch between chart types (Candlestick, Line, Volume)
- [ ] Statistics calculate correctly
- [ ] Hover tooltips show proper data
- [ ] Volume chart colors match price direction
- [ ] Responsive on mobile devices
- [ ] Warning shows for tickers without data
- [ ] Navigation buttons work correctly
- [ ] URL parameters persist on reload

---

**The chart view is now live at:** http://localhost:5000/ticker/{TICKER}/chart
