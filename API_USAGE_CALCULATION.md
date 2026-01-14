# API Usage Calculation & Optimization Strategy

## 📊 Assets Configuration

### Total Assets: 10

#### Forex Pairs (4)
1. **EURUSD=X** - Euro / US Dollar
2. **GBPUSD=X** - British Pound / US Dollar
3. **USDJPY=X** - US Dollar / Japanese Yen
4. **AUDUSD=X** - Australian Dollar / US Dollar

#### Commodities (2)
5. **XAU_USD** - Gold Spot
6. **XAG_USD** - Silver Spot

#### Indices (2)
7. **US30** - Dow Jones Industrial Average
8. **US100** - NASDAQ 100 (USTec)

#### Crypto (2)
9. **BTC/USD** - Bitcoin
10. **ETH/USD** - Ethereum

---

## 📈 Data Retrieval Schedule

### Fetch Intervals (as configured)
- **15m candles**: Every 15 minutes
- **1h candles**: Every 1 hour (60 minutes)
- **4h candles**: Every 4 hours (240 minutes)
- **1d candles**: Every 6 hours (360 minutes)

---

## 🧮 API Calls Calculation - UNOPTIMIZED (24/7 operation)

### Per Asset Per Day

| Timeframe | Fetch Interval | Calls Per Day | Calculation |
|-----------|----------------|---------------|-------------|
| **15m** | Every 15 min | **96** | 24 hours × 4 = 96 calls |
| **1h** | Every 1 hour | **24** | 24 hours × 1 = 24 calls |
| **4h** | Every 4 hours | **6** | 24 hours ÷ 4 = 6 calls |
| **1d** | Every 6 hours | **4** | 24 hours ÷ 6 = 4 calls |
| **TOTAL per asset** | | **130** | 96 + 24 + 6 + 4 |

### All Assets Combined (Unoptimized)

| Asset | 15m | 1h | 4h | 1d | **Total** |
|-------|-----|----|----|-------|
| EURUSD=X | 96 | 24 | 6 | 4 | **130** |
| GBPUSD=X | 96 | 24 | 6 | 4 | **130** |
| USDJPY=X | 96 | 24 | 6 | 4 | **130** |
| AUDUSD=X | 96 | 24 | 6 | 4 | **130** |
| XAU_USD | 96 | 24 | 6 | 4 | **130** |
| XAG_USD | 96 | 24 | 6 | 4 | **130** |
| US30 | 96 | 24 | 6 | 4 | **130** |
| US100 | 96 | 24 | 6 | 4 | **130** |
| BTC/USD | 96 | 24 | 6 | 4 | **130** |
| ETH/USD | 96 | 24 | 6 | 4 | **130** |
| **TOTAL** | **960** | **240** | **60** | **40** | **1,300** |

### ⚠️ **Problem**: Free Tier Limit = **800 calls/day**
**Unoptimized usage: 1,300 calls/day = 162% over limit!**

---

## ✅ Optimization Strategy #1: Market Hours Filtering

### Trading Hours by Asset Type

#### Forex (24/5 - Mon-Fri)
- **Active Hours**: 120 hours/week (24h × 5 days)
- **Percentage**: 71% of week (120/168)
- **Reduction**: ~29% fewer calls

#### US Indices (6.5h/day Mon-Fri)
- **Active Hours**: 32.5 hours/week (6.5h × 5 days)
- **Percentage**: 19% of week (32.5/168)
- **Reduction**: ~81% fewer calls

#### Crypto (24/7)
- **Active Hours**: 168 hours/week
- **Percentage**: 100% of week
- **Reduction**: 0%

### Optimized Calls Per Day (Market Hours Only)

