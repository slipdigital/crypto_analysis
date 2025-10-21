# Bulk Indicator Entry Feature

## Overview
The Bulk Indicator Entry feature allows you to update values for multiple indicators at once, all sharing the same date. This is perfect for daily indicator updates or batch data entry.

## How to Use

### Access the Feature
1. Navigate to **Indicators** page
2. Click the **"Bulk Entry"** button (green button in the header)
3. Or use the main navigation menu: **Bulk Entry**

### Enter Data
1. **Select Date**: Choose the date for all data points (defaults to today)
2. **Enter Values**: Type or use the slider for each indicator (-1.0 to 1.0)
3. **Visual Feedback**: 
   - Cards turn green when you enter a value
   - Real-time preview shows value position on gradient
   - Badge displays current value with color coding
4. **Save**: Click "Save All Values" to commit changes

### Quick Fill Options
Use the quick fill buttons to set all indicators to the same value:
- **-1.0 Bearish**: Set all to extremely bearish
- **-0.5**: Set all to moderately bearish
- **0.0 Neutral**: Set all to neutral
- **0.5**: Set all to moderately bullish
- **1.0 Bullish**: Set all to extremely bullish
- **Clear All**: Remove all entered values

### Smart Features

#### Skip Indicators
- Leave fields empty for indicators you don't want to update
- Only indicators with values will be saved

#### Update Existing Data
- If data exists for the selected date, it will be updated
- No duplicate entries are created

#### Live Counts
- **Filled**: Number of indicators with values entered
- **Empty**: Number of indicators still empty
- Updates in real-time as you enter data

#### Keyboard Shortcuts
- **Ctrl+S**: Save all values
- **Ctrl+0**: Fill all with 0 (neutral)

## Features

### Visual Indicators
- **Color-coded badges**: 
  - Red: -1.0 to -0.5 (bearish)
  - Orange: -0.5 to 0 (slightly bearish)
  - Gray: 0 (neutral)
  - Blue: 0 to 0.5 (slightly bullish)
  - Green: 0.5 to 1.0 (bullish)
- **Gradient bars**: Show value position visually
- **Card highlighting**: Green border when value entered

### Sticky Header
- Date selector stays visible while scrolling
- Quick fill buttons always accessible
- Save button always within reach

### Validation
- **Value Range**: Automatically clamped to -1.0 to 1.0
- **Date Validation**: Cannot select future dates
- **Real-time Feedback**: Invalid values corrected immediately

## Use Cases

### Daily Updates
Perfect for updating all your indicators at the end of each trading day:
1. Select today's date
2. Review each indicator
3. Enter your assessment
4. Save all at once

### Historical Data Entry
Backfill indicator data for specific dates:
1. Select any past date
2. Enter values based on historical analysis
3. Save and move to next date

### Batch Analysis
Quick sentiment analysis across all indicators:
1. Use quick fill buttons for initial values
2. Adjust individual indicators as needed
3. Save the snapshot

## Example Workflow

### End-of-Day Update
```
1. Open Bulk Entry page (defaults to today)
2. Review market conditions
3. For each indicator:
   - RSI Overbought: -0.8 (very overbought, bearish)
   - MACD Crossover: 0.6 (bullish crossover)
   - Volume Trend: 0.3 (slightly bullish)
   - Fear & Greed: -0.4 (fearful)
4. Save all values
5. Data is recorded for today across all 4 indicators
```

### Weekly Review
```
1. Select last Friday's date
2. Use "0.0 Neutral" quick fill as baseline
3. Adjust only indicators that were significant
4. Save to record the weekly snapshot
```

## Success Messages

After saving, you'll see a summary:
```
Bulk entry for 2025-10-15: 
- 8 new data point(s) added
- 3 data point(s) updated  
- 2 indicator(s) skipped (no value provided)
```

## Error Handling

### Validation Errors
Individual indicators with errors are shown:
```
⚠ RSI Indicator: Value must be between -1.0 and 1.0
⚠ Volume Trend: Invalid value "abc"
```

### Partial Success
- Valid entries are saved even if some fail
- Error messages show which indicators had issues
- You can fix and resubmit

## Tips

1. **Start with Quick Fill**: Set a baseline, then adjust individual indicators
2. **Use Sliders**: Faster than typing for approximate values
3. **Visual Feedback**: Watch the gradient bars to ensure values are in the right range
4. **Skip Confidently**: It's okay to leave indicators empty
5. **Daily Routine**: Make it part of your end-of-day analysis
6. **Batch Updates**: Group similar indicators together for faster entry

## Route Information

- **URL**: `/indicators/bulk-entry`
- **Methods**: GET (display form), POST (save data)
- **Access**: Available from Indicators page and main menu

## Database Impact

- Creates new `indicator_data` records for new date/indicator combinations
- Updates existing records if date/indicator combination exists
- All operations in a single transaction (all or nothing)
- Timestamps automatically updated

## Related Features

- **Individual Entry**: Add/edit single data points per indicator
- **Data List View**: See all data points for one indicator
- **Statistics**: View aggregated metrics per indicator

## Future Enhancements

Potential improvements:
- Copy from previous date
- Import from CSV
- Chart preview showing trend
- Compare to previous entries
- Template presets for common patterns
- Bulk delete for a date range
