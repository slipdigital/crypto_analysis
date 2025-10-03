# Flask Crypto Dashboard

A comprehensive web dashboard for cryptocurrency analysis built with Flask, integrating with your existing crypto data collection system.

## Features

### 🏠 Dashboard Overview
- **Market Summary Cards**: Total market cap, cryptocurrency count, Bitcoin dominance, and top 10 share
- **Top Performers Table**: Real-time performance rankings with 7-day changes
- **Market Overview Chart**: Visual representation of market distribution
- **Market Cap Preview**: Quick view of top 10 cryptocurrencies by market cap

### 📊 Market Cap Rankings
- **Sortable Table**: Complete market cap rankings with DataTables integration
- **Search & Filter**: Find specific cryptocurrencies quickly
- **Export Functionality**: Download data as CSV
- **Real-time Updates**: Auto-refresh every 5 minutes
- **Market Insights**: Bitcoin dominance, market statistics, and key metrics

### 📈 Interactive Charts
- **Multiple Chart Types**: Line charts, candlestick charts, and volume charts
- **Time Period Selection**: 7 days, 30 days, 90 days, and 1 year views
- **Price Information Cards**: Current price, price change, period high/low
- **Comparison Tool**: Compare multiple cryptocurrencies side-by-side
- **Download Charts**: Export charts as PNG images

### 🚀 Performance Analysis
- **Momentum Scoring**: Advanced algorithm combining growth, trend strength, and volatility
- **Multi-timeframe Analysis**: 1d, 3d, 7d, 14d, and 30d performance metrics
- **Performance Rankings**: Sort by different time periods
- **Volatility Analysis**: Track price volatility across timeframes
- **Visual Charts**: Momentum distribution and performance comparison charts

## Installation

### Prerequisites
- Python 3.8 or higher
- Existing crypto data collection system (from this repository)
- Web browser with JavaScript enabled

### Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Data Availability**
   Ensure you have collected crypto data by running:
   ```bash
   python crypto_collector.py
   ```

3. **Configure Flask Settings** (Optional)
   Edit `config/settings.json` to customize Flask configuration:
   ```json
   {
     "flask": {
       "secret_key": "your-secret-key-here",
       "debug": false,
       "host": "0.0.0.0",
       "port": 5000
     }
   }
   ```

4. **Run the Dashboard**
   ```bash
   python app.py
   ```

5. **Access the Dashboard**
   Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage Guide

### Navigation
- **Dashboard**: Overview of market summary and top performers
- **Market Cap**: Complete rankings table with search and export
- **Charts**: Interactive price charts with comparison tools
- **Performance**: Advanced performance analysis with momentum scoring

### Key Features

#### Market Cap Rankings
- Click column headers to sort data
- Use the search box to find specific cryptocurrencies
- Click "Export CSV" to download current data
- Data refreshes automatically every 5 minutes

#### Interactive Charts
1. Select a cryptocurrency from the dropdown
2. Choose time period (7d, 30d, 90d, 1y)
3. Select chart type (Line, Candlestick, Volume)
4. Click "Load Chart" to display
5. Use comparison tool to analyze multiple cryptocurrencies

#### Performance Analysis
- View momentum scores and performance rankings
- Filter by different time periods using the radio buttons
- Export performance data as CSV
- Analyze volatility and trend strength metrics

### Data Refresh
- **Automatic**: Data refreshes every 5 minutes
- **Manual**: Click refresh buttons or press Ctrl+R
- **Status**: Last update time shown in navigation bar

## API Endpoints

The dashboard provides RESTful API endpoints for programmatic access:

### Market Data
- `GET /api/market-cap` - Market cap rankings data
- `GET /api/performance` - Performance analysis data
- `GET /api/summary` - Dashboard summary data

### Chart Data
- `GET /api/historical/{symbol}?period={period}` - Historical price data
- `GET /api/chart-data/{symbol}?type={type}&period={period}` - Formatted chart data

