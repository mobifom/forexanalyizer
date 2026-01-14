# 📊 Signal History Table - Complete Guide

## ✅ What's Displayed

The V2 Recommendations section now displays **the last 20 signals** from the signal history table for each asset and timeframe combination.

---

## 📋 Signal History Table Features

### 1. **Last 20 Signals Per Timeframe**

For each asset, you see:
- **Maximum 20 most recent signals** per timeframe
- Sorted by **newest first** (most recent at top)
- Includes **all signal details**

### 2. **Filtering Options**

#### By Asset Type (Sidebar)
```
Select: "Forex Major Pairs"
Shows: EURUSD, GBPUSD, USDJPY, AUDUSD
  └─ Each shows last 20 signals per timeframe
```

#### By Timeframe (Sidebar)
```
Single Timeframe: "1d"
Shows: Only daily (1d) signals for selected assets
  └─ Last 20 daily signals for each asset

Multi-Timeframe: All
Shows: All timeframes (15m, 1h, 4h, 1d)
  └─ Last 20 signals for EACH timeframe
```

### 3. **Display Format**

#### Summary Card
```
📊 Signal History for EURUSD=X
Showing last 20 signals per timeframe

┌─────────────────────────────────────────────────────────┐
│ Timeframe | Total | BUY | SELL | Latest | Date         │
├─────────────────────────────────────────────────────────┤
│ 15M       │   18  │  12 │   6  │  BUY   │ 2025-11-16  │
│ 1H        │   20  │  13 │   7  │  SELL  │ 2025-11-16  │
│ 4H        │   20  │  15 │   5  │  BUY   │ 2025-11-16  │
│ 1D        │   20  │  14 │   6  │  BUY   │ 2025-11-16  │
└─────────────────────────────────────────────────────────┘
```

#### Signal Details Table (per timeframe)
```
1D Timeframe - Showing Last 20 Signals (max 20)

┌────────────────┬────────┬──────────┬────────────┬─────────┬───────────┬─────────────┬──────┬──────────┬─────────┐
│ Date           │ Signal │ Strength │ Confidence │ Entry   │ Stop Loss │ Take Profit │ R:R  │ Trend    │ Price   │
├────────────────┼────────┼──────────┼────────────┼─────────┼───────────┼─────────────┼──────┼──────────┼─────────┤
│ 2025-11-16 ... │ BUY    │ STRONG   │ 72.5%      │ 1.09500 │ 1.09200   │ 1.10000     │ 1:2.5│ BULLISH  │ 1.09500 │
│ 2025-11-16 ... │ SELL   │ V_STRONG │ 85.0%      │ 1.09450 │ 1.09700   │ 1.08900     │ 1:3.2│ BEARISH  │ 1.09450 │
│ 2025-11-15 ... │ BUY    │ MODERATE │ 65.0%      │ 1.09300 │ 1.09000   │ 1.09800     │ 1:1.7│ BULLISH  │ 1.09300 │
│ ... (up to 20 signals total)                                                                                    │
└────────────────┴────────┴──────────┴────────────┴─────────┴───────────┴─────────────┴──────┴──────────┴─────────┘

Metrics: BUY: 14 | SELL: 6 | Strong: 18 | Avg Confidence: 73.2%
```

---

## 🎯 How It Works

### Database Query
```python
# For single timeframe
signals = signals_db.get_signals(
    asset_symbol='EURUSD=X',
    timeframe='1d',
    limit=20,              # ← Last 20 signals
    active_only=True       # Only active (not archived)
)

# For multi-timeframe
signals_by_tf = signals_db.get_signals_by_timeframe(
    asset_symbol='EURUSD=X',
    limit_per_timeframe=20,  # ← Last 20 per timeframe
    active_only=True
)
```

### Sorting
Signals are ordered by `created_at DESC`:
- **Newest signal** = Row 1 (top)
- **20th newest signal** = Row 20 (bottom)
- Older signals not shown (but still in database)

---

## 📊 Complete Display Structure

```
🎯 V2 Recommendations
Filters: Asset Type: Forex Major Pairs | Timeframe: All
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 EURUSD=X
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Signal History for EURUSD=X
Showing last 20 signals per timeframe

Summary Table (counts by timeframe)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tabs: [15M - Last 18 signals] [1H - Last 20 signals] [4H - Last 20 signals] [1D - Last 20 signals]

Inside Each Tab:
┌─────────────────────────────────────────────────┐
│ Showing last 20 signals (max 20 per timeframe) │
├─────────────────────────────────────────────────┤
│                                                 │
│  Signal Details Table                          │
│  (Date, Signal, Strength, Entry, SL, TP, etc.)│
│  Rows 1-20 (newest to oldest)                  │
│                                                 │
│  Metrics: BUY, SELL, Strong, Avg Confidence    │
│                                                 │
│  📋 View Latest Recommendation Details         │
│  (Expandable - shows full trade plan)          │
│                                                 │
└─────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 GBPUSD=X
(Same structure repeated for each selected asset)
```

