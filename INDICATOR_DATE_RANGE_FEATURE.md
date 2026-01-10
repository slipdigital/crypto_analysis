# Indicator Data Date Range Entry Feature

## Overview
The Date Range Entry feature allows you to add indicator data values across multiple dates at once with a single value. This is perfect for filling in historical data, setting baseline values, or quickly updating periods where the indicator remained constant.

## Features

### 1. Date Range Selection
- **Start Date**: Choose the beginning date of the range
- **End Date**: Choose the ending date of the range
- **Date Validation**: End date must be after start date
- **Max Date**: Cannot select future dates

### 2. Value Configuration
- **Single Value**: One value applied to all dates in range
- **Range**: -1.0 to 1.0 (validated)
- **Visual Feedback**: 
  - Real-time progress bar showing value position
  - Color-coded bar (red for negative, green for positive, gray for neutral)
  - Quick action buttons for common values

### 3. Smart Options
- **Skip Weekends**: Automatically exclude Saturdays and Sundays (markets closed)
- **Overwrite Existing**: Choose whether to update existing data or skip those dates
- **Date Counter**: See how many dates will be processed before submitting

### 4. Summary Preview
- Shows total number of dates to process
- Displays date range and value to be applied
- Updates dynamically as you change options

## Usage

### Accessing Date Range Entry

1. **From Indicator Data Page**:
   - Go to **Indicators** → Select an indicator → Click **View Data**
   - Click the green **Date Range Entry** button at the top

2. **Direct URL**: 
   - `/indicators/<indicator_id>/data/range-entry`

### Filling a Date Range

#### Example 1: Setting Neutral Value for Historical Period
**Scenario**: You want to set RSI indicator to neutral (0.0) for January 2024

1. Click **Date Range Entry** button
2. Set **Start Date**: `2024-01-01`
3. Set **End Date**: `2024-01-31`
4. Enter **Value**: `0.0` (or click "Set to 0.0" button)
5. Keep **Skip weekends** checked
6. Leave **Overwrite existing** unchecked
7. Review summary: "Will process 23 date(s)..."
8. Click **Apply to Date Range**

Result: 23 weekdays in January 2024 now have value 0.0

#### Example 2: Marking Bullish Period
**Scenario**: Market was strongly bullish in March, set indicator to 0.8

1. Set **Start Date**: `2024-03-01`
2. Set **End Date**: `2024-03-31`
3. Click **Set to 1.0** then adjust to `0.8`
4. Keep **Skip weekends** checked
5. Check **Overwrite existing** (to update any existing data)
6. Click **Apply to Date Range**

Result: All weekdays in March have value 0.8, previous data overwritten

#### Example 3: Including Weekends
**Scenario**: 24/7 crypto indicator needs all days

1. Set date range
2. Enter value
3. **Uncheck** "Skip weekends"
4. Click **Apply to Date Range**

Result: All 7 days per week included

## Quick Action Buttons

Located in the sidebar for fast value entry:

| Button | Value | Use Case |
|--------|-------|----------|
| Set to -1.0 (Minimum) | -1.0 | Extreme bearish signal |
| Set to -0.5 | -0.5 | Moderate bearish |
| Set to 0.0 (Neutral) | 0.0 | Neutral / no signal |
| Set to 0.5 | 0.5 | Moderate bullish |
| Set to 1.0 (Maximum) | 1.0 | Extreme bullish signal |

## Options Explained

### Skip Weekends
- **Checked (default)**: Only Monday-Friday included
- **Unchecked**: All 7 days included
- **Recommended**: Keep checked for stock/traditional markets
- **When to uncheck**: 24/7 markets (crypto), or specific analysis needs

### Overwrite Existing Data
- **Unchecked (default)**: Existing dates are skipped, only adds to empty dates
- **Checked**: Updates all dates including those with existing data
- **Use case for checked**: Correcting historical data, baseline reset
- **Use case for unchecked**: Filling gaps without losing existing entries

## Results Summary

After submission, you'll see a detailed summary:

```
Date range entry completed: 18 new data point(s) added, 5 existing data point(s) skipped
```

Or with overwrite enabled:
```
Date range entry completed: 15 new data point(s) added, 8 data point(s) updated
```

## API Route

### Endpoint
```
GET/POST /indicators/<indicator_id>/data/range-entry
```

### POST Parameters
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `value` (required): Float between -1.0 and 1.0
- `skip_weekends` (optional): Checkbox, "on" to skip weekends
- `overwrite_existing` (optional): Checkbox, "on" to overwrite

### Response
- Success: Redirects to indicator data list with success message
- Error: Returns to form with error message

## Technical Details

### Date Processing
```python
# Generates date list
current_date = start_date
while current_date <= end_date:
    if skip_weekends and current_date.weekday() >= 5:
        # Skip Saturday (5) and Sunday (6)
        continue
    dates_to_process.append(current_date)
    current_date += timedelta(days=1)
```

### Value Validation
- Client-side: HTML5 input validation (type="number", min="-1", max="1")
- Server-side: Python float validation with range check
- Color coding based on value range

