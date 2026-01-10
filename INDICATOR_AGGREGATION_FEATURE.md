# Indicator Aggregation Feature

## Overview
The Indicator Aggregation feature provides a comprehensive daily view of all your indicator data, organized by indicator type. It calculates and displays average values for each indicator type on each day, allowing you to see overall market sentiment trends at a glance.

## Key Features

### 1. Daily Aggregation by Type
- Groups all indicators by their assigned type
- Calculates daily average for each type
- Shows overall market average across all indicators
- Displays data point counts for transparency

### 2. Time Period Selection
Quick filters for different time ranges:
- **7 Days** - Last week
- **30 Days** - Last month (default)
- **90 Days** - Last quarter
- **180 Days** - Last 6 months
- **1 Year** - Last 365 days

### 3. Type-Level Statistics
Overview cards showing for each indicator type:
- **Average**: Mean value across the entire period
- **Days**: Number of days with data
- **Min**: Lowest average value recorded
- **Max**: Highest average value recorded

### 4. Color-Coded Visualization
- Each indicator type displays with its assigned color
- Value badges color-coded:
  - 🟢 Green: Bullish (> 0.3)
  - 🔵 Blue: Slightly Bullish (0 to 0.3)
  - ⚪ Gray: Neutral (0)
  - 🟡 Yellow: Slightly Bearish (-0.3 to 0)
  - 🔴 Red: Bearish (< -0.3)

## How It Works

### Data Collection
```
1. Fetches all indicator data for the selected date range
2. Groups data by date
3. For each date:
   - Separates indicators by type
   - Calculates average per type
   - Calculates overall average
   - Counts data points
```

### Calculation Example
```
Date: 2025-10-15
Indicators:
- Technical indicators: RSI (0.7), MACD (0.5), Stochastic (0.6)
- Sentiment indicators: Fear/Greed (-0.2), Put/Call (0.1)
- On-Chain indicators: NVT (0.3), MVRV (0.4)

Results:
- Technical Average: (0.7 + 0.5 + 0.6) / 3 = 0.60
- Sentiment Average: (-0.2 + 0.1) / 2 = -0.05
- On-Chain Average: (0.3 + 0.4) / 2 = 0.35
- Overall Average: (0.7 + 0.5 + 0.6 - 0.2 + 0.1 + 0.3 + 0.4) / 7 = 0.34
```

## Usage Guide

### Accessing the Page
1. **From Navigation**: Click "Aggregation" in the top menu
2. **From Indicators Page**: Click "View Aggregation" button
3. **Direct URL**: `/indicators/aggregate`

### Reading the Data

#### Overview Cards (Top Section)
Each card represents one indicator type:
```
┌─────────────────────┐
│ 🔵 Technical        │
│                     │
│ Average    Days     │
│   0.45      28      │
│                     │
│ Min        Max      │
│  -0.12     0.87     │
└─────────────────────┘
```

**Interpretation**:
- Technical indicators averaged 0.45 (bullish) over the period
- Had data on 28 out of 30 days
- Lowest average was -0.12, highest was 0.87

#### Daily Table (Main Section)
Columns show:
1. **Date**: Calendar date
2. **Overall Avg**: Average of all indicators
3. **Points**: Total number of data points
4. **Type Columns**: Average for each indicator type

**Example Row**:
```
Date        | Overall | Points | Technical | Sentiment | On-Chain
2025-10-15  |  0.34   |   7    |   0.60    |   -0.05   |   0.35
            |         |        |  (3 pts)  |  (2 pts)  |  (2 pts)
```

### Interpreting Trends

#### Bullish Signal
```
All or most types showing positive averages (green/blue badges)
Overall average > 0.3
Consistent across multiple days
```

#### Bearish Signal
```
All or most types showing negative averages (red/yellow badges)
Overall average < -0.3
Consistent across multiple days
```

#### Mixed/Neutral Signal
```
Types showing different directions
Overall average near 0
High variance between types
```

#### Divergence Alert
```
One type significantly different from others
Example: Technical bullish (0.7) but Sentiment bearish (-0.5)
May indicate upcoming reversal or uncertainty
```

## Use Cases

### 1. Daily Market Overview
**Scenario**: Check overall market sentiment each morning

**Steps**:
1. Set to 7 days
2. Look at latest date row
3. Check overall average and type breakdowns
4. Compare to previous days for trend

**Insight**: Quick snapshot of where all your indicators stand

### 2. Trend Analysis
**Scenario**: Identify changing market conditions

**Steps**:
1. Set to 30 or 90 days
2. Scan overall average column
3. Look for color changes (red → yellow → green)
4. Note when types diverge

**Insight**: Spot trend reversals early

### 3. Type Performance Comparison
**Scenario**: See which indicator categories are most bullish/bearish

**Steps**:
1. Review overview cards at top
2. Compare average values across types
3. Identify leading and lagging types

**Insight**: Understand which aspects of market are strongest/weakest

### 4. Data Quality Check
**Scenario**: Ensure you're tracking indicators consistently

**Steps**:
1. Check "Points" column
2. Look for days with low counts
3. Review type columns for gaps (-)

**Insight**: Identify missing data and fill gaps

### 5. Divergence Detection
**Scenario**: Find conflicts between indicator types

**Steps**:
1. Look for dates where types show opposite signs
2. Example: Technical positive, Sentiment negative
3. Investigate individual indicators for context

**Insight**: Divergences may signal turning points

## Advanced Patterns

