# Indicator Data Feature

## Overview
The Indicator Data feature allows you to track time-series data points for each indicator. Each data point consists of a date and a normalized value between -1.0 and 1.0, representing bearish to bullish sentiment or any other metric you wish to track.

## Features

### Data Point Management
- **Add Data Points**: Create new data points with date and value
- **Edit Data Points**: Update existing data point values
- **Delete Data Points**: Remove unwanted data points
- **View History**: See all data points for an indicator in chronological order

### Value Range
- Values must be between **-1.0** (extremely bearish) and **1.0** (extremely bullish)
- **0.0** represents neutral
- The value range is enforced on both client and server side

### Statistics Dashboard
For each indicator with data, you'll see:
- **Total Points**: Count of all data points
- **Latest Value**: Most recent data point with date
- **Average**: Mean value across all data points
- **Minimum**: Lowest value recorded
- **Maximum**: Highest value recorded
- **Range**: Difference between max and min

### Visual Representation
- **Interactive Slider**: Drag to select values when adding/editing
- **Color-Coded Badges**: Values are color-coded from red (bearish) to green (bullish)
- **Visual Bar**: Each data point shows its position on a gradient scale
- **Real-Time Preview**: See value changes as you adjust the slider

## Database Schema

### indicator_data Table
```sql
CREATE TABLE indicator_data (
    id SERIAL PRIMARY KEY,
    indicator_id INTEGER NOT NULL REFERENCES indicators(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    value FLOAT NOT NULL CHECK (value >= -1.0 AND value <= 1.0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(indicator_id, date)
);

CREATE INDEX idx_indicator_data_indicator_id ON indicator_data(indicator_id);
CREATE INDEX idx_indicator_data_date ON indicator_data(date);
```

## Usage

### Adding Data Points

1. Navigate to the **Indicators** page
2. Click **"View Data"** on any indicator card
3. Click **"Add Data Point"** button
4. Select a date (cannot be in the future)
5. Enter or slide to select a value between -1.0 and 1.0
6. Click **"Add Data Point"**

### Editing Data Points

1. From the indicator data list, click the **Edit** (pencil) button
2. Modify the date or value as needed
3. Click **"Update Data Point"**

### Deleting Data Points

1. From the indicator data list, click the **Delete** (trash) button
2. Confirm the deletion in the modal dialog
3. The data point will be permanently removed

## Routes

### View Data Points
- **URL**: `/indicators/<indicator_id>/data`
- **Method**: GET
- **Description**: Lists all data points for an indicator with statistics

### Add Data Point
- **URL**: `/indicators/<indicator_id>/data/add`
- **Methods**: GET, POST
- **Description**: Form to create a new data point

### Edit Data Point
- **URL**: `/indicators/<indicator_id>/data/<data_id>/edit`
- **Methods**: GET, POST
- **Description**: Form to update an existing data point

### Delete Data Point
- **URL**: `/indicators/<indicator_id>/data/<data_id>/delete`
- **Method**: POST
- **Description**: Removes a data point

## Validation Rules

### Date Validation
- Required field
- Must be a valid date in YYYY-MM-DD format
- Cannot be in the future
- Must be unique per indicator (one value per date per indicator)

### Value Validation
- Required field
- Must be a number between -1.0 and 1.0 (inclusive)
- Validated on both client-side (HTML5) and server-side (Flask)

## Value Interpretation Guide

| Range | Color | Interpretation | Example Use Cases |
|-------|-------|----------------|-------------------|
| 1.0 to 0.5 | Green | Strongly Bullish | Extremely positive indicators |
| 0.5 to 0.0 | Blue | Moderately Bullish | Positive but cautious |
| 0.0 | Gray | Neutral | No clear direction |
| 0.0 to -0.5 | Orange | Moderately Bearish | Negative but not extreme |
| -0.5 to -1.0 | Red | Strongly Bearish | Extremely negative indicators |

## Tips for Effective Use

1. **Consistency**: Use the same criteria when assigning values to maintain consistency over time
2. **Documentation**: Use the indicator description to document what each value range means for that specific indicator
3. **Regular Updates**: Update indicators regularly to maintain useful time-series data
4. **Trend Analysis**: Look at the statistics to identify trends (increasing/decreasing average, volatility)
5. **Multiple Indicators**: Compare multiple indicators side-by-side for comprehensive analysis

## Integration Points

### Models
- `IndicatorData` model in `models.py`
- Foreign key relationship to `Indicator` with cascade delete
- Unique constraint on (indicator_id, date)

### Templates
- `indicator_data.html`: List view with statistics and visual bars
- `indicator_data_form.html`: Add/edit form with slider and preview
- `indicators.html`: Updated with "View Data" button

### Database Migration
- Migration script: `create_indicator_data_table.py`
- Creates table with indexes on indicator_id and date
- Verifies creation before reporting success

## Future Enhancements

Potential improvements for the indicator data feature:

1. **Charting**: Add Chart.js line charts to visualize data over time
2. **Bulk Import**: Allow CSV upload for batch data import
3. **Export**: Download data points as CSV or JSON
4. **API Access**: RESTful API endpoints for programmatic access
5. **Calculations**: Auto-calculate derived metrics (moving averages, momentum, etc.)
6. **Alerts**: Set up alerts when values cross certain thresholds
7. **Comparison**: Overlay multiple indicators on the same chart
8. **Notes**: Add text notes to specific data points for context

## Technical Notes

- Data points are sorted by date in descending order (newest first)
- Uses SQLAlchemy ORM for database operations
- Flash messages provide user feedback for all operations
- Modal dialogs confirm destructive actions (delete)
- Client-side JavaScript syncs slider and input field values
- Responsive Bootstrap 5 design works on all screen sizes

## Error Handling

The system handles various error conditions:

- **Duplicate Dates**: Prevents adding multiple data points for the same date
- **Invalid Values**: Rejects values outside -1.0 to 1.0 range
- **Missing Indicator**: Redirects with error message if indicator not found
- **Database Errors**: Rolls back transactions and displays user-friendly messages
- **Invalid Date Formats**: Catches parsing errors and provides feedback

## Example Workflow

1. Create an indicator: "Market Sentiment"
2. Add data points over time:
   - 2024-01-01: 0.8 (very bullish)
   - 2024-01-15: 0.5 (moderately bullish)
   - 2024-02-01: -0.2 (slightly bearish)
   - 2024-02-15: -0.6 (moderately bearish)
3. View statistics to see the trend shifting from bullish to bearish
4. Use this data to inform trading decisions or correlate with market movements
