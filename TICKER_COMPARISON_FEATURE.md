# Ticker Comparison - Relative Strength Feature

## Overview
The Ticker Comparison feature allows you to compare the relative performance of two cryptocurrencies over time using multiple chart visualizations. This tool helps identify which asset is outperforming and by how much, making it invaluable for pair trading, asset rotation, and investment decisions.

## Key Features

### 1. Dual Ticker Selection
- Select any two tickers from dropdowns
- Ticker 1 (Numerator): The asset you're testing
- Ticker 2 (Denominator): The benchmark or comparison asset
- Common comparisons: BTC vs ETH, ALT vs BTC, TOKEN vs USD

### 2. Multiple Time Periods
Choose from predefined periods:
- **30 Days**: Short-term momentum
- **60 Days**: Medium-term trends
- **90 Days**: Quarterly performance (default)
- **180 Days**: Half-year trends
- **1 Year**: Long-term comparison

### 3. Four Chart Views

#### A. Indexed Performance Chart
- Normalizes both tickers to 100 at start
- Shows percentage gains/losses visually
- Makes comparison easy regardless of price differences
- **Blue line**: Ticker 1 performance
- **Red line**: Ticker 2 performance

#### B. Relative Strength Ratio Chart
- Shows Ticker1 / Ticker2 ratio over time
- Normalized to 100 at start
- **Rising = Ticker 1 outperforming**
- **Falling = Ticker 2 outperforming**
- Most important chart for relative strength analysis

#### C. Individual Price Charts
- Raw price data for each ticker
- Useful for context and absolute price levels
- Shows actual dollar values

### 4. Statistics Dashboard
Four key metrics displayed at top:

**Ticker 1 Change**: Total percentage change over period
**Ticker 2 Change**: Total percentage change over period
**Relative Strength Change**: How much RS ratio has changed
**Winner**: Which ticker outperformed (green highlight)

## How Relative Strength Works

### The Formula
```
Relative Strength = Price of Ticker 1 / Price of Ticker 2
```

### Interpretation

**When RS is Rising:**
- Ticker 1 is outperforming Ticker 2
- Either Ticker 1 is gaining more, OR
- Ticker 1 is losing less

**When RS is Falling:**
- Ticker 2 is outperforming Ticker 1
- Either Ticker 2 is gaining more, OR
- Ticker 2 is losing less

### Example Calculation
```
Day 1: BTC = $40,000, ETH = $2,000
RS = 40,000 / 2,000 = 20.0

Day 30: BTC = $44,000 (+10%), ETH = $2,100 (+5%)
RS = 44,000 / 2,100 = 20.95

RS Change: (20.95 / 20.0 - 1) × 100 = +4.75%
→ BTC outperformed ETH by 4.75%
```

## Use Cases

### 1. Altcoin vs Bitcoin Comparison
**Purpose**: Determine if altcoin is in uptrend vs BTC

**Setup**:
- Ticker 1: Your altcoin (e.g., ETH, SOL, ADA)
- Ticker 2: BTC
- Period: 90-180 days

**What to Look For**:
- Rising RS = Altcoin season for that coin
- Falling RS = Bitcoin dominance increasing
- Flat RS = Moving together (beta = 1)

### 2. Sector Rotation
**Purpose**: Compare two altcoins to find leader

**Setup**:
- Ticker 1: Newer/smaller cap coin
- Ticker 2: Established competitor
- Period: 30-60 days

**What to Look For**:
- Rising RS = Money rotating into Ticker 1
- Falling RS = Ticker 2 maintaining leadership
- Crossovers = Potential momentum shifts

### 3. Benchmark Comparison
**Purpose**: Is your investment beating the market?

**Setup**:
- Ticker 1: Your holding
- Ticker 2: Market benchmark (BTC or ETH)
- Period: Your holding period

**What to Look For**:
- RS > 100 = You're beating the benchmark
- RS < 100 = Underperforming
- Trend matters more than absolute value

### 4. Pair Trading Setup
**Purpose**: Find divergences for mean reversion trades

**Setup**:
- Ticker 1: First asset in pair
- Ticker 2: Second asset in pair
- Period: 30-90 days

**What to Look For**:
- RS at extremes = Potential mean reversion
- Breaking out of range = New trend starting
- Tight correlation = Good pair for trading