| Asset Type | Assets | Unoptimized | Market Hours | Optimized Calls | Savings |
|------------|--------|-------------|--------------|-----------------|---------|
| **Forex** | 4 | 520 | Mon-Fri 24h | ~370 | -29% |
| **Commodities** | 2 | 260 | Mon-Fri 24h | ~185 | -29% |
| **Indices** | 2 | 260 | Mon-Fri 9:30-4pm | ~50 | -81% |
| **Crypto** | 2 | 260 | 24/7 | 260 | 0% |
| **TOTAL** | **10** | **1,300** | | **~865** | **-33%** |

### ⚠️ **Still Over**: 865 calls/day (108% of limit)

---

## ✅ Optimization Strategy #2: Selective Timeframe Fetching

### Reduced 15m Fetching (Primary Savings)

Instead of fetching 15m candles 24/7, reduce frequency:
- **Option A**: Fetch 15m only during peak hours (8am-8pm = 12 hours)
- **Option B**: Fetch 15m only for high-priority assets
- **Option C**: Fetch 15m every 30 minutes instead of 15

#### Option A: Peak Hours Only (12h/day)

| Timeframe | Full Day | Peak Hours | Savings |
|-----------|----------|------------|---------|
| 15m | 96 | **48** | **-50%** |
| 1h | 24 | 24 | 0% |
| 4h | 6 | 6 | 0% |
| 1d | 4 | 4 | 0% |
| **Total/asset** | 130 | **82** | **-37%** |

**Total for 10 assets**: 820 calls/day ✅ (within limit with market hours!)

#### Option B: High Priority Assets Only

Fetch 15m for only 5 priority assets:
- 5 assets × 96 calls = 480 calls
- 5 assets × 34 calls (1h+4h+1d) = 170 calls
- **Total**: 650 calls/day ✅

#### Option C: 30-Minute Intervals

| Timeframe | Normal | 30-min | Savings |
|-----------|--------|--------|---------|
| 15m | 96 | **48** | **-50%** |
| Others | 34 | 34 | 0% |
| **Total/asset** | 130 | **82** | **-37%** |

**Total for 10 assets**: 820 calls/day ✅

---

## ✅ Optimization Strategy #3: Priority-Based Smart Scheduling

### Asset Priority Tiers

#### High Priority (Fetch All Timeframes Frequently)
- **EURUSD=X** - Most liquid forex pair
- **BTC/USD** - Volatile, high interest
- **US30** - Major index

**Calls**: 3 assets × 130 = 390 calls/day

#### Medium Priority (Fetch 15m Less Frequently)
- **GBPUSD=X, ETH/USD, US100, XAU_USD**
- Fetch 15m every 30 min = 48 calls instead of 96

**Calls**: 4 assets × 82 = 328 calls/day

#### Low Priority (Fetch 15m Hourly Only)
- **USDJPY=X, AUDUSD=X, XAG_USD**
- Fetch 15m every hour = 24 calls instead of 96

**Calls**: 3 assets × 58 = 174 calls/day

### **Total with Priority System**: 390 + 328 + 174 = **892 calls/day**

---

## 🎯 RECOMMENDED Configuration (Under 800/day)

### Hybrid Approach: Market Hours + Priority + Reduced 15m

| Asset | Type | 15m Freq | Market Hours | Daily Calls |
|-------|------|----------|--------------|-------------|
| **EURUSD=X** | Forex | Every 30m | Mon-Fri 24h | 65 |
| **GBPUSD=X** | Forex | Every 30m | Mon-Fri 24h | 65 |
| **USDJPY=X** | Forex | Every 1h | Mon-Fri 24h | 50 |
| **AUDUSD=X** | Forex | Every 1h | Mon-Fri 24h | 50 |
| **XAU_USD** | Commodity | Every 30m | Mon-Fri 24h | 65 |
| **XAG_USD** | Commodity | Every 1h | Mon-Fri 24h | 50 |
| **US30** | Index | Every 30m | Mon-Fri 9:30-4pm | 20 |
| **US100** | Index | Every 1h | Mon-Fri 9:30-4pm | 13 |
| **BTC/USD** | Crypto | Every 15m | 24/7 | 130 |
| **ETH/USD** | Crypto | Every 30m | 24/7 | 82 |
| | | | **TOTAL** | **~590** ✅ |

