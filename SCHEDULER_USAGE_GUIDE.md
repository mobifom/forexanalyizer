# Smart Scheduler Usage Guide

## Overview

The Smart Scheduler provides automated, optimized data retrieval for forex, indices, crypto, and commodities with built-in:
- ✅ API rate limiting (respects 8 calls/min, 800 calls/day)
- ✅ Market hours awareness
- ✅ Asset priority system
- ✅ Automatic analysis triggers
- ✅ Usage monitoring and reporting

---

## 📊 New Assets Added

### Total: 10 Assets

| Asset | Symbol | Type | Priority |
|-------|--------|------|----------|
| EUR/USD | `EURUSD=X` | Forex | High |
| GBP/USD | `GBPUSD=X` | Forex | Medium |
| USD/JPY | `USDJPY=X` | Forex | Low |
| AUD/USD | `AUDUSD=X` | Forex | Low |
| Gold | `XAU_USD` | Commodity | Medium |
| Silver | `XAG_USD` | Commodity | Low |
| **Dow Jones** | **`US30`** | **Index** | **High** ⭐ |
| **NASDAQ 100** | **`US100`** | **Index** | **Medium** ⭐ |
| **Bitcoin** | **`BTC/USD`** | **Crypto** | **High** ⭐ |
| **Ethereum** | **`ETH/USD`** | **Crypto** | **Medium** ⭐ |

---

## 🚀 Quick Start

### Option 1: Run the Scheduler (Background Service)

```bash
# Make executable
chmod +x run_scheduler.py

# Run the scheduler
python run_scheduler.py
```

This will:
1. Start fetching data automatically based on schedule
2. Trigger analysis after each fetch
3. Print usage reports every 5 minutes
4. Run until you press Ctrl+C

### Option 2: Manual Integration in Your Code

```python
from src.scheduler.smart_scheduler import SmartScheduler
from src.utils.config_loader import load_config

# Load config
config = load_config('config/config.yaml')

# Create scheduler
scheduler = SmartScheduler(config)

# Register callbacks
scheduler.register_fetch_callback(your_fetch_function)
scheduler.register_analysis_callback(your_analysis_function)

# Start scheduler
assets = config['currency_pairs']
timeframes = config['timeframes']
scheduler.start(assets, timeframes)

# Monitor usage
print(scheduler.get_usage_report())
```

---

## ⚙️ Configuration

### Scheduler Settings (`config/config.yaml`)

```yaml
scheduler:
  enabled: true               # Master switch

  # Fetch intervals (minutes)
  fetch_intervals:
    '15m': 15                 # Every 15 minutes
    '1h': 60                  # Every 1 hour
    '4h': 240                 # Every 4 hours
    '1d': 360                 # Every 6 hours

  # Market hours (reduce API calls)
  respect_market_hours: true
  market_hours:
    forex:
      enabled: true
      days: [0,1,2,3,4]       # Mon-Fri
      start_hour: 0
      end_hour: 24

    indices:
      enabled: true
      days: [0,1,2,3,4]       # Mon-Fri
      start_hour: 9           # 9 AM ET
      end_hour: 16            # 4 PM ET

    crypto:
      enabled: false          # 24/7, no restrictions
      days: [0,1,2,3,4,5,6]
      start_hour: 0
      end_hour: 24

  # API limits
  rate_limiting:
    max_calls_per_minute: 8
    max_calls_per_day: 800
    enable_smart_throttling: true

  # Asset priorities (affects 15m fetch frequency)
  asset_priority:
    high: ['EURUSD=X', 'BTC/USD', 'US30']      # 15m every 15 min
    medium: ['GBPUSD=X', 'ETH/USD', 'US100', 'XAU_USD']  # 15m every 30 min
    low: ['USDJPY=X', 'AUDUSD=X', 'XAG_USD']   # 15m every 1 hour

  # Auto-analysis
  auto_analysis:
    enabled: true
    trigger_on_timeframes: ['15m', '1h', '4h', '1d']
    batch_analysis: true      # Analyze multiple timeframes together
    delay_seconds: 2          # Wait before analyzing
```

---

## 📈 API Usage Breakdown

### Expected Daily API Calls (Recommended Config)

