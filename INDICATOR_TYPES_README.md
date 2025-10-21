# Indicator Types Feature

## Overview
The Indicator Types feature allows you to categorize and visually organize your indicators using custom types with color coding. This makes it easier to manage and identify different categories of indicators at a glance.

## Features

### 1. Indicator Type Management
- **Create Types**: Define custom indicator types with unique names, descriptions, and colors
- **Edit Types**: Update type names, descriptions, and colors
- **Delete Types**: Remove unused types (protected if indicators are using them)
- **Color Coding**: Each type has a unique color for visual distinction

### 2. Type Integration with Indicators
- **Optional Classification**: Assign indicators to types during creation or editing
- **Visual Badges**: Indicators display their type with a colored badge
- **Quick Access**: Manage types button on the indicators page
- **Flexible Organization**: Indicators can exist without a type (backward compatible)

## Database Schema

### IndicatorType Model
```python
class IndicatorType(Base):
    __tablename__ = 'indicator_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # Unique type name
    description = Column(Text)                                # Optional description
    color = Column(String(7), nullable=False)                 # Hex color code
    created_at = Column(String(30), nullable=False)
    updated_at = Column(String(30), nullable=False)
```

### Indicator Model (Updated)
```python
class Indicator(Base):
    __tablename__ = 'indicators'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    indicator_type_id = Column(Integer, ForeignKey('indicator_types.id'), nullable=True)  # NEW
    created_at = Column(String(30), nullable=False)
    updated_at = Column(String(30), nullable=False)
```

## Usage

### Creating Indicator Types

1. **Navigate to Indicator Types**
   - Click "Types" in the navigation menu
   - Or click "Manage Types" on the Indicators page

2. **Create New Type**
   - Click "Create Type" button
   - Fill in the form:
     - **Name** (required): Unique name for the type
     - **Description** (optional): Detailed explanation
     - **Color** (required): Choose a color using the color picker
   - Click "Create" to save

