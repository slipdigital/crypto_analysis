# Bulk Indicator Entry - Quick Start

## What's New?

A new page that allows you to update **multiple indicators at once**, all sharing the same date!

## Quick Access

1. **From Indicators Page**: Click the green "Bulk Entry" button
2. **From Navigation Menu**: Click "Bulk Entry" in the top nav

## How It Works

### Simple 3-Step Process

1. **Pick a Date** (defaults to today)
2. **Enter Values** for indicators you want to update (-1.0 to 1.0)
3. **Click "Save All Values"**

## Key Features

### ⚡ Quick Fill Buttons
- **-1.0 Bearish**: Set all to extremely bearish
- **0.0 Neutral**: Set all to neutral
- **1.0 Bullish**: Set all to extremely bullish
- **Clear All**: Remove all values

### 🎨 Visual Feedback
- Cards turn **green** when you enter a value
- Gradient bars show value position
- Color-coded badges (red→yellow→gray→blue→green)
- Live count of filled vs empty indicators

### 🎯 Smart Saving
- **Skip Indicators**: Leave empty fields - only filled indicators are saved
- **Auto-Update**: Existing data for the date is updated (no duplicates)
- **Validation**: Values automatically clamped to -1.0 to 1.0 range

### ⌨️ Keyboard Shortcuts
- **Ctrl+S**: Save all values
- **Ctrl+0**: Fill all with 0 (neutral)

## Example Use Case

**Daily Market Update** (takes ~2 minutes):

```
1. Open Bulk Entry (auto-selects today)
2. Quick review of your indicators:
   - RSI: -0.7 (overbought, bearish)
   - MACD: 0.5 (bullish crossover)
   - Volume: 0.2 (slightly up)
   - Sentiment: -0.3 (slightly fearful)
3. Click "Save All Values"
4. Done! All 4 indicators updated for today
```

## UI Layout

```
┌─────────────────────────────────────────────┐
│ Date: [2025-10-15]  [Quick Fill] [Save All]│ ← Sticky Header
├─────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐                 │
│ │ RSI  │ │MACD  │ │Volume│ ...             │ ← Indicator Cards
│ │[===] │ │[===] │ │[===] │                 │   (3 columns on desktop)
│ │█████ │ │█████ │ │█████ │                 │
│ │ 0.50 │ │-0.30 │ │ 0.10 │                 │
│ └──────┘ └──────┘ └──────┘                 │
└─────────────────────────────────────────────┘
```

## What Gets Saved?

✅ **New Data**: Creates new indicator_data records  
✅ **Updates**: Updates existing data for the same date  
❌ **Empty Fields**: Skipped (not saved)  
❌ **Invalid Values**: Shown as warnings  

## Success Message Example

```
✓ Bulk entry for 2025-10-15: 
  8 new data point(s) added, 
  2 data point(s) updated, 
  3 indicator(s) skipped
```

## Tips for Fast Entry

1. **Use Quick Fill** as a baseline (e.g., start with "0.0 Neutral")
2. **Adjust Only What Changed** - leave the rest
3. **Use Sliders** for speed - type exact values only when needed
4. **Watch the Green Cards** - easy to see what's filled
5. **Make It a Routine** - end-of-day habit takes 2-3 minutes

## Access Requirements

- Must have at least one indicator created
- Date cannot be in the future
- Values must be between -1.0 and 1.0

## Route

- **URL**: `http://localhost:5001/indicators/bulk-entry`
- **Methods**: GET (show form), POST (save data)

## Testing Steps

1. **Restart Flask** if it's running (to load new routes)
2. Navigate to **Indicators** page
3. Click **"Bulk Entry"** button (green)
4. Enter values for a few indicators
5. Click **"Save All Values"**
6. Check individual indicators to see the data was saved

## Related Features

- **Individual Entry**: `/indicators/<id>/data/add` - Add to one indicator
- **Data List**: `/indicators/<id>/data` - View all data for one indicator
- **Indicators**: `/indicators` - Manage your indicators

---

**Need Help?** See `BULK_ENTRY_README.md` for complete documentation.
