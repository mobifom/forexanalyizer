# Analysis Database & History Tracking Guide

## Overview

The Forex Analyzer now stores all analysis results in a SQLite database with:
- ✅ **Analysis Storage** - Every analysis result is saved with full details
- ✅ **Change Tracking** - Automatic comparison with previous analysis
- ✅ **History Viewing** - Review past analyses and trends
- ✅ **Weekly Rotation** - Automatic cleanup of data older than 7 days
- ✅ **Statistics** - Track signal distribution and changes

---

## Features

### 1. **Automatic Storage**

Every time an analysis is performed, the system automatically:
1. Stores the complete analysis results
2. Compares with the previous analysis
3. Tracks what changed (signal, confidence, indicators)
4. Logs significant changes
5. Marks the new analysis as "latest"

### 2. **Change Detection**

The system detects and categorizes changes:

| Change Type | Description | Significance |
|-------------|-------------|--------------|
| **SIGNAL_CHANGE** | Consensus changed (BUY↔SELL↔HOLD) | HIGH |
| **SIGNAL_REVERSAL** | Complete reversal (BUY↔SELL) | HIGH |
| **REVERSAL_DETECTED** | Trend reversal detected | HIGH |
| **CONFIDENCE_CHANGE** | Confidence changed by 10%+ | MEDIUM/HIGH |
| **TIMEFRAME_SIGNAL_CHANGE** | Individual timeframe signal changed | MEDIUM |
| **RSI_CHANGE** | RSI entered/exited zones | MEDIUM/HIGH |

### 3. **Weekly Data Rotation**

Automatically cleans up old data:
- **Runs**: Once per day (automatic)
- **Keeps**: Last 7 days of data
- **Preserves**: Latest analysis for each asset (always kept)
- **Deletes**: Historical data older than 7 days

---

## Database Schema

### Tables

#### 1. `analysis_results`
Stores complete analysis results for each asset/timeframe.

**Key Fields:**
- `asset_symbol` - Asset identifier (EURUSD=X, BTC/USD, etc.)
- `timeframe` - Analysis timeframe (15m, 1h, 4h, 1d)
- `consensus` - Overall signal (BUY, SELL, HOLD)
- `confidence` - Signal confidence (0-1)
- `tf_*_signal` - Individual timeframe signals
- `tf_*_confidence` - Individual timeframe confidences
- `rsi`, `macd`, `price`, `atr` - Technical indicators
- `trend_strength`, `momentum` - Trend analysis
- `reversal_detected`, `reversal_type` - Reversal detection
- `nearest_support`, `nearest_resistance` - Key levels
- `stop_loss`, `take_profit`, `risk_reward_ratio` - Trade plan
- `full_analysis` - Complete analysis JSON
- `is_latest` - Flag for current analysis

#### 2. `analysis_changes`
Tracks changes between consecutive analyses.

**Key Fields:**
- `asset_symbol`, `timeframe`
- `previous_signal`, `current_signal`
- `signal_changed` - Boolean flag
- `confidence_change` - Numeric change
- `confidence_direction` - UP, DOWN, STABLE
- `change_type` - Category of change
- `change_description` - Human-readable description
- Links to `previous_analysis_id` and `current_analysis_id`

#### 3. `analysis_summary`
Daily/hourly summaries of analysis activity.

---

## Usage

### Running the Scheduler (Stores Analysis Automatically)

```bash
python run_scheduler.py
```

The scheduler now:
- Fetches data on schedule
- Analyzes each asset
- **Stores results in database**
- **Compares with previous analysis**
- **Logs changes**
- **Runs daily cleanup**

### Viewing Analysis History

Use the `view_analysis_history.py` tool:

#### Show Latest Analyses (All Assets)

```bash
python view_analysis_history.py --latest
```

Output:
```
================================================================================
LATEST ANALYSIS RESULTS
================================================================================

🟢 EURUSD=X (1d)
  Signal: BUY
  Confidence: 65.0%
  Price: $1.08234
  RSI: 45.2
  Trend Strength: 68.0%
  Analyzed: 2025-01-11 14:30:00

🟡 BTC/USD (1d)
  Signal: HOLD
  Confidence: 52.0%
  Price: $42,150.00
  RSI: 58.1
  Analyzed: 2025-01-11 14:28:00
```

#### Show Latest for Specific Asset

```bash
python view_analysis_history.py --latest --asset "EURUSD=X"
python view_analysis_history.py -l -a "BTC/USD"
```

