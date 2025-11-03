# Forex Analyzer - GUI Guide

## 🎨 Professional Web-Based Interface

The Forex Analyzer now includes a beautiful, professional web-based GUI built with Streamlit!

### ✨ Features

- **📈 Interactive Charts** - Candlestick charts with technical indicators
- **🎯 Multi-Timeframe Dashboard** - View all timeframes at once
- **💼 Trade Plan Visualization** - Visual representation of entry, stop loss, and take profit
- **📊 Multi-Pair Scanner** - Scan multiple assets simultaneously
- **🤖 ML Model Training** - Train models directly from the interface
- **📱 Responsive Design** - Works on desktop, tablet, and mobile

---

## 🚀 Quick Start

### Launch the GUI

**On macOS/Linux:**
```bash
./run_gui.sh
```

**On Windows:**
```bash
run_gui.bat
```

**Or manually:**
```bash
streamlit run app.py
```

The GUI will automatically open in your default web browser at `http://localhost:8501`

---

## 📖 User Interface Guide

### Main Page - Single Asset Analysis

#### 1. Select Your Asset

In the sidebar, choose:
- **Forex Pairs**: EURUSD, GBPUSD, USDJPY, etc.
- **Precious Metals**: Gold (GC=F), Silver (SI=F)
- **Custom**: Enter any symbol

#### 2. Configure Analysis

- **Use ML Model**: Toggle machine learning predictions on/off
- **Account Balance**: Set your trading account size for position calculations

#### 3. Analyze

Click the **🔍 Analyze** button to start the analysis.

#### 4. View Results

Results are organized in tabs:

**📈 Charts Tab**
- Interactive candlestick charts
- Moving averages (20, 50)
- Bollinger Bands
- Volume bars
- RSI indicator
- Zoom, pan, and hover for details

**📋 Trade Plan Tab**
- Entry price
- Stop loss level (ATR-based)
- Take profit target
- Position size in lots
- Risk amount in dollars
- Potential profit/loss
- Risk:reward ratio
- Visual level chart

**🎯 Multi-Timeframe Tab**
- Summary of all timeframes (1D, 4H, 1H, 15M)
- Individual timeframe breakdowns
- Trend strength and momentum
- Individual indicator signals
- Support and resistance levels

**📊 Technical Details Tab**
- Current indicator values
- Recent price action table
- Detailed metrics

---

### Scanner Page - Multi-Asset Scanning

Navigate to **📊 Scanner** in the sidebar.

#### 1. Select Symbols

Choose from presets:
- **Forex Major Pairs**: EURUSD, GBPUSD, USDJPY, AUDUSD
- **Precious Metals**: Gold, Silver
- **All Assets**: Everything
- **Custom**: Pick individual symbols

#### 2. Configure & Scan

- Set account balance
- Toggle ML predictions
- Click **🔍 Scan All**

#### 3. Review Results

**Overview Tab**
- Complete table of all scanned symbols
- Color-coded signals (Green=BUY, Red=SELL, Yellow=HOLD)
- Sortable columns

**BUY Signals Tab**
- Only BUY opportunities
- Sorted by confidence
- Expandable details for each

**SELL Signals Tab**
- Only SELL opportunities
- Sorted by confidence
- Expandable details for each

---

### Training Page - ML Model Training

Navigate to **🤖 Training** in the sidebar.

#### 1. Select Symbol

Choose the asset to train on:
- Forex pairs (EURUSD recommended for best data)
- Precious metals (GC=F, SI=F)

#### 2. Configure

- Model save path (default: `models/forex_model.pkl`)
- Parameters use config defaults

#### 3. Train

Click **🚀 Start Training**

Training process:
1. Fetches historical data
2. Calculates indicators
3. Prepares features
4. Trains ensemble model
5. Shows accuracy metrics
6. Saves model

#### 4. Review Results

- Training accuracy
- Test accuracy
- Classification report
- Model location

---

## 🎨 Understanding the Interface

### Signal Colors

- 🟢 **Green (BUY)**: Bullish signal, consider long position
- 🔴 **Red (SELL)**: Bearish signal, consider short position
- 🟡 **Yellow (HOLD)**: No clear signal, wait for better opportunity

### Confidence Score

- **> 70%**: Strong signal
- **60-70%**: Moderate signal
- **< 60%**: Weak signal (may be rejected by risk manager)

### Timeframe Agreement

Shows how many timeframes agree on the signal:
- **4/4**: All timeframes agree (strongest)
- **3/4**: Strong consensus
- **2/4**: Mixed signals
- **1/4**: Weak agreement

---

## 💡 Tips for Best Results

### Analysis
1. **Check multiple timeframes**: Look at the Multi-Timeframe tab
2. **Verify on charts**: Visual confirmation is important
3. **Check agreement**: Higher agreement = more reliable
4. **Review trade plan**: Ensure risk:reward makes sense

### Scanning
1. **Use presets first**: Start with Forex Major Pairs or Precious Metals
2. **Sort by confidence**: Focus on highest confidence signals
3. **Check BUY/SELL tabs**: Review filtered opportunities
4. **Expand details**: Click each signal for full trade plan

