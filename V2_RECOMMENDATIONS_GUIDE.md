# 🎯 V2 Recommendations - Usage Guide

## ✅ Fixed and Enhanced!

The V2 Recommendations section now automatically displays stored analysis data based on your sidebar selections.

---

## 📊 How It Works

### Automatic Display Based on Sidebar Selections

The V2 Recommendations section is **connected to your sidebar selections**:

```
┌─────────────────────────────────────────────────────────┐
│                    SIDEBAR                               │
├─────────────────────────────────────────────────────────┤
│  Quick Select:                                          │
│    ○ Forex Major Pairs                                  │
│    ○ Indices                                            │
│    ○ Crypto                                             │
│    ○ Precious Metals                                    │
│    ○ All Assets                                         │
│    ● Custom                                             │
│                                                         │
│  💱 Forex:                                              │
│    ☑ EURUSD=X                                          │
│    ☑ GBPUSD=X                                          │
│    ☐ USDJPY=X                                          │
│                                                         │
│  🥇 Metals:                                            │
│    ☑ XAU_USD                                           │
│    ☐ XAG_USD                                           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│            🎯 V2 RECOMMENDATIONS                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📈 EURUSD=X                                           │
│  ├─ Summary: 3 timeframes, 12 recommendations          │
│  └─ Tabs: [15M] [1H] [4H] [1D]                        │
│                                                         │
│  📈 GBPUSD=X                                           │
│  ├─ Summary: 2 timeframes, 8 recommendations           │
│  └─ Tabs: [1H] [4H]                                   │
│                                                         │
│  📈 XAU_USD                                            │
│  ├─ Summary: 4 timeframes, 15 recommendations          │
│  └─ Tabs: [15M] [1H] [4H] [1D]                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Two Display Modes

### Mode 1: Sidebar Selection Active ✓

**When you select assets from the sidebar:**
- ✅ Only shows recommendations for **selected assets**
- ✅ Updates automatically when you change selections
- ✅ Displays all stored data for those assets

**Example:**
```
Sidebar: Select "Forex Major Pairs"
  → Selected: EURUSD=X, GBPUSD=X, USDJPY=X, AUDUSD=X

V2 Recommendations displays:
  📈 EURUSD=X (with all its recommendations)
  📈 GBPUSD=X (with all its recommendations)
  📈 USDJPY=X (with all its recommendations)
  📈 AUDUSD=X (with all its recommendations)
```

### Mode 2: Auto-Display All Stored Data ✓

**When NO assets are selected from sidebar:**
- ✅ Automatically finds **all assets with stored data**
- ✅ Displays recommendations for all of them
- ✅ Shows you everything that's available

**Example:**
```
Sidebar: No selection (or "Custom" with no checkboxes)

V2 Recommendations displays:
  💡 Select assets from the sidebar, or view all assets with stored recommendations below

  📈 EURUSD=X (has stored data - displayed)
  📈 XAU_USD (has stored data - displayed)
  📈 US30 (has stored data - displayed)
  (Other assets without data are skipped)
```

---

## 📋 What's Displayed for Each Asset

For every selected or available asset, you see:

### 1. **Summary Card**
```
📊 Recommendations Summary for EURUSD=X

Timeframe | Total Recommendations | BUY | SELL | Latest | Date
--------------------------------------------------------------
15M       | 5                     | 3   | 2    | BUY    | 2025-11-16
1H        | 8                     | 5   | 3    | SELL   | 2025-11-16
4H        | 12                    | 8   | 4    | BUY    | 2025-11-16
1D        | 15                    | 10  | 5    | BUY    | 2025-11-16
```

### 2. **Timeframe Tabs**

Click on any timeframe tab to see:

#### Recommendations Table
| Date | Signal | Strength | Confidence | Entry | Stop Loss | Take Profit | R:R | Trend | Price |
|------|--------|----------|------------|-------|-----------|-------------|-----|-------|-------|
| 2025-11-16 10:30 | BUY | STRONG | 72.5% | 1.09500 | 1.09200 | 1.10000 | 1:2.5 | BULLISH | 1.09500 |
| 2025-11-16 08:15 | SELL | VERY_STRONG | 85.0% | 1.09450 | 1.09700 | 1.08900 | 1:3.2 | BEARISH | 1.09450 |

#### Summary Metrics
- **BUY**: Count of BUY recommendations
- **SELL**: Count of SELL recommendations
- **Strong**: Count of STRONG/VERY_STRONG recommendations
- **Avg Confidence**: Average confidence across all recommendations

### 3. **Detailed View (Expandable)**

Click "📋 View Latest Recommendation Details" to see:

```
Recommendation Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type: 🟢 BUY              Confidence: 72.5%        Date: 2025-11-16 10:30
Strength: STRONG          Timeframe: 1D            Price: 1.09500