### Example API Usage
```bash
# Get market cap data
curl http://localhost:5000/api/market-cap

# Get Bitcoin historical data for 30 days
curl http://localhost:5000/api/historical/BTC?period=30d

# Get performance analysis
curl http://localhost:5000/api/performance
```

## Architecture

### Backend Structure
```
├── app.py                 # Main Flask application
├── services/              # Business logic layer
│   ├── data_service.py    # Data integration service
│   ├── chart_service.py   # Chart data preparation
│   └── market_service.py  # Market analysis service
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Dashboard page
│   ├── market_cap.html   # Market cap page
│   ├── charts.html       # Charts page
│   └── performance.html  # Performance page
└── static/               # Static assets
    ├── css/dashboard.css # Custom styling
    └── js/dashboard.js   # JavaScript functionality
```

### Data Integration
The dashboard integrates with your existing crypto data system:
- **Market Cap Data**: Uses `market_cap_report.py` for market cap calculations
- **Performance Data**: Leverages `performance_report.py` for analysis
- **Historical Data**: Accesses CSV files in `crypto_data/historical/`
- **Snapshots**: Uses daily snapshots from `crypto_data/daily_snapshots/`

### Frontend Technologies
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Interactive charts and visualizations
- **DataTables**: Advanced table functionality
- **Font Awesome**: Icons and visual elements
- **jQuery**: DOM manipulation and AJAX requests

## Configuration

### Flask Settings
Edit `config/settings.json`:
```json
{
  "flask": {
    "secret_key": "change-this-in-production",
    "debug": false,
    "host": "0.0.0.0",
    "port": 5000
  }
}
```

### Data Refresh Intervals
Modify `static/js/dashboard.js`:
```javascript
const REFRESH_INTERVAL = 300000; // 5 minutes in milliseconds
```

### Chart Configuration
Customize chart appearance in chart service files or template JavaScript sections.

## Troubleshooting

### Common Issues

1. **No Data Available**
   - Ensure you've run `python crypto_collector.py` to collect data
   - Check that CSV files exist in `crypto_data/` directories
   - Verify API key configuration in `config/settings.json`

2. **Charts Not Loading**
   - Check browser console for JavaScript errors
   - Ensure Chart.js CDN is accessible
   - Verify historical data exists for selected cryptocurrency

3. **Performance Issues**
   - Reduce auto-refresh interval
   - Limit number of cryptocurrencies in comparison charts
   - Check server resources and data file sizes

4. **API Errors**
   - Check Flask application logs
   - Verify data service configuration
   - Ensure all required Python packages are installed

### Debug Mode
Enable debug mode for development:
```bash
export FLASK_DEBUG=1
python app.py
```

### Logs
Check application logs for detailed error information:
- Flask logs appear in console when running in debug mode
- Data collection logs in `crypto_data/logs/`

## Security Considerations

### Production Deployment
1. **Change Secret Key**: Use a secure, random secret key
2. **Disable Debug Mode**: Set `debug: false` in configuration
3. **Use HTTPS**: Deploy behind a reverse proxy with SSL
4. **Restrict Access**: Consider authentication for sensitive data
5. **Update Dependencies**: Keep all packages up to date

### Data Privacy
- Dashboard displays market data only (no personal information)
- API endpoints are read-only
- No user data collection or tracking

## Performance Optimization

### Caching
Consider implementing caching for:
- Market cap calculations
- Performance analysis results
- Chart data preparation

### Database Integration
For larger datasets, consider migrating from CSV to:
- SQLite for local deployment
- PostgreSQL for production deployment
- Redis for caching layer

## Contributing

### Development Setup
1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Make changes and test thoroughly
5. Submit pull request with detailed description

### Code Style
- Follow PEP 8 for Python code
- Use consistent JavaScript formatting
- Comment complex logic and algorithms
- Write descriptive commit messages

## License

This project is part of the cryptocurrency analysis system. Use and modify as needed for your analysis requirements.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs for error details
3. Verify data collection is working properly
4. Test with a fresh data collection run

---

**Happy Crypto Analysis! 🚀📈**

Built with ❤️ using Flask, Bootstrap, and Chart.js