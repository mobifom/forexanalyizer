# ✅ Batch Job Frequency Update

## Changes Made:

### 1️⃣ 4-Hour Timeframe
**Previous**: Every 240 minutes (4 hours) → 6 calls/asset/day
**Updated**: Every 60 minutes (1 hour) → **24 calls/asset/day**

**Reason**: More frequent updates for swing trading signals

### 2️⃣ Daily Timeframe
**Previous**: Every 360 minutes (6 hours) → 4 calls/asset/day
**Updated**: Every 1440 minutes (24 hours) → **1 call/asset/day**

**Reason**: Daily candles only need to be fetched once per day

---

## Impact on API Calls

### Per Asset:
| Timeframe | Old Frequency | New Frequency | Old Calls/Day | New Calls/Day | Change |
|-----------|--------------|---------------|---------------|---------------|---------|
| 15m | 15 min | 15 min | 96 | 96 | No change |
| 1h | 60 min | 60 min | 24 | 24 | No change |
| 4h | 240 min | **60 min** | 6 | **24** | **+18 calls** |
| 1d | 360 min | **1440 min** | 4 | **1** | **-3 calls** |
| **Total** | - | - | **130** | **145** | **+15 calls** |

### For All 10 Assets:
- **Old Total**: 1,300 calls/day
- **New Total**: 1,450 calls/day
- **Change**: +150 calls/day (+11.5%)

### With Market Hours Optimization:
- **Old Optimized**: ~740 calls/day
- **New Optimized**: ~823 calls/day
- **Free Tier Limit**: 800 calls/day
- **Status**: ⚠️ Slightly over by ~23 calls/day

---

## 📊 New Fetch Schedule

### Example for EURUSD=X:

| Time | Timeframes Fetched |
|------|-------------------|
| 00:00 | 15m, 1h, 4h, **1d** |
| 00:15 | 15m |
| 00:30 | 15m |
| 00:45 | 15m |
| 01:00 | 15m, 1h, 4h |
| 01:15 | 15m |
| ... | ... |
| 02:00 | 15m, 1h, 4h |
| ... | ... |

**Daily candle** now fetched **once** at midnight instead of 4 times throughout the day.

**4-hour candle** now fetched **every hour** instead of every 4 hours, giving you fresher data for swing trading decisions.

---

## ✅ Benefits

### 4h → Every 1 Hour:
✅ **More responsive** swing trading signals
✅ **Earlier detection** of 4h timeframe changes
✅ **Better confluence** with 1h signals
✅ **Faster analysis** updates

### 1d → Once Per Day:
✅ **API savings** (4 calls → 1 call per asset)
✅ **Logical** (daily candles don't change intraday)
✅ **Reduced redundancy** (same data fetched 4x before)
✅ **Better efficiency**

---

## ⚠️ Consideration: API Limit

With the new settings, you're **~23 calls over** the 800/day free tier limit when running all 10 assets with market hours optimization.

### Options to Stay Under Limit:

**Option A - Reduce 15m Frequency** (Recommended):
```yaml
'15m': 30  # Change from 15 to 30 minutes
```
- Saves ~480 calls/day
- New total: ~690 calls/day ✅ (well under 800)

**Option B - Reduce Asset Count**:
Remove 2-3 low priority assets:
- Remove: AUDUSD=X, XAG_USD, US100
- New total: ~725 calls/day ✅ (under 800)

**Option C - Use Current Settings**:
- The scheduler will hit the 800 limit around 11-12pm daily
- Remaining fetches will be paused until next day
- High priority assets will still be updated

---

## 🔄 When Changes Take Effect

**Immediately** after restarting the scheduler:

1. Stop the current scheduler (if running):
   ```bash
   Ctrl+C
   ```

2. Start with new settings:
   ```bash
   python run_scheduler.py
   ```

3. Verify in console output:
   ```
   Schedule:
     15m: Every 15 minutes
     1h: Every 60 minutes
     4h: Every 60 minutes    ← NEW
     1d: Every 1440 minutes  ← NEW
   ```

---

## 📈 Expected Behavior

### What You'll See:

**In Logs**:
```
2025-11-16 10:00:00 - INFO - 📊 Fetching EURUSD=X 4h
2025-11-16 10:00:01 - INFO - ✅ Successfully fetched EURUSD=X 4h: 730 candles
2025-11-16 10:00:03 - INFO - 🔍 Analyzing EURUSD=X across ['4h']
2025-11-16 11:00:00 - INFO - 📊 Fetching EURUSD=X 4h  ← 1 hour later!
2025-11-16 11:00:01 - INFO - ✅ Successfully fetched EURUSD=X 4h: 730 candles
```

**Before**: 4h data fetched at 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
**Now**: 4h data fetched **every hour**: 00:00, 01:00, 02:00, 03:00, ...

**Daily Data**:
**Before**: 1d data fetched at 00:00, 06:00, 12:00, 18:00
**Now**: 1d data fetched **once** at 00:00 (midnight)

---

## 🎯 Summary

| Change | Old | New | Impact |
|--------|-----|-----|---------|
| **4h Frequency** | Every 4 hours | Every 1 hour | +300% freshness |
| **1d Frequency** | Every 6 hours | Once daily | -75% redundancy |
| **Total Calls/Asset** | 130/day | 145/day | +11.5% |
| **API Status** | ✅ Under limit | ⚠️ Slightly over | Need minor adjustment |

**Files Modified**:
- ✅ `config/config.yaml` - Updated fetch_intervals
- ✅ `BATCH_JOB_API_FREQUENCY.md` - Updated documentation

**Recommendation**: Consider implementing **Option A** (reduce 15m to 30 min) to stay comfortably under the 800/day limit while keeping your improved 4h and 1d frequencies! 🚀
