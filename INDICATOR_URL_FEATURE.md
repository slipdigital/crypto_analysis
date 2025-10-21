# Indicator URL Field

## Overview
Added an optional URL field to the Indicator model to allow storing reference links, documentation, or related resources for each indicator.

## Changes Made

### Database Schema
- **Added Column**: `url` VARCHAR(500) to `indicators` table
- **Nullable**: Yes (optional field)
- **Purpose**: Store reference URLs for indicator documentation, articles, or resources

### Model Updates
```python
class Indicator(Base):
    url = Column(String(500), nullable=True)  # Optional URL for reference/documentation
```

### Migration
- **Script**: `add_indicator_url_column.py`
- **Command**: `.venv\Scripts\python.exe add_indicator_url_column.py`
- **Status**: ✅ Completed

### Flask App Updates

#### Routes Modified
1. **indicator_create()**: Now accepts and saves URL field
2. **indicator_edit()**: Now accepts and updates URL field

#### Templates Updated
1. **indicator_form.html**: 
   - Added URL input field with type="url" validation
   - Placeholder text and help text
   - Max length: 500 characters

2. **indicators.html**: 
   - Displays "Reference Link" button if URL exists
   - Opens in new tab with security attributes (rel="noopener noreferrer")
   - Bootstrap icon for visual clarity

## Usage

### Adding URL to New Indicator
1. Go to **Indicators** → **Create New Indicator**
2. Fill in Title and Description
3. Enter URL in the **Reference URL** field (e.g., `https://tradingview.com/wiki/RSI`)
4. Click **Create**

### Adding URL to Existing Indicator
1. Go to **Indicators** → Find indicator → Click **Edit**
2. Enter URL in the **Reference URL** field
3. Click **Save Changes**

### Viewing Reference Links
- On the indicators list page, indicators with URLs show a blue **Reference Link** button
- Click the button to open the URL in a new tab

## Examples

### Example URLs
- **Technical Indicator**: `https://www.investopedia.com/terms/r/rsi.asp`
- **Trading Strategy**: `https://tradingview.com/ideas/macd-crossover/`
- **Research Paper**: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1234567`
- **YouTube Tutorial**: `https://youtube.com/watch?v=example`
- **Documentation**: `https://docs.example.com/indicators/custom-rsi`

## Benefits
- **Quick Reference**: Easy access to indicator documentation
- **Knowledge Base**: Build a library of resources for each indicator
- **Sharing**: Share specific indicator methodologies with team members
- **Learning**: Link to tutorials or educational content
- **Attribution**: Credit original sources or creators

## Technical Details

### Validation
- HTML5 URL validation on client-side
- Browser shows error for invalid URL format
- Empty/null values allowed (field is optional)

### Security
- Links open in new tab (`target="_blank"`)
- Security attributes added (`rel="noopener noreferrer"`) to prevent:
  - Tabnapping attacks
  - Referrer leakage

### Database
- Maximum length: 500 characters
- Sufficient for most URLs including query parameters
- Can store shortened URLs (bit.ly, tinyurl, etc.)

## Future Enhancements
- URL validation on server-side
- URL preview/metadata fetching
- Link checking (verify if URL is active)
- Multiple URLs per indicator
- URL categories (Documentation, Tutorial, Research, etc.)