### Training
1. **Train on main symbol**: Use the pair you trade most
2. **Retrain weekly**: Keep model updated
3. **Use EURUSD for forex**: Best historical data
4. **Be patient**: Training takes 1-5 minutes

---

## 🔧 Advanced Features

### Interactive Charts

- **Zoom**: Click and drag to zoom
- **Pan**: Hold shift and drag to pan
- **Reset**: Double-click to reset view
- **Hover**: See exact values
- **Legend**: Click to hide/show indicators

### Custom Symbols

Enter any symbol that yfinance supports:
- Forex: `XXXYYY=X` format
- Futures: Ends with `=F`
- Stocks: Regular ticker symbols
- ETFs: Regular ticker symbols

### Multiple Analyses

The GUI keeps previous results, so you can:
- Analyze multiple symbols
- Compare different timeframes
- Review historical analyses

---

## 🎯 Common Workflows

### Daily Trading Routine

1. Launch GUI: `./run_gui.sh`
2. Go to Scanner page
3. Select "All Assets"
4. Click "Scan All"
5. Review BUY/SELL tabs
6. Click on promising signals
7. Check charts for confirmation
8. Execute trades on your broker

### Weekly Model Update

1. Go to Training page
2. Select EURUSD=X (or your main pair)
3. Click "Start Training"
4. Wait for completion
5. Model automatically used in future analyses

### Single Pair Deep Dive

1. Main page
2. Select symbol
3. Enable ML
4. Click Analyze
5. Review all 4 tabs:
   - Charts for visual confirmation
   - Trade Plan for exact levels
   - Multi-Timeframe for consensus
   - Technical Details for metrics

---

## 📊 Understanding Charts

### Candlestick Chart
- **Green candle**: Price went up (close > open)
- **Red candle**: Price went down (close < open)
- **Wicks**: High and low of period
- **Body**: Open to close range

### Indicators on Chart
- **Orange line**: 20-period MA
- **Blue line**: 50-period MA
- **Gray bands**: Bollinger Bands
- **Bars below**: Volume
- **Purple line**: RSI (bottom panel)

### Chart Timeframes
- **1D (Daily)**: Long-term trend
- **4H**: Medium-term movement
- **1H**: Short-term trading
- **15M**: Intraday scalping

---

## ⚙️ Configuration

### Changing Settings

Settings are in `config/config.yaml`:
- Timeframe weights
- Indicator parameters
- Risk management rules
- ML model settings

After changing config:
1. Save the file
2. Restart the GUI
3. New settings will be applied

### Account Balance

Set in sidebar for each analysis:
- Affects position sizing
- Determines risk amount
- Calculates lot sizes

---

## 🐛 Troubleshooting

### GUI Won't Start

**Error**: "streamlit: command not found"
```bash
pip install streamlit
```

**Error**: "No module named 'plotly'"
```bash
pip install plotly
```

### Analysis Fails

**Error**: "Failed to fetch data"
- Check internet connection
- Verify symbol format
- Try different symbol

**Error**: "Model not found"
- Train a model first
- Or disable ML predictions

### Charts Not Showing

- Check that plotly is installed
- Try refreshing the page
- Clear browser cache

### Slow Performance

- Reduce number of symbols in scanner
- Close other browser tabs
- Check internet speed
- Consider using fewer timeframes

---

## 🔒 Security Notes

### Local Only

The GUI runs locally on your computer:
- No data sent to external servers
- Your analyses are private
- All processing happens locally

### Network Access

By default, Streamlit only accepts connections from localhost.

To access from other devices on your network:
```bash
streamlit run app.py --server.address=0.0.0.0
```

**Warning**: Only do this on trusted networks!

---

## 📱 Mobile Access

The GUI is responsive and works on mobile devices:

1. Start the GUI on your computer
2. Note the local IP address
3. On mobile browser, visit `http://<your-ip>:8501`
4. Requires devices on same network

---

## 🎓 Learning Resources

### New to Trading?
- Start with single symbol analysis
- Use EURUSD (most liquid)
- Review charts and indicators
- Don't trade real money yet

### Intermediate Traders
- Use the scanner daily
- Train models weekly
- Compare technical vs ML signals
- Track your trades separately

### Advanced Users
- Customize config settings
- Train separate models per symbol
- Use scanner for multi-asset portfolios
- Integrate with broker APIs (external)

---

## 🔄 Updates and Maintenance

### Keep Software Updated

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Pull latest code (if using git)
git pull
```

### Retrain Models

Retrain ML models:
- Weekly for active trading
- Monthly for long-term analysis
- After market regime changes

### Cache Management

Streamlit caches data for performance. To clear:
```bash
# In the GUI, press 'C' then 'Clear cache'
# Or restart the server
```

---

## 📞 Support

### Documentation

- **This guide**: `GUI_GUIDE.md`
- **Main README**: `README.md`
- **Quick Start**: `QUICKSTART.md`
- **API docs**: In source code docstrings

### Issues

- Check troubleshooting section above
- Review console logs for errors
- Verify all dependencies installed
- Try test scripts first

---

## 🎉 Enjoy!

You now have a professional forex and metals trading analysis tool with a beautiful GUI!

**Happy Trading! 📈💰**

---

*Remember: This tool provides analysis only. Always do your own research and never risk more than you can afford to lose.*