### With Market Hours Applied (~71% uptime for Forex)
**Estimated**: ~420 calls/day ✅ **WELL UNDER LIMIT**

---

## 📊 Summary Table: Expected API Calls Per Asset

### Recommended Configuration (Per Asset)

| Asset | 15m (freq) | 1h | 4h | 1d | **Daily Total** |
|-------|------------|----|----|-------|
| **EURUSD=X** | 35 (30m) | 17 | 4 | 3 | **59** |
| **GBPUSD=X** | 35 (30m) | 17 | 4 | 3 | **59** |
| **USDJPY=X** | 17 (1h) | 17 | 4 | 3 | **41** |
| **AUDUSD=X** | 17 (1h) | 17 | 4 | 3 | **41** |
| **XAU_USD** | 35 (30m) | 17 | 4 | 3 | **59** |
| **XAG_USD** | 17 (1h) | 17 | 4 | 3 | **41** |
| **US30** | 7 (30m) | 6 | 2 | 3 | **18** |
| **US100** | 6 (1h) | 6 | 2 | 3 | **17** |
| **BTC/USD** | 96 (15m) | 24 | 6 | 4 | **130** |
| **ETH/USD** | 48 (30m) | 24 | 6 | 4 | **82** |
| | | | | **TOTAL** | **~547** ✅ |

### Market Hours Adjustment
With market hours filtering applied (Forex 5/7 days, Indices business hours):
- **Weekdays**: ~78 calls/day
- **Weekends**: ~21 calls/day (crypto only)
- **Monthly Average**: ~547 calls/day

---

## 🚀 Analysis Triggers

### Auto-Analysis Configuration

Analysis is triggered after each data fetch for:

1. **15m fetch** → Analyze 15m timeframe only
2. **1h fetch** → Analyze 1h timeframe only
3. **4h fetch** → Analyze 4h + perform confluence check
4. **1d fetch** → Analyze 1d + perform full multi-timeframe analysis

### Batch Analysis (Optimized)

When multiple timeframes are fetched simultaneously:
- Batch analysis reduces redundant calculations
- Shared indicator calculations across timeframes
- Single confluence calculation instead of multiple

---

## 💡 Additional Optimization Options

### If Still Need to Reduce Calls

1. **Disable 15m for low-volatility pairs**
   - Remove 15m for USDJPY, AUDUSD, XAG_USD
   - **Savings**: ~35 calls/day per asset

2. **Increase 1d fetch interval to 12 hours**
   - 1d changes slowly, 2 fetches/day sufficient
   - **Savings**: ~20 calls/day total

3. **Weekend mode**
   - Crypto only on weekends
   - **Current**: ~21 calls/day
   - **Savings**: N/A (already minimal)

4. **Use cached data more aggressively**
   - Extend cache to 30 minutes for 15m
   - Extend cache to 2 hours for 1h
   - **Savings**: ~30% fewer calls with slight data staleness

---

## 📝 API Call Limits Reference

### Twelve Data Free Tier
- **Per Minute**: 8 calls/minute
- **Per Day**: 800 calls/day
- **Recommended Configuration**: ~547 calls/day (68% utilization)
- **Safety Margin**: ~253 calls/day buffer for manual refreshes

### Peak API Usage Times
- **Market Open** (9:30 AM ET): ~10 calls (indices + forex)
- **Every 15 minutes**: ~2 calls (BTC only)
- **Every 30 minutes**: ~4 calls (high priority assets)
- **Every hour**: ~10 calls (all assets 1h + low priority 15m)
- **Every 4 hours**: ~10 calls (4h timeframe)
- **Every 6 hours**: ~10 calls (daily timeframe)

**Never exceeds 8 calls/minute with proper rate limiting** ✅
