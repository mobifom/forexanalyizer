# GUI Advanced Controls - Quick Start

## 🎯 Yes! You Can Now Adjust Risk Controls Through the GUI!

All risk and signal quality settings are now available directly in the web interface.

---

## 📍 Where to Find Them

### In the Sidebar → Look for "⚙️ Advanced Settings"

```
┌─────────────────────────────────────┐
│ Forex Analyzer Pro                  │
├─────────────────────────────────────┤
│ ⚙️ Settings                          │
│                                      │
│ Symbol Type:                        │
│ ○ Forex Pairs                       │
│ ○ Precious Metals                   │
│                                      │
│ Analysis Options:                   │
│ ☑ Use ML Model                      │
│ Account Balance: $10000             │
│                                      │
│ ┌─ ⚙️ Advanced Settings ──────────┐ │ ← CLICK HERE!
│ │ [Click to expand]               │ │
│ └─────────────────────────────────┘ │
│                                      │
│ [🔍 Analyze]                        │
└─────────────────────────────────────┘
```

---

## 🎚️ What You'll See When Expanded

```
┌─ ⚙️ Advanced Settings ─────────────────────┐
│                                              │
│ Signal Quality Controls                     │
│ Lower values = More signals but lower quality│
│                                              │
│ Min Timeframes Agreement                    │
│ ├─────●─────┤ 2                            │
│ 1  2  3  4                                  │
│                                              │
│ Min Confidence Score                        │
│ ├────────●──┤ 50%                           │
│ 30%      60%      80%                       │
│                                              │
│ ─────────────────────────────────────       │
│                                              │
│ Risk Management                             │
│                                              │
│ Risk Per Trade                              │
│ ├────●───────┤ 2.0%                         │
│ 0.5%      5.0%                              │
│                                              │
│ Stop Loss (ATR Multiplier)                  │
│ ├────●───────┤ 2.0                          │
│ 1.0       4.0                               │
│                                              │
│ Min Risk:Reward Ratio                       │
│ ├────●───────┤ 1:1.5                        │
│ 1:1.0     1:3.0                             │
│                                              │
│ ─────────────────────────────────────       │
│                                              │
│ Indicator Sensitivity                       │
│                                              │
│ RSI Overbought                              │
│ ├────────●──┤ 70                            │
│ 60        80                                │
│                                              │
│ RSI Oversold                                │
│ ├────●──────┤ 30                            │
│ 20        40                                │
│                                              │
│ ─────────────────────────────────────       │
│                                              │
│ Quick Presets                               │
│ ┌────────┐ ┌────────┐ ┌────────┐           │
│ │ 🛡️ Con- │ │ ⚖️ Bal- │ │ 🚀 Agg-│           │
│ │ servat │ │ anced  │ │ ressive│           │
│ │  ive   │ │        │ │        │           │
│ └────────┘ └────────┘ └────────┘           │
│                                              │
└──────────────────────────────────────────────┘
```

---

## ⚡ Quick Actions

### To Get More Trading Signals:

1. **Click** "⚙️ Advanced Settings"
2. **Click** "🚀 Aggressive" button
3. **Click** "🔍 Analyze"

**Done!** You'll now see 2-3x more signals.

---

### To Use Conservative (High Quality) Settings:

1. **Click** "⚙️ Advanced Settings"
2. **Click** "🛡️ Conservative" button
3. **Click** "🔍 Analyze"

**Done!** You'll only see high-confidence signals.

---

### To Manually Fine-Tune:

1. **Click** "⚙️ Advanced Settings"
2. **Drag sliders** to desired values
3. **Click** "🔍 Analyze"

**Changes apply immediately!**

---

## 🎯 Most Common Adjustments

### "I want more opportunities"
```
1. Open Advanced Settings
2. Move "Min Timeframes" slider left to 1
3. Move "Min Confidence" slider left to 40%
4. Analyze
```

### "I want lower risk per trade"
```
1. Open Advanced Settings
2. Move "Risk Per Trade" slider left to 1.0%
3. Analyze
```

### "My stops are too tight"
```
1. Open Advanced Settings
2. Move "Stop Loss" slider right to 2.5 or 3.0
3. Analyze
```

---

## 📊 Available on All Pages

These controls appear on:
- ✅ Main Analysis Page (full controls)
- ✅ Scanner Page (simplified controls)
- ✅ All settings sync automatically

---

## 💡 Pro Tips

1. **Start with presets**: Click Conservative/Balanced/Aggressive to instantly configure all settings

2. **Adjust incrementally**: Move sliders one notch at a time and observe results

3. **Scanner workflow**:
   - Use Aggressive preset on Scanner
   - Get many opportunities
   - Re-analyze interesting signals with Conservative preset for confirmation

4. **Settings are per-session**: They reset when you close the GUI (unless you edit config.yaml to make permanent)

---

## 🚀 Launch Now and Try It!

```bash
# Start the GUI
./run_gui.sh

# Or
streamlit run app.py
```

Then look for **"⚙️ Advanced Settings"** in the sidebar!

---

## 📖 Need More Details?

See **GUI_ADVANCED_CONTROLS.md** for:
- Complete explanation of each control
- Recommended workflows
- Troubleshooting
- Advanced strategies

---

**You now have full control over your trading parameters directly in the web interface! 🎉**

No more editing config files - adjust everything with simple sliders and buttons!