### 5. Layer 1 Comparison
**Purpose**: Which L1 blockchain is gaining market share?

**Setup**:
- Ticker 1: Newer L1 (SOL, AVAX, etc.)
- Ticker 2: ETH
- Period: 180-365 days

**What to Look For**:
- Sustained RS rise = Gaining adoption
- RS fall = ETH maintaining dominance
- Volatility in RS = Unstable relative value

## Reading the Charts

### Indexed Performance Chart

**Both Lines Rising:**
- Both assets are in uptrend
- Compare which is steeper for winner
- Gap widening = divergence

**Both Lines Falling:**
- Both assets are in downtrend
- Higher line is losing less (relative winner)
- Gap narrowing = convergence

**Lines Diverging:**
- Outperformance is accelerating
- One asset much stronger
- Consider rotation

**Lines Converging:**
- Performance gap closing
- Mean reversion may be occurring
- Previous leader weakening

### Relative Strength Chart

**Uptrend (Rising):**
- Clear bullish RS for Ticker 1
- Consider overweight Ticker 1
- Look for pullbacks to enter

**Downtrend (Falling):**
- Clear bullish RS for Ticker 2
- Consider overweight Ticker 2
- Ticker 1 is underperforming

**Sideways (Flat):**
- No clear relative advantage
- Both moving similarly
- Wait for breakout

**Breakout (Sharp Move):**
- New trend beginning
- Confirm with volume/fundamentals
- May present trading opportunity

## Trading Strategies

### Momentum Following
```
1. Identify RS uptrend (rising for 30+ days)
2. Enter Ticker 1, exit Ticker 2
3. Hold while RS continues rising
4. Exit when RS starts falling
```

### Mean Reversion
```
1. Identify historically correlated pair
2. Wait for RS to reach extreme
3. Short overperformer, long underperformer
4. Exit when RS returns to mean
```

### Rotation Strategy
```
1. Compare multiple assets to BTC
2. Rank by RS strength
3. Rotate into top performers
4. Rebalance monthly
```

### Divergence Trading
```
1. Find pair that usually moves together
2. Wait for major RS divergence
3. Bet on convergence
4. Set tight stops
```

## Best Practices

### Selecting Tickers

**Good Comparisons:**
- Same sector (Layer 1 vs Layer 1)
- Similar market cap range
- Correlated historically
- Liquid markets

**Poor Comparisons:**
- Vastly different market caps
- Different sectors
- Low correlation
- Illiquid markets

### Time Period Selection

**Short-term (30 days):**
- Day trading / swing trading
- Quick momentum plays
- More noise, less signal

**Medium-term (90-180 days):**
- Position trading
- Trend following
- Good signal-to-noise ratio

**Long-term (1 year):**
- Investment decisions
- Strategic allocation
- Macro trends

### Interpretation Tips

1. **Don't trade on single day moves** - Look for sustained trends
2. **Consider both absolute and relative** - Both charts matter
3. **Volume context** - Low volume RS changes are suspect
4. **Fundamental backdrop** - News can drive RS changes
5. **Multiple timeframes** - Check different periods for confirmation

## Example Scenarios

### Scenario 1: Strong Relative Outperformance
```
Setup: ETH vs BTC, 90 days
Results:
- ETH: +25%
- BTC: +10%
- RS Change: +13.6%

Interpretation:
- ETH strongly outperforming
- RS in clear uptrend
- Action: Consider overweight ETH
```

### Scenario 2: Both Down, Relative Winner
```
Setup: MATIC vs SOL, 60 days
Results:
- MATIC: -15%
- SOL: -30%
- RS Change: +17.6%

Interpretation:
- Both in downtrend
- MATIC losing less (relative winner)
- Action: If must hold one, choose MATIC
```

### Scenario 3: Divergence Alert
```
Setup: DOT vs ADA, 180 days
Results:
- DOT: +40%
- ADA: +5%
- RS Change: +33.3%

Interpretation:
- Massive divergence
- DOT way outperforming
- Action: Either ride momentum OR bet on mean reversion
```

### Scenario 4: No Relative Edge
```
Setup: BNB vs BTC, 90 days
Results:
- BNB: +18%
- BTC: +17%
- RS Change: +0.9%

Interpretation:
- Moving together
- No relative advantage
- Action: Choose based on other factors
```