### Conflict Handling
- Check for existing data on each date
- If exists and overwrite=False: skip, increment skipped_count
- If exists and overwrite=True: update value, increment updated_count
- If not exists: create new entry, increment added_count

## Use Cases

### 1. Historical Data Backfill
Fill in missing historical data with baseline values:
```
Period: 2023-01-01 to 2023-12-31
Value: 0.0 (neutral baseline)
Skip weekends: Yes
Overwrite: No (keep existing data)
```

### 2. Seasonal Adjustments
Mark entire seasons with specific values:
```
Summer 2024 (Jun-Aug): 0.6 (bullish season)
Winter 2024 (Dec-Feb): -0.3 (bearish season)
```

### 3. Event Marking
Mark major events across multiple days:
```
Market Crash Period: -1.0
Recovery Period: Gradual increases
Bull Run Period: 0.8 to 1.0
```

### 4. Testing & Development
Quickly populate test data:
```
Range: Last 30 days
Value: Random or specific test values
Good for testing charts and analytics
```

### 5. Correction & Reset
Fix incorrect historical data:
```
Overwrite: Yes
Apply corrected values to entire period
```

## Best Practices

### Planning Your Entry
1. **Review existing data first** - Check what dates already have values
2. **Use appropriate granularity** - Smaller ranges for more accuracy
3. **Document your logic** - Add indicator descriptions explaining the values
4. **Test with small ranges** - Try a week first before doing months

### Value Selection
- **Be consistent** - Use similar values for similar market conditions
- **Don't overuse extremes** - Reserve -1.0 and 1.0 for truly extreme conditions
- **Round to 0.1** - Easier to interpret and compare

### Weekend Handling
- **Stock markets**: Always skip weekends
- **Crypto markets**: Consider including weekends
- **Forex**: Market-specific (some pairs trade weekends)

### Overwriting Data
- **Use cautiously** - Can't undo bulk overwrites
- **Backup first** - Export existing data if making major changes
- **Verify range** - Double-check start/end dates before overwriting

## Comparison with Other Entry Methods

| Feature | Date Range Entry | Single Entry | Bulk Entry |
|---------|-----------------|--------------|------------|
| **Multiple Dates** | ✅ Same value | ❌ One date | ✅ Multiple indicators |
| **Multiple Indicators** | ❌ One indicator | ❌ One indicator | ✅ All indicators |
| **Different Values** | ❌ Same value | ✅ One value | ✅ Per indicator |
| **Best For** | Historical fills | Precise daily entry | Daily snapshot |
| **Speed** | Fast for ranges | Moderate | Fast for snapshot |

### When to Use Each

**Use Date Range Entry when:**
- Filling historical gaps with constant value
- Setting baseline periods
- Marking extended events (crashes, rallies)
- Quick testing with dummy data

**Use Single Entry when:**
- Adding today's specific value
- Updating individual dates
- Need different value per date

**Use Bulk Entry when:**
- Daily routine: updating all indicators at once
- Taking market snapshot
- Consistent daily tracking

## Troubleshooting

### "End date must be after start date"
**Solution**: Check that end date is later than start date

### "Value must be between -1.0 and 1.0"
**Solution**: Enter value in valid range or use quick action buttons

### No dates processed (all filtered out)
**Solution**: 
- If range includes only weekends and skip_weekends=Yes
- Uncheck "Skip weekends" or choose a range with weekdays

### Unexpected skip count
**Cause**: Dates already have data and overwrite=No
**Solution**: Check "Overwrite existing" to update those dates

## Future Enhancements

### Potential Features
- **Variable values**: Different value per day (pattern entry)
- **Formula-based entry**: Calculate values based on date
- **Copy from another indicator**: Duplicate date ranges
- **Batch operations**: Multiple ranges at once
- **Preview mode**: See what would change before applying
- **Undo functionality**: Rollback recent range entries
- **Import from CSV**: Bulk load from file

## Related Features

- **Single Data Entry**: Add/edit individual dates
- **Bulk Entry**: Update all indicators on one date
- **Data Export**: Export date ranges for backup
- **Charts**: Visualize the data you've entered

## Tips & Tricks

### Filling Gaps
1. View existing data to identify gaps
2. Use date range entry for each gap
3. Leave overwrite unchecked to preserve existing data

### Baseline Setting
```
1. Clear all existing data (if needed)
2. Set entire historical period to 0.0
3. Add specific dates with actual values
4. Creates baseline with highlights
```

### Gradual Updates
```
Instead of one large range:
- Week 1: -0.5
- Week 2: -0.3
- Week 3: -0.1
- Week 4: 0.0
Better captures gradual changes
```

### Testing Charts
```
Create interesting patterns:
- Jan: -1.0 (deep bottom)
- Feb-Apr: -0.5 to 0.5 (recovery)
- May-Aug: 0.8 (bull run)
- Sep-Dec: 0.3 (consolidation)
Perfect for testing chart rendering
```
