# 📈 Forex Analyzer Pro

A comprehensive forex and precious metals trading analysis tool powered by machine learning and multi-timeframe technical analysis.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

## 🌟 Features

### Real-Time Data Integration
- ✅ **Twelve Data API** - Real-time forex data (FREE tier supported)
- ✅ **Yahoo Finance** - Backup data source
- ✅ **Oanda API** - Professional forex data (optional)
- ✅ **10-minute smart caching** - Balance between freshness and API limits

### Multi-Timeframe Analysis
- 📊 **4 Timeframes**: 15m, 1h, 4h, 1d
- 🎯 **Timeframe Consensus** - Identify high-confidence trades
- 📈 **Enhanced Recommendations** - Multi-entry and multi-target strategies
- ⚖️ **Confluence Scoring** - Weight signals by timeframe importance

### Technical Indicators
- Moving Averages (MA 20, 50, 200)
- Exponential Moving Averages (EMA 12, 26, 50)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Stochastic Oscillator
- Bollinger Bands
- ATR (Average True Range)
- Support & Resistance Levels

### Machine Learning
- 🤖 **Random Forest Classifier** - Price direction prediction
- 📚 **Ensemble Voting** - Combines ML + Technical signals
- 🎓 **Model Training** - Train on historical data
- 💾 **Model Persistence** - Save and load trained models

### Risk Management
- 💰 **Position Sizing** - Based on ATR and account balance
- 🛑 **Dynamic Stop Loss** - Multiple options (1-3x ATR, 2-3% fixed)
- 🎯 **Multiple Take Profits** - TP1 (Scalp), TP2 (Conservative), TP3 (Moderate), TP4 (Aggressive)
- ⚖️ **Risk:Reward Ratio** - Configurable minimum R:R
- 📊 **Multi-Entry Points** - NOW, Pullback, Best entry strategies

### Professional UI
- 🎨 **Streamlit Dashboard** - Beautiful web interface
- 📊 **Interactive Charts** - Plotly candlestick charts with annotations
- 🔄 **Real-Time Updates** - Manual refresh for latest data
- 📱 **Responsive Design** - Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites

```bash
python 3.8+
pip
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ForexAnalyzer.git
cd ForexAnalyzer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Get FREE API Key (Optional but Recommended)**

Get a free Twelve Data API key for real-time forex data:
- Sign up at: https://twelvedata.com/pricing
- Copy your API key from the dashboard
- See [GET_FREE_API_KEY.md](GET_FREE_API_KEY.md) for detailed instructions

4. **Configure API Key**

Edit `config/config.yaml`:
```yaml
twelvedata:
  enabled: true
  api_key: 'YOUR_API_KEY_HERE'
```

5. **Run the app**
```bash
streamlit run app.py
```

6. **Open your browser**
```
http://localhost:8501
```

## 📖 Documentation

### Core Documentation
- [GET_FREE_API_KEY.md](GET_FREE_API_KEY.md) - How to get free real-time forex API
- [WHY_SIGNALS_DIFFER.md](WHY_SIGNALS_DIFFER.md) - Understanding multi-timeframe signals
- [GOLD_PRICE_FIX.md](GOLD_PRICE_FIX.md) - Cache and data freshness explained

### Technical Improvements
- [CHART_ANNOTATION_FIX.md](CHART_ANNOTATION_FIX.md) - Chart annotation improvements
- [COLOR_IMPROVEMENTS.md](COLOR_IMPROVEMENTS.md) - High-contrast color scheme
- [OVERLAP_FIX.md](OVERLAP_FIX.md) - Annotation overlap prevention
- [ANNOTATION_IMPROVEMENTS.md](ANNOTATION_IMPROVEMENTS.md) - Complete annotation guide

## 🎯 Usage

### Basic Analysis

1. **Select a symbol** (EUR/USD, Gold, etc.)
2. **Configure settings** (account balance, risk tolerance)
3. **Click "🔍 Analyze"**
4. **Review signals and trade plan**

### Multi-Pair Scanning

1. Go to **"📊 Scanner"** page
2. Select pairs to scan
3. Choose timeframe mode
4. Click **"Scan Pairs"**
5. View heatmap and detailed signals

### Model Training

1. Go to **"🤖 Training"** page
2. Select forex pair
3. Click **"Train Model"**
4. Review accuracy metrics
5. Model auto-saves to `models/`

## ⚙️ Configuration

### Main Config File: `config/config.yaml`

```yaml
# Timeframes to analyze
timeframes:
  - '1d'
  - '4h'
  - '1h'
  - '15m'

# Risk Management
risk_management:
  risk_per_trade: 0.02        # 2% of account
  atr_multiplier: 2.0         # Stop loss distance
  min_risk_reward: 1.5        # Minimum 1:1.5 R:R

# Data Settings
data:
  cache_duration_minutes: 10  # Auto-refresh interval
  data_source: 'auto'         # Twelve Data → Oanda → Yahoo

# Twelve Data API
twelvedata:
  enabled: true
  api_key: 'YOUR_KEY_HERE'
```

### Trading Presets

**Conservative** (Low risk, high accuracy):
- Min timeframes agree: 3/4 (75%)
- Min confidence: 60%
- Risk per trade: 1%
- R:R ratio: 2.0

**Balanced** (Default):
- Min timeframes agree: 2/4 (50%)
- Min confidence: 50%
- Risk per trade: 2%
- R:R ratio: 1.5

**Aggressive** (High frequency):
- Min timeframes agree: 1/4 (25%)
- Min confidence: 40%
- Risk per trade: 3%
- R:R ratio: 1.2

## 📊 Supported Pairs

### Forex
- EUR/USD, GBP/USD, USD/JPY
- AUD/USD, NZD/USD, USD/CAD
- EUR/JPY, GBP/JPY, EUR/GBP
- All major forex pairs

### Precious Metals
- Gold (XAU/USD)
- Silver (XAG/USD) - Requires Twelve Data Grow plan

## 🔧 Troubleshooting

### Issue: "No data available"
**Solution**: Check internet connection or API key

### Issue: "Signals differ across timeframes"
**Solution**: This is normal! See [WHY_SIGNALS_DIFFER.md](WHY_SIGNALS_DIFFER.md)

### Issue: "Cache shows old prices"
**Solution**: Click "🔄 Refresh Latest Data" button

### Issue: "API rate limit exceeded"
**Solution**: Wait 1 minute or increase cache duration

## 🧪 Diagnostic Tools

### Signal Diagnosis
```bash
python diagnose_signals.py EURUSD=X
```

Shows:
- Exact candle times
- Current indicator values
- Why signals were generated
- Cache age

### Test API Connection
```bash
python test_twelvedata.py
```

Tests:
- API key validity
- Data retrieval
- Gold/Silver support

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

**This software is for educational purposes only.**

- Not financial advice
- Trading carries risk of loss
- Past performance doesn't guarantee future results
- Always do your own research
- Never risk more than you can afford to lose

## 🙏 Acknowledgments

- **Twelve Data** - Real-time forex API
- **Streamlit** - Beautiful web framework
- **Plotly** - Interactive charts
- **scikit-learn** - Machine learning
- **yfinance** - Backup data source

## 📧 Contact

For questions or issues, please open a GitHub issue.

## 🗺️ Roadmap

- [ ] Add more ML models (LSTM, XGBoost)
- [ ] Implement backtesting engine
- [ ] Add portfolio management
- [ ] Create mobile app
- [ ] Add cryptocurrency support
- [ ] Implement automated trading (with user approval)

---

**Made with ❤️ for forex traders**

⭐ Star this repo if you find it useful!