## Technical Details

### Data Requirements
- Both tickers must have overlapping date ranges
- Missing dates are excluded from both datasets
- Minimum 20 common dates recommended
- Uses closing prices only

### Calculations

**Indexed Performance:**
```python
indexed_value = (current_price / start_price) × 100
```

**Relative Strength Ratio:**
```python
rs_ratio = price_ticker1 / price_ticker2
```

**Normalized RS:**
```python
rs_normalized = (current_rs / start_rs) × 100
```

**Percentage Changes:**
```python
change = ((end_value / start_value) - 1) × 100
```

### Chart Colors
- **Blue**: Ticker 1 / Numerator
- **Red**: Ticker 2 / Denominator
- **Teal**: Relative Strength Ratio
- **Green**: Positive changes
- **Red**: Negative changes

## API Reference

### Route
```
GET /charts/compare
```

### Query Parameters
- `ticker1` (required): Symbol for first ticker
- `ticker2` (required): Symbol for second ticker
- `days` (optional): Number of days to compare (default: 90)
  - Valid values: 30, 60, 90, 180, 365

### Example URLs
```
/charts/compare?ticker1=X:ETHUSD&ticker2=X:BTCUSD&days=90
/charts/compare?ticker1=X:SOLUSD&ticker2=X:ETHUSD&days=180
/charts/compare?ticker1=X:MATICUSD&ticker2=X:AVAXUSD&days=60
```

## Troubleshooting

### "No data available"
**Cause**: Tickers don't have overlapping date ranges
**Solution**: 
- Choose tickers with similar data history
- Select shorter time period
- Check individual ticker charts first

### Charts look wrong
**Cause**: Very different price scales
**Solution**:
- Look at indexed chart instead of raw prices
- Use RS ratio chart for comparison
- Both tickers are normalized for easy comparison

### RS seems inverted
**Cause**: Tickers in wrong order
**Solution**:
- Swap ticker1 and ticker2
- RS = ticker1 / ticker2, so order matters
- Remember: numerator vs denominator

### Sudden RS spikes
**Cause**: Data quality issues or real events
**Solution**:
- Check for missing data
- Verify prices on external sources
- Look for news/events on that date

## Future Enhancements

### Potential Features
- **Correlation coefficient**: Statistical correlation measure
- **Beta calculation**: Volatility relationship
- **Spread trading**: Show entry/exit signals
- **Multiple comparisons**: Compare 3+ tickers at once
- **RS ranking**: Automatically rank all tickers
- **Alerts**: Notify when RS crosses thresholds
- **Export**: Download comparison data
- **Annotations**: Mark important events on charts

## Related Features

- **Individual Ticker Charts**: View single ticker history
- **Top Gainers/Losers**: See best/worst performers
- **Market Data**: Current prices and market caps

## Quick Reference Card

### Setup Checklist
- [ ] Select Ticker 1 (what you're testing)
- [ ] Select Ticker 2 (your benchmark)
- [ ] Choose time period
- [ ] Click "Compare"

### Reading RS Chart
- **Rising** = Ticker 1 winning
- **Falling** = Ticker 2 winning
- **Flat** = Moving together
- **Breakout** = Trend change

### Common Pairs
- ALT vs BTC (altcoin strength)
- ETH vs BTC (layer 1 dominance)
- SOL vs ETH (new vs established L1)
- Your coin vs Sector leader

### Decision Matrix
| RS Trend | Action |
|----------|--------|
| Rising | Buy Ticker 1, Sell Ticker 2 |
| Falling | Buy Ticker 2, Sell Ticker 1 |
| Peak | Consider mean reversion |
| Trough | Consider mean reversion |
| Breakout | Follow new trend |

## Summary

The Ticker Comparison tool provides professional-grade relative strength analysis with:

✅ **Visual clarity** - Multiple chart views
✅ **Easy comparison** - Normalized to 100
✅ **Statistical rigor** - Proper RS calculations
✅ **Flexible timeframes** - 30 days to 1 year
✅ **Quick insights** - Statistics at a glance
✅ **Actionable data** - Clear winner identification

Use this tool to make smarter decisions about which assets to hold, when to rotate, and how your investments compare to benchmarks!
