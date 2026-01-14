# Trading Signals Database - Quick Start

## What's New? 🎉

A complete **Trading Signals Database** system has been added to your ForexAnalyzer! Now every BUY/SELL signal generated is automatically saved with full trade plan details and displayed in an organized, easy-to-use interface.

## Key Features

### ✅ **Automatic Signal Storage**
- Signals automatically saved on every analysis
- Complete trade plan with entry/exit points
- Organized by asset and timeframe

### ✅ **Rich Signal Details**
- **Signal Type**: BUY or SELL
- **Strength Level**: Confidence percentage
- **3 Entry Points**: Immediate, Pullback, Aggressive
- **3 Take Profit Levels**: Quick, Conservative, Extended
- **3 Stop Loss Levels**: Tight (1 ATR), Standard (2 ATR), Wide (3 ATR)
- **Risk Metrics**: R:R ratio and risk percentage
- **Market Context**: Trend, momentum, reversal warnings

### ✅ **UI Display in Scanner**
- New "Signal History & Recommendations" section
- View last 20 signals per timeframe
- Color-coded tables (green for BUY, red for SELL)
- Expandable detail views for each signal
- Summary statistics by timeframe

### ✅ **Weekly Rotation**
- Signals kept active for 7 days
- Automatic archiving of old signals
- Permanent deletion after 30 days
- Runs automatically via scheduler

## Files Created

```
src/database/signals_db.py          # Signals database manager
src/utils/signal_display.py         # UI display utilities
SIGNALS_DATABASE_GUIDE.md           # Complete documentation
SIGNALS_FEATURE_SUMMARY.md          # This file
test_signals_db.py                  # Test script
```

## Files Modified

```
src/forex_analyzer.py               # Added signal storage on analysis
pages/1_📊_Scanner.py               # Added signal history display
run_scheduler.py                    # Added signals cleanup
```

## How to Use

### 1. Test the Installation

```bash
python test_signals_db.py
```

This will:
- Initialize the database
- Create a test signal
- Verify retrieval functions
- Test cleanup functionality

### 2. Generate Real Signals

**Option A: Via Scanner UI**
1. Run: `streamlit run app.py`
2. Go to **📊 Scanner** page
3. Select assets and click **🔍 Scan All**
4. Signals automatically saved!

**Option B: Via Scheduler (Automated)**
```bash
python run_scheduler.py
```
- Runs analysis automatically on schedule
- Saves signals continuously
- Handles cleanup automatically

### 3. View Signal History

1. Go to **📊 Scanner** page
2. Scroll to **"Signal History & Recommendations"** section
3. Select an asset from dropdown
4. View signals organized by timeframe (15m, 1h, 4h, 1d)
5. Click **"View Latest Signal Details"** for full trade plan

## Signal Display Format

### Summary Table
```
Date                Signal  Strength      Confidence  Entry    Stop Loss  Take Profit  R:R      Trend
2025-11-16 10:30   BUY     STRONG        72.5%       1.0950   1.0920     1.1000       1:2.5   BULLISH
2025-11-16 08:15   SELL    VERY_STRONG   85.0%       1.0945   1.0970     1.0890       1:3.2   BEARISH
```

### Detailed View
- **3 Entry Points**: Choose based on risk tolerance
- **3 Take Profits**: Scale out for optimal profit
- **3 Stop Losses**: Match to your trading style
- **Market Context**: See trend, momentum, reversal warnings

## Database Location

```
data/signals.db              # Signals database
data/analysis.db             # Analysis database (existing)
```

## Weekly Rotation

### Automatic (Recommended)
Run the scheduler and it handles everything:
```bash
python run_scheduler.py
```

### Manual
```python
from src.database.signals_db import SignalsDB

signals_db = SignalsDB()
signals_db.cleanup_old_signals(days=7)        # Archive old signals
signals_db.delete_archived_signals(days=30)   # Delete very old signals
```

## Signal Strength Categories