3. **Default Types**
   The migration script creates these default types:
   - **Technical** (Blue #3B82F6): Technical analysis indicators
   - **Sentiment** (Purple #8B5CF6): Market sentiment indicators
   - **On-Chain** (Green #10B981): Blockchain metrics
   - **Fundamental** (Amber #F59E0B): Fundamental analysis
   - **Macro** (Red #EF4444): Macroeconomic indicators
   - **Custom** (Gray #6B7280): Custom indicators

### Managing Indicators with Types

1. **Assign Type During Creation**
   - When creating a new indicator, select a type from the dropdown
   - Leave as "-- No Type --" if you don't want to categorize it
   - See a live preview of the type's color badge

2. **Assign Type to Existing Indicators**
   - Edit an existing indicator
   - Select a type from the dropdown
   - Click "Save Changes"

3. **View Indicators by Type**
   - Type badges appear in the indicator cards
   - Colored badges make it easy to identify categories at a glance

### Editing and Deleting Types

1. **Edit Type**
   - Go to Indicator Types page
   - Click "Edit" on the type card
   - Update name, description, or color
   - Click "Edit" to save changes

2. **Delete Type**
   - Click "Delete" on the type card
   - Confirm deletion in the modal
   - **Note**: Cannot delete types that are assigned to indicators
   - Must reassign or delete those indicators first

## API Routes

### Indicator Type Routes
- `GET /indicator-types` - List all indicator types
- `GET /indicator-types/create` - Show create form
- `POST /indicator-types/create` - Create new type
- `GET /indicator-types/<id>/edit` - Show edit form
- `POST /indicator-types/<id>/edit` - Update type
- `POST /indicator-types/<id>/delete` - Delete type

### Updated Indicator Routes
- `GET /indicators/create` - Now includes type selector
- `POST /indicators/create` - Accepts `indicator_type_id` parameter
- `GET /indicators/<id>/edit` - Shows current type
- `POST /indicators/<id>/edit` - Updates `indicator_type_id`

## Migration

### Running the Migration
```bash
python create_indicator_types_table.py
```

The migration script:
1. Creates the `indicator_types` table
2. Adds `indicator_type_id` column to `indicators` table
3. Inserts 6 default indicator types
4. Is idempotent (safe to run multiple times)

### Manual Migration (if needed)
```sql
-- Create indicator_types table
CREATE TABLE indicator_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) NOT NULL,
    created_at VARCHAR(30) NOT NULL,
    updated_at VARCHAR(30) NOT NULL
);

-- Add indicator_type_id column to indicators
ALTER TABLE indicators 
ADD COLUMN indicator_type_id INTEGER REFERENCES indicator_types(id);
```

## Benefits

### Organization
- **Categorization**: Group related indicators together
- **Visual Distinction**: Quickly identify indicator types by color
- **Flexible Structure**: Optional types allow gradual adoption

### Usability
- **Quick Identification**: Color badges make scanning easier
- **Consistent Naming**: Standardize indicator categories
- **Easy Management**: Central location to manage all types

### Scalability
- **Unlimited Types**: Create as many types as needed
- **Custom Colors**: Choose colors that match your workflow
- **Protected Deletion**: Prevents accidental removal of used types

## Best Practices

### Naming Types
- Use clear, descriptive names (e.g., "Technical", "Sentiment")
- Be consistent with terminology
- Avoid overly specific names that limit reuse

### Choosing Colors
- Use distinct colors that are easy to differentiate
- Consider color blindness (avoid red/green combinations)
- Use darker colors for better text contrast
- Recommended palette:
  - Blue family: Technical indicators
  - Purple family: Sentiment/psychology
  - Green family: Growth/on-chain metrics
  - Red/Orange: Risk/macro factors
  - Gray: General/uncategorized

### Type Organization
- Start with broad categories, refine as needed
- Don't over-categorize - 5-8 types is usually sufficient
- Review and consolidate unused types periodically

## Examples

### Example 1: Technical Indicators Type
```
Name: Technical Analysis
Description: Indicators based on price action, volume, and statistical analysis
Color: #3B82F6 (Blue)
```

### Example 2: Sentiment Type
```
Name: Market Sentiment
Description: Indicators measuring fear, greed, and market psychology
Color: #8B5CF6 (Purple)
```

### Example 3: Creating an Indicator with Type
1. Go to Indicators → Create New Indicator
2. Fill in:
   - Title: "RSI Overbought (70+)"
   - Description: "Relative Strength Index above 70"
   - Type: "Technical Analysis"
3. See the blue badge preview
4. Click "Create"

## Troubleshooting

### Cannot Delete Type
**Error**: "Cannot delete because X indicator(s) are using it"

**Solution**:
1. Go to the Indicators page
2. Find all indicators with that type (look for the colored badge)
3. Edit each indicator and either:
   - Assign a different type, or
   - Remove the type (select "-- No Type --")
4. Return to Indicator Types and delete

### Type Not Showing in Dropdown
**Issue**: Type doesn't appear when creating/editing indicators

**Solution**:
- Ensure the type was created successfully (check Indicator Types page)
- Try refreshing the page
- Check browser console for JavaScript errors

### Colors Not Displaying
**Issue**: Type badges appear but without color

**Solution**:
- Verify the color value is a valid hex code (e.g., #3B82F6)
- Edit the type and re-save with a valid color
- Clear browser cache and refresh

## Integration with Existing Features

### Works With
- ✅ Indicator Data tracking
- ✅ Bulk Entry page
- ✅ Indicator editing
- ✅ Indicator deletion
- ✅ All existing CRUD operations

### Backward Compatibility
- ✅ Existing indicators work without types
- ✅ No data migration required for old indicators
- ✅ Optional feature - use as much or as little as needed

## Future Enhancements

### Potential Features
- Filter indicators by type on the list page
- Type-based dashboard views
- Export/import type configurations
- Type statistics and analytics
- Type-specific default values
- Bulk type assignment tool

## Technical Notes

### Foreign Key Relationship
- `indicator_type_id` is nullable for backward compatibility
- ON DELETE behavior: Protected (cannot delete if in use)
- Index recommended for large datasets

### Performance
- Minimal impact on existing queries
- Additional JOIN only when type information is needed
- Indexed foreign key for efficient lookups

### Security
- Name uniqueness enforced at database level
- Form validation for required fields
- CSRF protection via Flask
- SQL injection protection via SQLAlchemy ORM