#### View Recent Changes

```bash
# Last 24 hours (default)
python view_analysis_history.py --changes

# Last 48 hours
python view_analysis_history.py --changes --hours 48

# Specific asset
python view_analysis_history.py --changes --asset "US30"
```

Output:
```
================================================================================
RECENT CHANGES (Last 24 hours)
================================================================================

🔄 EURUSD=X (1d) - 2025-01-11 10:15:00
  Signal: HOLD → BUY
  Change Type: NEW_SIGNAL
  Description: New BUY signal generated
  Confidence: ↑ 15.0%

🔄 BTC/USD (1d) - 2025-01-11 08:30:00
  Signal: BUY → BUY
  Change Type: CONFIDENCE_CHANGE
  Description: Confidence increased by 12.5%
  Confidence: ↑ 12.5%
```

#### View Full History

```bash
# Last 7 days (default)
python view_analysis_history.py --history --asset "EURUSD=X"

# Last 14 days
python view_analysis_history.py --history --asset "BTC/USD" --days 14

# Specific timeframe
python view_analysis_history.py --history --asset "US30" --timeframe "4h"
```

Output:
```
================================================================================
ANALYSIS HISTORY: EURUSD=X (1d) - Last 7 days
================================================================================

Found 42 analyses

1. 🟢 2025-01-11 14:30:00
   Signal: BUY (Confidence: 65.0%)
   Price: $1.08234
   RSI: 45.2

2. 🟡 2025-01-11 08:00:00
   Signal: HOLD (Confidence: 50.0%)
   Price: $1.08156
   RSI: 48.8

3. 🟢 2025-01-10 20:00:00
   Signal: BUY (Confidence: 58.0%)
   Price: $1.08089
   RSI: 42.1 [OVERSOLD]
   ⚠️  BULLISH reversal

...
```

#### Show Database Statistics

```bash
python view_analysis_history.py --stats
```

Output:
```
================================================================================
📊 DATABASE STATISTICS
================================================================================

Total analyses stored: 1,245
Current (latest) analyses: 10
Total changes tracked: 387
Changes in last 24h: 23
Oldest record: 2025-01-04 10:00:00

Current Signal Distribution:
  🟢 BUY: 4 (40.0%)
  🟡 HOLD: 5 (50.0%)
  🔴 SELL: 1 (10.0%)
```

#### Show Cleanup Information

```bash
python view_analysis_history.py --cleanup-info
```

---

## Scheduler Integration

### Enhanced Scheduler Output

When you run `python run_scheduler.py`, you'll see:

```
============================================================
🚀 STARTING FOREX ANALYZER SCHEDULER WITH ANALYSIS TRACKING
============================================================
Assets: 10
Timeframes: ['1d', '4h', '1h', '15m']
Schedule:
  15m: Every 15 minutes
  1h: Every 60 minutes
  4h: Every 240 minutes
  1d: Every 360 minutes

Features:
  ✅ Analysis results stored in database
  ✅ Change tracking enabled
  ✅ Weekly data rotation (7 days)
============================================================

============================================================
📊 ANALYSIS DATABASE STATISTICS
============================================================
Total analyses: 1,245
Latest analyses: 10
Total changes tracked: 387
Changes (last 24h): 23

Current Signal Distribution:
  BUY: 4
  HOLD: 5
  SELL: 1
============================================================

✅ Scheduler running. Press Ctrl+C to stop.
```

### Analysis Logging with Changes

```
🔍 Starting analysis for EURUSD=X across ['1d', '4h', '1h', '15m']

📊 EURUSD=X Analysis Results:
   Consensus: BUY
   Confidence: 65.0%
   Agreement: 3/4 timeframes

📝 Changes since last analysis:
   🔴 Signal changed from HOLD to BUY
   🟡 Confidence increased by 15.0%
   🟡 4h signal changed from HOLD to BUY

✅ Analysis stored (ID: 1246)
```

---

## Monitoring & Reports

### Periodic Reports (Every 5 minutes)

```
============================================================
API USAGE REPORT
============================================================
Daily Usage: 234 / 800 calls
Daily Remaining: 566 calls
Daily Percentage: 29.3%
Last Minute: 2 / 8 calls
============================================================
```

### Statistics Report (Every 15 minutes)

```
============================================================
📊 ANALYSIS DATABASE STATISTICS
============================================================
Total analyses: 1,250
Latest analyses: 10
Total changes tracked: 390
Changes (last 24h): 25

Current Signal Distribution:
  BUY: 5
  HOLD: 4
  SELL: 1
============================================================
```