### The Bull Run Pattern
```
Day 1:  Overall  0.10  (Starting to turn)
Day 5:  Overall  0.30  (Gaining momentum)
Day 10: Overall  0.60  (Strong bull signal)
Day 15: Overall  0.80  (Extended, watch for reversal)
```

### The Distribution Pattern
```
Technical:  0.70  (High, possibly topping)
Sentiment: -0.30  (Negative, getting fearful)
On-Chain:   0.40  (Moderate)
→ Technical divergence may signal top
```

### The Accumulation Pattern
```
Technical: -0.60  (Oversold)
Sentiment: -0.80  (Extreme fear)
On-Chain:   0.20  (Starting to accumulate)
→ Bottom may be forming
```

### The Consolidation Pattern
```
All types: -0.10 to 0.10 range
Low variance for multiple days
→ Breakout likely coming
```

## Tips & Best Practices

### Data Requirements
- **Minimum**: At least 3-5 indicators with regular data
- **Optimal**: 10+ indicators across 3+ types
- **Frequency**: Daily updates for best results

### Interpretation Guidelines
1. **Don't rely on single day** - Look for multi-day patterns
2. **Weight by count** - More data points = more reliable
3. **Consider context** - External events may explain divergences
4. **Use with other tools** - Combine with charts and individual indicators

### Type Organization
- **Balance types** - Have similar number of indicators per type
- **Consistent updates** - Update all types regularly
- **Clear definitions** - Use types that make sense together

### Time Period Selection
- **Short term (7 days)**: Daily trading decisions
- **Medium term (30-90 days)**: Swing trading, trend following
- **Long term (180-365 days)**: Position trading, macro trends

## Technical Details

### Performance
- Query optimized for date ranges
- Calculates aggregations in Python (not DB) for flexibility
- Sticky table header for easy scrolling
- Responsive design for mobile viewing

### Data Flow
```
1. Query indicator_data table for date range
2. Join with indicators to get type_id
3. Group by date and type_id
4. Calculate statistics (avg, min, max, count)
5. Render with color-coded badges
```

### Null Handling
- Indicators without types are excluded from type aggregations
- Included in overall average
- Days with no data show "-" instead of 0

### Color Thresholds
```python
if value > 0.3:    # Green (strong bullish)
elif value > 0:    # Blue (bullish)
elif value == 0:   # Gray (neutral)
elif value > -0.3: # Yellow (bearish)
else:              # Red (strong bearish)
```

## API Reference

### Route
```
GET /indicators/aggregate
```

### Query Parameters
- `days` (optional): Number of days to show (default: 30)
  - Valid values: 7, 30, 90, 180, 365

### Response Data Structure
```python
{
    'aggregated_data': [
        {
            'date': date_object,
            'overall_average': float,
            'data_points_count': int,
            'type_averages': {
                type_id: {
                    'average': float,
                    'count': int,
                    'min': float,
                    'max': float
                }
            }
        }
    ],
    'type_stats': {
        type_id: {
            'avg': float,
            'min': float,
            'max': float,
            'count': int
        }
    }
}
```

## Troubleshooting

### No Data Showing
**Cause**: No indicators have data in selected period
**Solution**: 
- Add indicator data using bulk entry or individual entry
- Select a longer time period
- Check that indicators have assigned types

### Missing Type Columns
**Cause**: No indicators assigned to that type
**Solution**:
- Assign indicators to the type
- Or hide/remove unused types

### Inconsistent Counts
**Cause**: Some indicators updated more frequently than others
**Solution**:
- Use bulk entry to update all indicators on same dates
- Review individual indicators for gaps
- Set up regular update routine

### Surprising Averages
**Cause**: One or two extreme values skewing average
**Solution**:
- Check min/max values in overview cards
- Review individual indicator data
- Consider if outliers are valid or errors

## Future Enhancements

### Potential Features
- **Charts/Graphs**: Visual trend lines for each type
- **Comparison Mode**: Compare different time periods
- **Alerts**: Notify when averages cross thresholds
- **Export**: Download aggregated data as CSV
- **Custom Weighting**: Weight indicators differently in averages
- **Correlation Matrix**: Show how types correlate
- **Heatmap View**: Color-coded calendar view
- **Type Filtering**: Show/hide specific types

## Related Features

- **Indicators**: Manage individual indicators
- **Indicator Types**: Categorize indicators
- **Bulk Entry**: Update all indicators at once
- **Date Range Entry**: Fill historical data
- **Individual Data Entry**: Precise daily values

## Example Workflows

### Morning Routine
```
1. Open Aggregation page (default 30 days)
2. Check today's overall average
3. Review type breakdowns
4. Compare to yesterday and last week
5. Note any divergences
6. Make trading decisions
```

### Weekly Analysis
```
1. Set to 7 days
2. Export data (if available)
3. Compare each type's trend
4. Identify strongest/weakest types
5. Adjust positions accordingly
```

### Monthly Review
```
1. Set to 30 or 90 days
2. Review overview cards
3. Look for sustained trends
4. Check for regime changes
5. Plan next month's strategy
```

## Summary

The Indicator Aggregation feature transforms your individual indicator data into actionable market insights by:

✅ Aggregating by type for clearer signal
✅ Showing daily trends over time
✅ Highlighting divergences between types
✅ Providing quick visual feedback
✅ Supporting multiple time horizons
✅ Maintaining data transparency (counts shown)

Use this page as your **dashboard** to get a quick read on overall market conditions based on all your tracked indicators!
