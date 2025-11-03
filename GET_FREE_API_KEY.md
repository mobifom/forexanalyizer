# Get FREE Real-Time Forex API Key

## ❌ Finnhub Issue

**Unfortunately, Finnhub's free tier does NOT support forex data** - it only works for US stocks. Forex requires their premium plan ($99/month).

## ✅ Solution: Twelve Data (FREE Forex Support!)

**Twelve Data offers TRUE FREE forex data** including gold and silver!

### Free Tier Includes:
- ✅ **8 API calls per minute**
- ✅ **800 API calls per day**
- ✅ **Real-time** forex data
- ✅ **OHLC candlestick** data
- ✅ **140+ currencies** including EUR/USD, GBP/USD, etc.
- ✅ **Gold (XAU/USD)** ✨
- ✅ **Silver (XAG/USD)** ✨
- ✅ Multiple timeframes (1min to 1 month)
- ✅ **NO credit card required!**

---

## 🚀 Get Your FREE API Key (2 Minutes)

### Step 1: Sign Up

1. Go to: **https://twelvedata.com/pricing**
2. Click **"Get Free API Key"** (Basic plan - $0/month)
3. Fill in:
   - Email address
   - Password
   - Your name
4. Click **"Sign Up"**

### Step 2: Get Your API Key

1. **Check your email** for verification link
2. Click the verification link
3. **Log in** to your dashboard
4. Your API key will be displayed immediately!
   - Format: `abc123def456ghi789...` (32 characters)
5. **Copy** your API key

### Step 3: Configure ForexAnalyzer

**Option A: Edit Config File**

1. Open `config/config.yaml`
2. Find the `twelvedata` section
3. Update it:

```yaml
# Twelve Data API Settings (FREE - Supports Forex!)
twelvedata:
  enabled: true              # ⬅️ Change to true
  api_key: 'YOUR_API_KEY_HERE'  # ⬅️ Paste your key here
```

4. Set data source to auto:

```yaml
data:
  data_source: 'auto'  # Will use Twelve Data first
```

**Option B: Environment Variable**

```bash
# Linux/Mac
export TWELVEDATA_API_KEY='your_key_here'

# Windows
set TWELVEDATA_API_KEY=your_key_here
```

### Step 4: Run the App

```bash
streamlit run app.py
```

You should see:
```
✅ Twelve Data API initialized - Real-time forex data available!
📊 Active data source: Auto (Twelve Data (real-time) → yfinance (fallback))
```

---

## 📊 What Works with Free Tier

### ✅ Supported Symbols

**Forex Pairs:**
- EUR/USD, GBP/USD, USD/JPY
- AUD/USD, NZD/USD, USD/CAD
- EUR/JPY, GBP/JPY, EUR/GBP
- All major forex pairs!

**Precious Metals:**
- XAU/USD (Gold) ✨
- XAG/USD (Silver) ✨

**Timeframes:**
- 1min, 5min, 15min, 30min
- 1h, 2h, 4h
- 1day, 1week, 1month

---

## 💡 API Rate Limits

### Free Tier Limits:
- **8 calls per minute**
- **800 calls per day**

### How ForexAnalyzer Uses It:
- Analyzing 1 pair across 4 timeframes = **4 API calls**
- Scanning 6 pairs × 4 timeframes = **24 API calls**
- With 8 calls/min, you can do **2 pairs at a time**

**Tip:** Use cache to reduce API calls:
```yaml
data:
  cache_duration_minutes: 10  # Cache for 10 minutes
```

---

## 🔧 Troubleshooting

### "Rate limit exceeded"

You've hit 8 calls/minute:
- **Wait 1 minute** before next scan
- **Increase cache duration** (15-30 minutes)
- **Scan fewer pairs** at once

### "API key invalid"

- Check for typos in API key
- Make sure no extra spaces
- Verify email first (check spam folder)

### "No data available"

- Symbol might be wrong format
- Try: `EUR/USD` not `EURUSD`
- Check if pair is supported

---

## 💰 Upgrade Options (Optional)

If you need more than 8 calls/min:

**Grow Plan - $29/month:**
- 55 API calls/minute
- Unlimited daily calls
- Real-time updates

**Pro Plan - $79/month:**
- 145 API calls/minute
- Unlimited everything

Most users are fine with free tier!

---

## 🆚 Comparison

| Feature | Yahoo Finance | Twelve Data FREE |
|---------|---------------|------------------|
| Forex Data | Delayed ~15 min | ✅ Real-time |
| Gold/Silver | Delayed | ✅ Real-time |
| API Limit | None | 8/min, 800/day |
| Cost | Free | Free |
| Best For | Backup | **Primary** |

---

## ✅ Quick Summary

1. **Sign up**: https://twelvedata.com/pricing
2. **Get free API key** from dashboard
3. **Add to config.yaml** in `twelvedata` section
4. **Set `enabled: true`**
5. **Run**: `streamlit run app.py`

**That's it!** Real-time forex data for FREE! 🎉

---

## 🔗 Useful Links

- **Sign Up**: https://twelvedata.com/pricing
- **Documentation**: https://twelvedata.com/docs
- **Supported Symbols**: https://twelvedata.com/symbol-lists/forex
- **API Status**: https://status.twelvedata.com/

---

**Get your free API key now!** ⬇️
👉 https://twelvedata.com/pricing