---

## Data Rotation & Cleanup

### Automatic Cleanup

The system automatically runs cleanup once per day:

```
🧹 Running weekly data cleanup...
✅ Cleanup completed: 152 old analyses removed
```

### Manual Cleanup

```bash
python -c "from src.database.analysis_db import AnalysisDB; AnalysisDB().cleanup_old_data(days=7)"
```

### What Gets Deleted

- ✅ Analysis results older than 7 days (except latest)
- ✅ Change records older than 7 days
- ✅ Summary records older than 7 days

### What Gets Kept

- ✅ Latest analysis for each asset (always preserved)
- ✅ Last 7 days of historical data
- ✅ Recent changes (last 7 days)

---

## Database Files

### Location

```
ForexAnalyzer/
├── data/
│   ├── analysis.db          # Analysis database (NEW)
│   ├── users.db             # User authentication database
│   └── cache/               # Data cache
```

### Backup

To backup analysis data:

```bash
# Copy the database file
cp data/analysis.db data/analysis_backup_$(date +%Y%m%d).db
```

To restore:

```bash
cp data/analysis_backup_20250111.db data/analysis.db
```

---

## API Reference

### Python Usage

```python
from src.database.analysis_db import AnalysisDB
from src.analysis.analysis_comparison import AnalysisComparison

# Initialize database
db = AnalysisDB()

# Get latest analysis
latest = db.get_latest_analysis('EURUSD=X', '1d')
print(f"Signal: {latest['consensus']}")
print(f"Confidence: {latest['confidence']:.1%}")

# Get recent changes
changes = db.get_analysis_changes('EURUSD=X', hours=24)
for change in changes:
    if change['signal_changed']:
        print(f"{change['previous_signal']} → {change['current_signal']}")

# Get history
history = db.get_analysis_history('EURUSD=X', '1d', days=7)
print(f"Found {len(history)} analyses in last 7 days")

# Store new analysis
analysis_data = {
    'consensus': {'consensus': 'BUY', 'confidence': 0.65},
    'timeframe_analyses': {...},
    # ... more data
}
success, analysis_id = db.store_analysis('EURUSD=X', '1d', analysis_data)

# Compare analyses
previous = db.get_latest_analysis('EURUSD=X', '1d')
comparison = AnalysisComparison.compare_analyses(previous, current)

if comparison['has_changes']:
    summary = AnalysisComparison.format_change_summary(comparison)
    print(summary)

# Get statistics
stats = db.get_stats()
print(f"Total analyses: {stats['total_analyses']}")
print(f"Recent changes: {stats['recent_changes_24h']}")

# Cleanup old data
deleted = db.cleanup_old_data(days=7)
print(f"Deleted {deleted[0]} old analyses")
```

---

## Benefits

### 1. **Historical Context**
- See how signals evolved over time
- Identify patterns in signal changes
- Track confidence trends

### 2. **Change Awareness**
- Instant notification of signal changes
- Track confidence improvements/declines
- Detect reversals early

### 3. **Performance Tracking**
- Review past analyses
- Compare predictions vs outcomes
- Improve strategy based on history

### 4. **Automatic Maintenance**
- Weekly rotation keeps database small
- No manual cleanup needed
- Latest data always preserved

### 5. **Reference Data**
- Compare current analysis with past
- Understand what triggered changes
- Better decision making

---

## Files Created

| File | Purpose |
|------|---------|
| `src/database/analysis_db.py` | Analysis database manager |
| `src/analysis/analysis_comparison.py` | Comparison and formatting logic |
| `view_analysis_history.py` | CLI tool for viewing history |
| `ANALYSIS_DATABASE_GUIDE.md` | This documentation |

---

## Summary

The Analysis Database system provides:

✅ **Automatic storage** of every analysis
✅ **Change tracking** between analyses
✅ **Historical viewing** with CLI tool
✅ **Weekly rotation** to manage database size
✅ **Statistics** and monitoring
✅ **Reference data** for comparison

All analysis results are now persistent and can be reviewed, compared, and tracked over time. The system automatically manages data rotation to keep the database size reasonable while preserving recent history and the latest state.

**Start using it by running the scheduler:**
```bash
python run_scheduler.py
```

**View results anytime with:**
```bash
python view_analysis_history.py --latest
python view_analysis_history.py --changes
python view_analysis_history.py --stats
```
