# GUI Advanced Controls Guide

## ✨ New Feature: Adjust Risk Settings in GUI!

You can now adjust all risk and signal quality settings directly from the GUI without editing config files!

---

## 🎯 How to Access

### Main Analysis Page
1. Launch GUI: `./run_gui.sh` or `streamlit run app.py`
2. In the sidebar, look for **"⚙️ Advanced Settings"**
3. Click to expand the settings panel

### Scanner Page
1. Navigate to **"📊 Scanner"** in the sidebar
2. Look for **"⚙️ Advanced Settings"** section
3. Adjust settings before scanning

---

## 🎚️ Available Controls

### 1. Signal Quality Controls

#### **Min Timeframes Agreement** (1-4)
- **What it does**: How many timeframes must agree for a signal
- **Values**:
  - `1` = 25% agreement (Very Aggressive - accepts single timeframe)
  - `2` = 50% agreement (Balanced - default)
  - `3` = 75% agreement (Conservative)
  - `4` = 100% agreement (Very Conservative - all must agree)
- **Impact**: Lower = More signals, Higher = Fewer but higher quality

#### **Min Confidence Score** (30%-80%)
- **What it does**: Minimum confidence to accept a signal
- **Values**:
  - `30-40%` = Very Aggressive (many signals, lower quality)
  - `50%` = Balanced (default)
  - `60%` = Conservative (fewer signals, higher quality)
  - `70-80%` = Very Conservative (very few signals)
- **Impact**: Lower = More opportunities, Higher = Better quality

---

### 2. Risk Management Controls

#### **Risk Per Trade** (0.5%-5.0%)
- **What it does**: Percentage of your account to risk per trade
- **Recommended**:
  - `1.0%` = Conservative (recommended for beginners)
  - `2.0%` = Moderate (default)
  - `3.0%` = Aggressive
  - `5.0%` = Very Aggressive (high risk!)
- **Impact**: Higher = Larger position sizes, more profit/loss potential

#### **Stop Loss (ATR Multiplier)** (1.0-4.0)
- **What it does**: How far to place stop loss from entry
- **Values**:
  - `1.0-1.5` = Tight stop loss (gets stopped out more often)
  - `2.0` = Standard (default)
  - `2.5-3.0` = Wide stop loss (more breathing room)
  - `4.0` = Very wide (rarely gets stopped)
- **Impact**: Lower = More trades stopped out, Higher = Fewer stops but larger risk

#### **Min Risk:Reward Ratio** (1:1.0 to 1:3.0)
- **What it does**: Minimum profit target relative to risk
- **Values**:
  - `1:1.0` = Aggressive (accept equal risk/reward)
  - `1:1.5` = Moderate (default)
  - `1:2.0` = Conservative (require 2x reward)
  - `1:3.0` = Very Conservative (require 3x reward)
- **Impact**: Lower = More trade opportunities, Higher = Better risk/reward

---

### 3. Indicator Sensitivity

#### **RSI Overbought** (60-80)
- **What it does**: When RSI is "overbought" (bearish signal)
- **Values**:
  - `60-65` = More sensitive (triggers earlier/more often)
  - `70` = Standard (default)
  - `75-80` = Less sensitive (triggers later/less often)

#### **RSI Oversold** (20-40)
- **What it does**: When RSI is "oversold" (bullish signal)
- **Values**:
  - `35-40` = More sensitive (triggers earlier/more often)
  - `30` = Standard (default)
  - `20-25` = Less sensitive (triggers later/less often)

---

## 🚀 Quick Presets

Click one of these buttons for instant configuration:

### 🛡️ **Conservative Preset**
```
Min Timeframes: 3 (75%)
Min Confidence: 60%
Risk Per Trade: 1%
Stop Loss: 2.5x ATR
Risk:Reward: 1:2.0
RSI: Standard (70/30)
```
**Best for**: New traders, risk-averse investors
**Expected**: 10-20% of scans show signals, high win rate

### ⚖️ **Balanced Preset** (Default)
```
Min Timeframes: 2 (50%)
Min Confidence: 50%
Risk Per Trade: 2%
Stop Loss: 2.0x ATR
Risk:Reward: 1:1.5
RSI: Standard (70/30)
```
**Best for**: Most traders, balanced approach
**Expected**: 30-40% of scans show signals, good win rate

### 🚀 **Aggressive Preset**
```
Min Timeframes: 1 (25%)
Min Confidence: 40%
Risk Per Trade: 3%
Stop Loss: 1.5x ATR
Risk:Reward: 1:1.2
RSI: Sensitive (65/35)
```
**Best for**: Experienced traders, active trading
**Expected**: 60-70% of scans show signals, moderate win rate

---

## 📊 Real-Time Updates

All changes take effect **immediately**:
1. Adjust sliders
2. Click "🔍 Analyze" or "🔍 Scan All"
3. See results with new settings

No need to restart the GUI or save files!

---

## 💡 Usage Examples

### Example 1: Get More Trading Opportunities

**Goal**: I want more signals, willing to accept slightly lower quality

**Steps**:
1. Open "⚙️ Advanced Settings"
2. Move "Min Timeframes Agreement" to **1**
3. Move "Min Confidence Score" to **40%**
4. Or just click **"🚀 Aggressive"** preset
5. Click "🔍 Analyze"

