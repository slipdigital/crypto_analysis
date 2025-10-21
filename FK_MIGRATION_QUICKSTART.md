# Foreign Key Migration - Quick Reference

## What Changed?

`TickerData` now uses `ticker_id` (foreign key) instead of `ticker` (string).

## Before Running

### 1. BACKUP DATABASE! ⚠️
```bash
pg_dump -h localhost -U postgres crypto_data > backup_before_fk_migration.sql
```

### 2. Stop Data Collection
Stop any running `update_ticker_data.py` processes

### 3. Stop Flask App
Stop the dashboard web server

## Migration Steps

### Step 1: Run Migration Script
```bash
python migrate_ticker_fk.py
```

**What it does:**
- Adds `ticker_id` column
- Populates from existing `ticker` strings
- Adds foreign key constraint
- Removes old `ticker` column

**Time:** ~1-5 minutes depending on data volume

### Step 2: Verify Migration
```bash
# Check record count (should be unchanged)
psql -h localhost -U postgres crypto_data -c "SELECT COUNT(*) FROM ticker_data;"

# Check new schema
psql -h localhost -U postgres crypto_data -c "\d ticker_data"
# Should show ticker_id as foreign key
```

### Step 3: Test Application
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Start Flask app
cd flask_app
python app.py

# Visit http://localhost:5000
# Test: dashboard, charts, ticker details, comparison
```

### Step 4: Test Data Collection
```bash
# Test with 1 ticker
python update_ticker_data.py --limit 1

# If successful, run for all
python update_ticker_data.py
```

## Rollback (If Needed)

```bash
# 1. Restore database
psql -h localhost -U postgres -d crypto_data < backup_before_fk_migration.sql

# 2. Revert code
git checkout HEAD -- models.py
git checkout HEAD -- flask_app/app.py
git checkout HEAD -- update_ticker_data.py

# 3. Remove migration script
rm migrate_ticker_fk.py
```

## Code Changes Summary

### Models
```python
# OLD
ticker = Column(String, nullable=False, index=True)

# NEW
ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False, index=True)
ticker_obj = relationship("Ticker", back_populates="ticker_data")
```

### Queries
```python
# OLD
TickerData.ticker == "X:BTCUSD"

# NEW
TickerData.ticker_id == ticker.id
```

### Creating Data
```python
# OLD
TickerData(ticker="X:BTCUSD", date=today, ...)

# NEW
ticker = session.query(Ticker).filter_by(ticker="X:BTCUSD").first()
TickerData(ticker_id=ticker.id, date=today, ...)
```

## Verification Checklist

After migration, verify:

- [ ] Dashboard loads
- [ ] Ticker count matches pre-migration
- [ ] Charts display
- [ ] Ticker detail pages work
- [ ] Comparison feature works
- [ ] Outdated data warning shows
- [ ] Data collection script runs
- [ ] No errors in logs

## Benefits

✅ **Faster queries** - Integer joins vs string joins  
✅ **Data integrity** - Database enforces relationships  
✅ **Less storage** - Integers smaller than strings  
✅ **Cascade deletes** - Auto-cleanup when ticker removed  
✅ **Best practices** - Proper relational design  

## Support

If issues occur:
1. Check error messages
2. Verify database schema
3. Test queries manually
4. Review FOREIGN_KEY_MIGRATION.md
5. Restore from backup if needed

## Migration Script Output

Expected successful output:
```
============================================================
TICKER DATA FOREIGN KEY MIGRATION
============================================================

Step 1: Adding ticker_id column...
✓ ticker_id column added

Step 2: Populating ticker_id from ticker strings...
✓ Updated 50000 rows

Step 3: Checking for orphaned records...
✓ No orphaned records found

Step 4: Dropping old unique constraint...
✓ Old constraint dropped

Step 5: Making ticker_id NOT NULL...
✓ ticker_id is now NOT NULL

Step 6: Adding foreign key constraint...
✓ Foreign key constraint added

Step 7: Adding index on ticker_id...
✓ Index added

Step 8: Creating new unique constraint on (ticker_id, date)...
✓ New unique constraint added

Step 9: Dropping old ticker column and index...
✓ Old ticker column and index dropped

Step 10: Verifying migration...
✓ ticker_data has 50000 records

✅ Migration completed successfully!
```

## Common Issues

### "ticker column does not exist"
**Solution:** Code not updated - check you've updated all files

### "foreign key constraint violation"
**Solution:** Trying to insert data for non-existent ticker - ensure ticker exists first

### "migration script hangs"
**Solution:** Large dataset - be patient or run on smaller data first

## Performance Comparison

**Before Migration:**
- String comparison: `ticker = 'X:BTCUSD'`
- Slower joins, more storage

**After Migration:**
- Integer comparison: `ticker_id = 123`
- Faster joins, less storage

**Typical Improvements:**
- 20-40% faster queries
- 60-80% less storage for ticker column
- Better index performance

## Next Steps After Migration

1. Monitor application for errors
2. Check query performance
3. Update any custom scripts to use ticker_id
4. Consider adding more foreign key relationships
5. Update documentation

## Files Changed

✅ `models.py` - Schema updated  
✅ `migrate_ticker_fk.py` - NEW migration script  
✅ `update_ticker_data.py` - Updated queries  
✅ `flask_app/app.py` - Updated all routes  

---

**Remember:** Always backup before running migrations!