---

## 🔢 Signal Count Examples

### Example 1: Less Than 20 Signals
```
Asset: New analysis, only 5 signals generated
Display: Shows all 5 signals
Label: "Showing Last 5 Signals (max 20)"
```

### Example 2: Exactly 20 Signals
```
Asset: Has exactly 20 signals
Display: Shows all 20 signals
Label: "Showing Last 20 Signals (max 20)"
```

### Example 3: More Than 20 Signals
```
Asset: Has 50 signals in database
Display: Shows newest 20 signals only
Label: "Showing Last 20 Signals (max 20)"
Note: Signals 21-50 are in database but not displayed
```

---

## 📅 Data Retention

### Active Signals (Displayed)
- **Age**: Last 7 days
- **Status**: `is_active = 1`
- **Displayed**: YES (in V2 Recommendations)
- **Count**: Up to 20 per timeframe

### Archived Signals (Not Displayed by Default)
- **Age**: 8-30 days old
- **Status**: `is_active = 0`
- **Displayed**: NO (unless you change `active_only=False`)
- **Purpose**: Historical record

### Deleted Signals
- **Age**: Older than 30 days
- **Status**: Permanently deleted
- **Displayed**: NO (no longer in database)

---

## 🎨 Visual Indicators

### Table Header
```
15M - Last 18 signals
1H - Last 20 signals  ← At maximum (20 signals shown)
4H - Last 15 signals
1D - Last 20 signals  ← At maximum (20 signals shown)
```

### Caption
```
Showing last 12 signals (max 20 per timeframe)
```
This tells you:
- **12 signals** are currently displayed
- **Maximum 20** can be displayed per timeframe

---

## 📊 What Each Column Shows

| Column | Description | Example |
|--------|-------------|---------|
| **Date** | When signal was generated | 2025-11-16 10:30 |
| **Signal** | BUY or SELL | BUY (green) |
| **Strength** | Signal quality | STRONG |
| **Confidence** | Percentage confidence | 72.5% |
| **Entry** | Primary entry price | 1.09500 |
| **Stop Loss** | Standard stop loss | 1.09200 |
| **Take Profit** | Conservative target | 1.10000 |
| **R:R** | Risk:Reward ratio | 1:2.5 |
| **Trend** | Market trend | BULLISH |
| **Price** | Market price at signal time | 1.09500 |

---

## 🔍 How to View All Signals

### View Last 20 (Default)
```
V2 Recommendations → Select asset
Shows: Last 20 signals per timeframe
```

### View Archived Signals (Advanced)
If you want to see older signals (8-30 days old):

```python
# Modify in code
signals_db.get_signals(
    asset_symbol='EURUSD=X',
    timeframe='1d',
    limit=20,
    active_only=False  # ← Shows archived too
)
```

### View More Than 20 (Advanced)
If you want to see more than 20:

```python
# Modify in code
signals_db.get_signals(
    asset_symbol='EURUSD=X',
    timeframe='1d',
    limit=50,  # ← Show 50 instead of 20
    active_only=True
)
```

---

## ⚡ Quick Reference

| Question | Answer |
|----------|--------|
| **How many signals shown?** | Last 20 per timeframe |
| **Sorted how?** | Newest first (top) |
| **Which signals?** | Active signals (last 7 days) |
| **Per asset?** | Yes, 20 per asset per timeframe |
| **Per timeframe?** | Yes, separate 20 for each timeframe |
| **Can I see more?** | Yes, modify `limit` parameter in code |
| **Where are older signals?** | Archived (8-30 days) or deleted (>30 days) |

---

## 📝 Summary

✅ **Last 20 Signals**: Maximum 20 most recent signals per timeframe
✅ **Clear Labeling**: Shows "Last X signals (max 20)" everywhere
✅ **Filtered by Sidebar**: Respects asset type and timeframe selections
✅ **Newest First**: Sorted with most recent at top
✅ **Complete Details**: All trade plan info in expandable view
✅ **Active Only**: Shows signals from last 7 days by default

**The signal history table is now fully functional and displays the last 20 signals for each asset/timeframe combination!** 📊
