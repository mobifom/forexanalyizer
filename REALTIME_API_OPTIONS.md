# Real-Time Forex API Options (2025)

Comparison of free/affordable real-time forex APIs to replace Yahoo Finance's delayed data.

## 🏆 Top Recommendations

### 1. **Finnhub** ⭐ BEST FREE OPTION
- **Website**: https://finnhub.io
- **Free Tier**: 60 API calls/minute
- **Real-Time**: ✅ Yes
- **OHLC/Candlestick**: ✅ Yes (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- **Forex Pairs**: ✅ Global FX pairs
- **WebSocket**: ✅ Yes (for streaming)
- **Registration**: Required (free)
- **Best For**: Production use with reasonable limits

**Pros:**
- Generous free tier (60 calls/min)
- Real-time data
- OHLC candlestick support
- WebSocket for streaming
- Good documentation
- Python SDK available

**Cons:**
- Requires API key registration
- Some advanced features require paid plan

**Pricing:**
- Free: 60 calls/min
- Premium: Starting at $59/month (unlimited calls)

---

### 2. **Twelve Data** ⭐ RUNNER UP
- **Website**: https://twelvedata.com
- **Free Tier**: 8 API calls/minute, 800/day
- **Real-Time**: ✅ Yes
- **OHLC/Candlestick**: ✅ Yes (1min to monthly)
- **Forex Pairs**: ✅ 140+ currencies, 2000+ pairs
- **WebSocket**: ✅ Yes
- **Registration**: Required (free)
- **Best For**: Testing and small projects

**Pros:**
- Real-time forex data
- Multiple timeframes (1min to monthly)
- Good free tier for testing
- Excellent documentation
- Python SDK available

**Cons:**
- Lower free tier limits (8/min vs Finnhub's 60/min)
- Daily cap of 800 requests

**Pricing:**
- Free: 8 calls/min, 800/day
- Grow: $29/month (55 calls/min, unlimited daily)
- Pro: $79/month (145 calls/min)

---

### 3. **Polygon.io**
- **Website**: https://polygon.io
- **Free Tier**: Limited (delayed data)
- **Real-Time**: ⚠️ Requires paid plan ($99/month)
- **OHLC/Candlestick**: ✅ Yes
- **Forex Pairs**: ✅ Yes
- **WebSocket**: ✅ Yes
- **Best For**: Professional/Production (if budget allows)

**Pros:**
- Very reliable
- Excellent API quality
- Great documentation
- Production-ready

**Cons:**
- No free real-time data
- Expensive ($99/month minimum)

---

## 📊 Other Options

### 4. **Alpha Vantage**
- **Free Tier**: 25 calls/day
- **Real-Time Forex**: ❌ No (Premium only)
- **OHLC**: ✅ Daily data only (free)
- **Best For**: Historical data only

**Note**: Intraday forex is now premium (paid) feature.

---

### 5. **FCSAPI**
- **Website**: https://fcsapi.com
- **Free Tier**: 500 calls/month
- **Real-Time**: ✅ Yes (1-5 second updates)
- **OHLC**: ✅ Yes
- **Forex Pairs**: ✅ 145+ currencies, 2000+ pairs

**Pros:**
- Very fast updates (1-5 seconds)
- Good forex coverage

**Cons:**
- Very limited free tier (500/month total)
- Expensive paid plans

---

### 6. **FreeForexAPI**
- **Website**: https://www.freeforexapi.com
- **Free Tier**: ✅ Unlimited
- **Real-Time**: ⚠️ Current rates only
- **OHLC**: ❌ No historical/candlestick data
- **Best For**: Simple current rate lookups only

**Note**: Only provides current exchange rates, no historical OHLC data.

---

### 7. **Currencylayer**
- **Free Tier**: 100 requests/month
- **Real-Time**: ✅ Yes
- **OHLC**: ❌ No
- **Best For**: Simple currency conversion

**Note**: No OHLC/candlestick data, just current rates.

---

## 📋 Comparison Table

| API | Free Calls/Min | Free Daily Limit | Real-Time | OHLC | WebSocket | Best For |
|-----|----------------|------------------|-----------|------|-----------|----------|
| **Finnhub** | 60 | Unlimited | ✅ | ✅ | ✅ | **Production** |
| **Twelve Data** | 8 | 800 | ✅ | ✅ | ✅ | Testing/Small |
| **Polygon.io** | N/A | N/A | ❌ (Paid) | ✅ | ✅ | Enterprise |
| **Alpha Vantage** | ~0.02 | 25 | ❌ (Paid) | ⚠️ Daily only | ❌ | Historical |
| **FCSAPI** | ~1 | ~17 | ✅ | ✅ | ❌ | Limited use |
| **FreeForexAPI** | Unlimited | Unlimited | ⚠️ Current | ❌ | ❌ | Rates only |

---

## 🎯 Recommendation for ForexAnalyzer

### Primary Choice: **Finnhub**

**Why Finnhub:**
1. ✅ Best free tier (60 calls/min vs 8 for Twelve Data)
2. ✅ True real-time data
3. ✅ OHLC candlestick support
4. ✅ Multiple timeframes (1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M)
5. ✅ Good documentation
6. ✅ WebSocket support for streaming
7. ✅ Reliable and production-ready

**For ForexAnalyzer needs:**
- Scanning 4-6 pairs across 4 timeframes = ~24 calls per scan
- With 60 calls/min, you can run 2+ full scans per minute
- More than enough for the current use case

### Backup Choice: **Twelve Data**

If Finnhub has any issues, Twelve Data is an excellent fallback:
- Still provides real-time OHLC
- Lower limits but workable (8/min = 1 scan every 3 minutes)
- Very similar API structure

---

## 🚀 Implementation Plan

### Step 1: Get API Keys
1. **Finnhub**: https://finnhub.io/register
   - Sign up for free account
   - Get API key from dashboard

2. **Twelve Data** (backup): https://twelvedata.com/
   - Sign up for free account
   - Get API key

### Step 2: Integration
Create a new data fetcher class that supports:
- Finnhub as primary source
- Twelve Data as fallback
- Yahoo Finance as last resort

### Step 3: API Endpoints

**Finnhub Forex OHLC:**
```
GET https://finnhub.io/api/v1/forex/candle?symbol=OANDA:EUR_USD&resolution=D&from=1572651390&to=1575243390&token=YOUR_API_KEY
```

Parameters:
- `symbol`: Format `OANDA:EUR_USD` (use OANDA as broker)
- `resolution`: 1, 5, 15, 30, 60, D, W, M
- `from`: Unix timestamp
- `to`: Unix timestamp

**Twelve Data Forex OHLC:**
```
GET https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&apikey=YOUR_API_KEY
```

Parameters:
- `symbol`: Format `EUR/USD`
- `interval`: 1min, 5min, 15min, 30min, 1h, 4h, 1day, 1week, 1month
- `outputsize`: Number of data points (max 5000)

---

## 💰 Cost Comparison (If Scaling Up)

If you need more than free tier:

| Provider | Monthly Cost | Calls/Min | Daily Limit | Notes |
|----------|-------------|-----------|-------------|-------|
| Finnhub | $59 | Unlimited | Unlimited | Best value |
| Twelve Data Grow | $29 | 55 | Unlimited | Good starter |
| Twelve Data Pro | $79 | 145 | Unlimited | More calls |
| Polygon.io | $99 | High | Unlimited | Enterprise |

---

## 📝 Next Steps

1. ✅ Sign up for Finnhub free account
2. ✅ Get API key
3. ✅ Implement Finnhub data fetcher
4. ✅ Test with current ForexAnalyzer
5. ✅ Add Twelve Data as fallback
6. ✅ Update documentation

---

## 🔗 Useful Links

- **Finnhub Docs**: https://finnhub.io/docs/api
- **Finnhub Python SDK**: `pip install finnhub-python`
- **Twelve Data Docs**: https://twelvedata.com/docs
- **Twelve Data Python SDK**: `pip install twelvedata`

---

**Last Updated**: November 2025