**Result**: 2-3x more BUY/SELL signals, fewer HOLD signals

---

### Example 2: Reduce Risk Per Trade

**Goal**: I want to risk less per trade (safer)

**Steps**:
1. Open "⚙️ Advanced Settings"
2. Move "Risk Per Trade" to **1.0%**
3. Move "Min Risk:Reward" to **1:2.0**
4. Keep other settings as default
5. Analyze normally

**Result**: Smaller position sizes, require better risk:reward

---

### Example 3: More Sensitive RSI Signals

**Goal**: Catch trends earlier with RSI

**Steps**:
1. Open "⚙️ Advanced Settings"
2. Move "RSI Overbought" to **65**
3. Move "RSI Oversold" to **35**
4. Keep timeframes at **2**
5. Keep confidence at **50%**
6. Analyze

**Result**: RSI triggers earlier, more RSI-based signals

---

### Example 4: Conservative High-Quality Signals Only

**Goal**: Only show me the best, highest confidence signals

**Steps**:
1. Open "⚙️ Advanced Settings"
2. Click **"🛡️ Conservative"** preset
3. Or manually set:
   - Min Timeframes: **3**
   - Min Confidence: **60%**
   - Risk Per Trade: **1%**
4. Run scanner

**Result**: Very few signals but very high quality

---

## 🎯 Finding Your Sweet Spot

### Testing Different Settings

1. **Start with Balanced** preset
2. **Run scanner** on all assets
3. **Check results**:
   - Too many HOLD? → Lower thresholds (more aggressive)
   - Too many low-confidence signals? → Raise thresholds (more conservative)
4. **Adjust incrementally**:
   - Change one setting at a time
   - Test and observe results
   - Find what works for your style

### Monitor Win Rate

Track which settings give you best results:
- **Conservative**: Expect 60-70% win rate, fewer trades
- **Balanced**: Expect 50-60% win rate, moderate trades
- **Aggressive**: Expect 40-50% win rate, many trades

---

## ⚠️ Important Notes

### Settings Are Temporary

- GUI settings are **per-session only**
- When you close GUI, settings reset to config.yaml defaults
- To make permanent: Edit `config/config.yaml` directly

### Settings Affect All Analyses

- Changes apply to current session
- Both main analysis and scanner use same settings
- Adjust before each analysis if needed

### Visual Feedback

- Sliders show current values in real-time
- Preset buttons provide instant configuration
- Changes take effect on next analysis

---

## 📈 Recommended Workflows

### Daily Trading Routine

```
1. Launch GUI
2. Click "🚀 Aggressive" preset
3. Go to Scanner page
4. Scan all assets
5. Review signals (expect 5-10 opportunities)
6. For interesting signals:
   - Switch back to main page
   - Click "🛡️ Conservative" preset
   - Re-analyze specific pair for confirmation
7. If still shows signal with conservative settings → High confidence trade!
```

### Conservative Long-Term Trading

```
1. Launch GUI
2. Click "🛡️ Conservative" preset
3. Scan all assets weekly
4. Only trade signals with:
   - 60%+ confidence
   - 3+ timeframes agreeing
   - Good risk:reward (1:2+)
5. Expect 1-2 trades per week max
```

### Active Intraday Trading

```
1. Launch GUI
2. Click "🚀 Aggressive" preset
3. Further adjust:
   - RSI Overbought: 65
   - RSI Oversold: 35
4. Scan every 1-2 hours
5. Take signals with:
   - 40%+ confidence
   - 1+ timeframe
6. Use tight stops (1.5x ATR)
7. Expect multiple trades per day
```

---

## 🔧 Troubleshooting

### "Still getting all HOLD signals even on aggressive"

**Solution**:
1. Make sure you clicked the preset button
2. Check sliders moved to new values
3. Try even more aggressive:
   - Min Timeframes: **1**
   - Min Confidence: **35%**
4. Market may genuinely be consolidating (this is realistic)

### "Getting too many conflicting signals"

**Solution**:
1. Increase "Min Timeframes Agreement" to **2** or **3**
2. This filters out pairs with timeframe conflicts

### "Position sizes too large/small"

**Solution**:
1. Adjust "Risk Per Trade" slider
2. Or change "Account Balance" value
3. Position size = Risk Amount ÷ Stop Loss Distance

### "Stops too tight, always getting stopped out"

**Solution**:
1. Increase "Stop Loss (ATR Multiplier)" to **2.5** or **3.0**
2. This gives trades more breathing room

---

## 📚 Summary

✅ **All settings now adjustable in GUI**
✅ **No need to edit config files**
✅ **Three quick presets available**
✅ **Changes take effect immediately**
✅ **Works on both main page and scanner**

### Quick Reference:

| Want More Signals? | Lower These |
|-------------------|-------------|
| Min Timeframes | 3 → 2 → 1 |
| Min Confidence | 60% → 50% → 40% |

| Want Better Quality? | Raise These |
|---------------------|-------------|
| Min Timeframes | 1 → 2 → 3 |
| Min Confidence | 40% → 50% → 60% |

| Want Lower Risk? | Adjust These |
|-----------------|-------------|
| Risk Per Trade | 2% → 1% |
| Min Risk:Reward | 1:1.5 → 1:2.0 |

---

**Now you have full control over your trading strategy directly from the GUI! 🎉**