| Asset | Type | 15m Freq | Market Hrs | Daily Calls |
|-------|------|----------|------------|-------------|
| EURUSD=X | Forex | 30min | Mon-Fri 24h | 59 |
| GBPUSD=X | Forex | 30min | Mon-Fri 24h | 59 |
| USDJPY=X | Forex | 1h | Mon-Fri 24h | 41 |
| AUDUSD=X | Forex | 1h | Mon-Fri 24h | 41 |
| XAU_USD | Commodity | 30min | Mon-Fri 24h | 59 |
| XAG_USD | Commodity | 1h | Mon-Fri 24h | 41 |
| US30 | Index | 30min | Mon-Fri 9:30-4pm | 18 |
| US100 | Index | 1h | Mon-Fri 9:30-4pm | 17 |
| BTC/USD | Crypto | 15min | 24/7 | 130 |
| ETH/USD | Crypto | 30min | 24/7 | 82 |
| | | | **TOTAL** | **~547** ✅ |

**Utilization: 68% of daily limit (253 calls remaining for manual use)**

See `API_USAGE_CALCULATION.md` for detailed breakdown.

---

## 🔍 Analysis Triggers

Analysis is automatically triggered after data fetch:

### Trigger Rules

1. **15m fetch** → Analyze 15m timeframe only
   - Quick analysis of short-term signals
   - Low computational cost

2. **1h fetch** → Analyze 1h timeframe only
   - Medium-term trend analysis
   - Confluence with 15m if recently fetched

3. **4h fetch** → Analyze 4h + confluence check
   - Important timeframe for swing trading
   - Checks alignment with other timeframes

4. **1d fetch** → Full multi-timeframe analysis
   - Comprehensive analysis across all timeframes
   - Generates complete trading recommendations
   - Applies enhanced signal controls

### Batch Analysis (Optimized)

When `batch_analysis: true`:
- If multiple timeframes were fetched within 60 seconds
- All timeframes are analyzed together in one pass
- Saves computation and provides better context
- Example: 1h fetch triggers → checks if 15m was just fetched → analyzes both together

---

## 📊 Monitoring & Reporting

### Real-Time Usage Report

```bash
# View current usage
python -c "
from src.scheduler.smart_scheduler import SmartScheduler
from src.utils.config_loader import load_config

config = load_config('config/config.yaml')
scheduler = SmartScheduler(config)
print(scheduler.get_usage_report())
"
```

Output:
```
============================================================
API USAGE REPORT
============================================================
Daily Usage: 234 / 800 calls
Daily Remaining: 566 calls
Daily Percentage: 29.3%
Last Minute: 2 / 8 calls
============================================================
```

### Usage Stats in Code

```python
stats = scheduler.api_tracker.get_usage_stats()

print(f"Daily: {stats['daily_count']}/{stats['daily_limit']}")
print(f"Remaining: {stats['daily_remaining']}")
print(f"Percentage: {stats['daily_percentage']:.1f}%")
print(f"Per Minute: {stats['minute_count']}/{stats['minute_limit']}")
```

---

## 🎯 Priority System Explained

The priority system adjusts **15-minute fetch frequency** to stay within API limits:

### High Priority Assets
- Fetched every **15 minutes** (full frequency)
- Best for: Most liquid, high-volatility assets
- Examples: EURUSD=X, BTC/USD, US30

### Medium Priority Assets
- Fetched every **30 minutes** (half frequency)
- Best for: Important but less volatile
- Examples: GBPUSD=X, ETH/USD, US100, XAU_USD

### Low Priority Assets
- Fetched every **1 hour** (same as 1h timeframe)
- Best for: Less volatile, lower importance
- Examples: USDJPY=X, AUDUSD=X, XAG_USD

**Note**: 1h, 4h, and 1d timeframes are NOT affected by priority. All assets fetch these on schedule.

---

## 🛠️ Customization Examples

### Example 1: Crypto-Only Mode (24/7)

```yaml
currency_pairs:
  - 'BTC/USD'
  - 'ETH/USD'

scheduler:
  respect_market_hours: false  # Fetch 24/7

  fetch_intervals:
    '15m': 15    # Real-time crypto tracking
    '1h': 60
    '4h': 240
    '1d': 360

  asset_priority:
    high: ['BTC/USD', 'ETH/USD']
```

**Expected API calls**: 260/day (both high priority)

### Example 2: Conservative Mode (Under 400 calls/day)

```yaml
scheduler:
  fetch_intervals:
    '15m': 30    # Fetch 15m every 30 minutes
    '1h': 120    # Fetch 1h every 2 hours
    '4h': 480    # Fetch 4h every 8 hours
    '1d': 720    # Fetch 1d every 12 hours

  asset_priority:
    high: ['EURUSD=X']          # Only 1 high priority
    medium: ['BTC/USD', 'US30']
    low: [...]                  # Rest are low
```