📍 Entry Points
├─ Entry 1 (Immediate):  1.09500
├─ Entry 2 (Pullback):   1.09300
└─ Entry 3 (Aggressive): 1.09600

🎯 Take Profit Levels          🛡️ Stop Loss Levels
├─ TP1 (Quick):      1.09800   ├─ SL Tight (1 ATR):    1.09350
├─ TP2 (Conservative): 1.10000   ├─ SL Standard (2 ATR): 1.09200
└─ TP3 (Extended):   1.10500   └─ SL Wide (3 ATR):     1.09000

📊 Risk Metrics               🔍 Market Context
├─ Risk:Reward: 1:2.5        ├─ Trend: BULLISH
└─ Risk %: 1.5%              ├─ Momentum: STRONG
                             └─ ⚠️ No reversals detected
```

---

## 🔄 How to Use

### Scenario 1: View Specific Assets

```bash
1. Open Scanner page
2. Sidebar → Select asset type (e.g., "Forex Major Pairs")
   OR
   Sidebar → Select "Custom" → Check specific assets
3. Scroll down to "🎯 V2 Recommendations"
4. See only your selected assets' recommendations ✓
```

### Scenario 2: View All Stored Data

```bash
1. Open Scanner page
2. Sidebar → Don't select any assets (or use default)
3. Scroll down to "🎯 V2 Recommendations"
4. See ALL assets with stored recommendations ✓
```

### Scenario 3: After Running Analysis

```bash
1. Sidebar → Select assets (e.g., EURUSD=X, GBPUSD=X)
2. Click "🔍 Scan All"
3. Analysis runs and saves to database
4. Scroll down to "🎯 V2 Recommendations"
5. See the freshly generated recommendations ✓
```

---

## 📅 Data Retention

- **Active**: Last 7 days (shown by default)
- **Archived**: Older than 7 days (can be viewed by modifying `active_only` parameter)
- **Deleted**: Older than 30 days (permanently removed)

---

## 🎨 Visual Features

### Color Coding
- 🟢 **BUY signals**: Green background
- 🔴 **SELL signals**: Red background
- 🟡 **HOLD signals**: Yellow background (if any)

### Strength Indicators
- 🟢 **VERY_STRONG** (≥75%): Dark green
- 🟢 **STRONG** (60-74%): Light green
- 🟡 **MODERATE** (45-59%): Yellow
- 🔴 **WEAK** (<45%): Red

---

## ⚡ Quick Tips

1. **Default View**: When page loads, it automatically shows all assets with data
2. **Filter by Selection**: Use sidebar to filter to specific assets
3. **Multiple Assets**: Works with single or multiple asset selections
4. **Live Updates**: Changes sidebar selection → Recommendations update instantly
5. **No Data**: If an asset has no stored recommendations, you'll see an info message

---

## 🐛 Troubleshooting

### "No stored recommendations found"
**Cause**: Database is empty - no analysis has been run yet
**Solution**: Run an analysis via Scanner or Scheduler

### "No recommendations recorded for [asset]"
**Cause**: That specific asset hasn't been analyzed yet
**Solution**:
1. Select that asset in sidebar
2. Click "Scan All" to analyze it
3. Recommendations will appear after analysis

### Sidebar selections not showing
**Cause**: Those assets may not have stored data
**Solution**: Run analysis for those assets first

---

## 📝 Summary

✅ **Connected to Sidebar**: Displays recommendations based on your asset selections
✅ **Auto-Display**: Shows all available data when nothing is selected
✅ **Complete History**: Last 20 recommendations per timeframe
✅ **Detailed Trade Plans**: Entry points, TP, SL, risk metrics
✅ **Easy Navigation**: Tabs for timeframes, expandable details
✅ **Always Up-to-Date**: Shows latest stored analysis data

**The V2 Recommendations section is your complete trading signal history, organized and ready to use!** 🎯