| Category | Confidence | Description |
|----------|------------|-------------|
| **VERY_STRONG** | ≥75% | Multiple indicators strongly aligned |
| **STRONG** | 60-74% | Most indicators agree, good confidence |
| **MODERATE** | 45-59% | Acceptable confidence, some disagreement |
| **WEAK** | <45% | Low confidence, mixed signals |

## Example Usage

### View EURUSD Signals in Python

```python
from src.database.signals_db import SignalsDB

signals_db = SignalsDB()

# Get last 20 signals for EURUSD on daily timeframe
signals = signals_db.get_signals(
    asset_symbol='EURUSD=X',
    timeframe='1d',
    limit=20,
    active_only=True
)

for signal in signals:
    print(f"{signal['created_at']}: {signal['signal_type']} @ {signal['current_price']}")
    print(f"  Confidence: {signal['strength_level']:.1%}")
    print(f"  Entry: {signal['entry_point_1']}")
    print(f"  SL: {signal['stop_loss_standard']}")
    print(f"  TP: {signal['take_profit_2']}")
    print()
```

### Get Signals Grouped by Timeframe

```python
signals_by_tf = signals_db.get_signals_by_timeframe(
    asset_symbol='EURUSD=X',
    limit_per_timeframe=20
)

# Result: {'15m': [...], '1h': [...], '4h': [...], '1d': [...]}

for tf, signals in signals_by_tf.items():
    print(f"{tf.upper()}: {len(signals)} signals")
```

### Get Database Statistics

```python
stats = signals_db.get_stats()

print(f"Active signals: {stats['total_active_signals']}")
print(f"This week: {stats['this_week_signals']}")
print(f"By type: {stats['signals_by_type']}")
print(f"By timeframe: {stats['signals_by_timeframe']}")
```

## Benefits

### For Trading
- ✅ Complete signal history for review
- ✅ Multiple entry/exit options per signal
- ✅ Risk metrics for every trade
- ✅ Market context to understand conditions

### For Analysis
- ✅ Track signal performance over time
- ✅ Compare signals across timeframes
- ✅ Identify strong vs weak signals
- ✅ Learn from historical signals

### For Organization
- ✅ Automatic storage - no manual work
- ✅ Weekly rotation keeps database clean
- ✅ Easy-to-use UI for quick review
- ✅ Programmatic access for advanced users

## What's Different from Analysis Database?

| Feature | Analysis DB | Signals DB |
|---------|-------------|------------|
| **Purpose** | Track market analysis changes | Store actionable trading signals |
| **Content** | Full analysis with all indicators | Focused trade plans |
| **Frequency** | Every analysis run | Only BUY/SELL signals |
| **Retention** | 7 days active | 7 days active, 30 days archived |
| **UI Display** | Analysis history viewer | Signal tables in Scanner |

Both databases work together:
- **Analysis DB**: "What changed in the market?"
- **Signals DB**: "What trades should I consider?"

## Troubleshooting

### No signals showing
**Problem**: Signal history section shows no signals
**Solution**: Run an analysis first to generate signals

### Signals not updating
**Problem**: New analysis but signals not appearing
**Solution**: Check that `data/signals.db` exists and has write permissions

### Old signals not rotating
**Problem**: Signals older than 7 days still showing
**Solution**: Run scheduler or manually call `cleanup_old_signals()`

## Next Steps

1. ✅ **Test the feature**: Run `python test_signals_db.py`
2. ✅ **Generate signals**: Run Scanner or Scheduler
3. ✅ **View history**: Check Scanner → Signal History section
4. ✅ **Read docs**: See `SIGNALS_DATABASE_GUIDE.md` for details

## Support

- **Full Documentation**: `SIGNALS_DATABASE_GUIDE.md`
- **Test Script**: `python test_signals_db.py`
- **Database Manager**: `src/database/signals_db.py`
- **UI Components**: `src/utils/signal_display.py`

---

**Enjoy the new Trading Signals Database! 🚀**

This feature automatically tracks all your trading signals with complete trade plans, making it easier to review opportunities and make informed trading decisions.