**Expected API calls**: ~350/day

### Example 3: Aggressive Mode (Maxing Out Free Tier)

```yaml
scheduler:
  fetch_intervals:
    '15m': 15    # All assets every 15 min
    '1h': 30     # More frequent 1h
    '4h': 120    # More frequent 4h
    '1d': 360

  asset_priority:
    high: ['EURUSD=X', 'GBPUSD=X', 'BTC/USD', 'US30', 'ETH/USD']  # Many high priority
```

**Expected API calls**: ~780/day (near limit)

---

## 🐛 Troubleshooting

### Issue: "Daily limit reached"

**Solution 1**: Reduce fetch frequency
```yaml
fetch_intervals:
  '15m': 30  # Was 15, now 30 (half the calls)
```

**Solution 2**: Reduce number of assets
```yaml
currency_pairs:
  - 'EURUSD=X'  # Comment out assets you don't need
  # - 'USDJPY=X'
```

**Solution 3**: Enable market hours filtering
```yaml
respect_market_hours: true  # Only fetch during active hours
```

### Issue: "Per-minute limit reached"

This shouldn't happen with proper scheduling, but if it does:

```yaml
rate_limiting:
  max_calls_per_minute: 6  # Was 8, more conservative
  enable_smart_throttling: true  # Ensures this is enabled
```

### Issue: Scheduler not fetching

**Check 1**: Is scheduler enabled?
```yaml
scheduler:
  enabled: true  # Must be true
```

**Check 2**: Are we within market hours?
```python
from src.scheduler.smart_scheduler import MarketHoursChecker

checker = MarketHoursChecker(config['scheduler'])
is_open = checker.is_market_open('EURUSD=X', 'forex')
print(f"Market open: {is_open}")
```

**Check 3**: Check logs
```bash
python run_scheduler.py 2>&1 | tee scheduler.log
```

---

## 📝 Symbol Mappings Reference

The system automatically converts between different formats:

| Config Symbol | Twelve Data | Yahoo Finance | Description |
|---------------|-------------|---------------|-------------|
| `EURUSD=X` | `EUR/USD` | `EURUSD=X` | Euro/Dollar |
| `US30` | `US30` | `^DJI` | Dow Jones |
| `US100` | `USTEC` | `^NDX` | NASDAQ 100 |
| `BTC/USD` | `BTC/USD` | `BTC-USD` | Bitcoin |
| `ETH/USD` | `ETH/USD` | `ETH-USD` | Ethereum |
| `XAU_USD` | `XAU/USD` | `GC=F` | Gold |
| `XAG_USD` | `XAG/USD` | `SI=F` | Silver |

No manual conversion needed - the system handles it automatically!

---

## 🎓 Best Practices

1. **Start Conservative**
   - Begin with fewer assets
   - Monitor API usage for a day
   - Gradually add more assets

2. **Use Priority System**
   - Set your most important assets as high priority
   - Use low priority for assets you check occasionally

3. **Enable Market Hours**
   - Saves significant API calls
   - Forex: 24/5 vs 24/7 = 29% savings
   - Indices: Business hours only = 81% savings

4. **Monitor Usage**
   - Check usage reports regularly
   - Adjust intervals if approaching limit
   - Consider upgrading if consistently hitting limits

5. **Batch Analysis**
   - Keep `batch_analysis: true`
   - More efficient, better context
   - Reduces redundant calculations

---

## 📚 Related Files

- `config/config.yaml` - Main configuration
- `API_USAGE_CALCULATION.md` - Detailed API call breakdown
- `run_scheduler.py` - Scheduler entry point
- `src/scheduler/smart_scheduler.py` - Scheduler implementation
- `src/data/twelvedata_fetcher.py` - Symbol mappings

---

## 🆘 Support

If you encounter issues:

1. Check logs for error messages
2. Verify API key is set: `echo $TWELVEDATA_API_KEY`
3. Test with single asset first
4. Review `API_USAGE_CALCULATION.md` for optimization tips

---

## 🎉 Summary

With the Smart Scheduler, you now have:

✅ **10 assets** across 4 asset classes (Forex, Indices, Crypto, Commodities)
✅ **Optimized data retrieval** (547 calls/day, 68% utilization)
✅ **Automatic analysis** after each fetch
✅ **Enhanced signal controls** for better accuracy
✅ **Market hours awareness** for efficiency
✅ **Real-time monitoring** of API usage
✅ **Flexible configuration** for your needs

Happy Trading! 📈
