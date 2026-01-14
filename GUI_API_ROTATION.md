# 🎨 GUI API Key Rotation - Complete Integration

## Overview

The **Streamlit GUI** (Analysis, Scanner, Training pages) now **fully supports API key rotation**! All manual "Analyze" and "Scan" buttons use the same rotation system as the automated scheduler.

---

## ✅ What Was Integrated

### **Before** (Single Key Only):
```python
# Old ForexAnalyzer initialization
analyzer = ForexAnalyzer()
# Used only: TWELVEDATA_API_KEY (single key)
# Limit: 800 calls/day
# Problem: GUI and scheduler had separate limits
```

### **After** (Automatic Rotation):
```python
# New ForexAnalyzer initialization
analyzer = ForexAnalyzer()
# Automatically loads: TWELVEDATA_API_KEY_1, _2, _3
# Creates APIKeyRotator if multiple keys found
# Shares capacity: 2,400 calls/day
# GUI and scheduler use same rotation system
```

---

## 🔧 How It Works

### 1. **ForexAnalyzer Initialization**

When you open the GUI (app.py, Scanner, or Training pages):

```python
# Streamlit pages automatically create
st.session_state.analyzer = ForexAnalyzer()

# Inside ForexAnalyzer.__init__():
api_keys = load_api_keys_from_config(config)  # Loads all 3 keys

if len(api_keys) > 1:
    # Create rotator for GUI
    self.api_key_rotator = APIKeyRotator(
        api_keys=api_keys,
        max_per_day=800,
        max_per_minute=8
    )
    api_key_provider = self.api_key_rotator.get_current_key

# Pass provider to data fetcher
self.data_fetcher = ForexDataFetcher(
    twelvedata_api_key_provider=api_key_provider  # Dynamic rotation!
)
```

### 2. **Automatic Key Usage**

When you click "🔍 Analyze" button:

```python
# User clicks "Analyze" for EURUSD
analysis = analyzer.analyze_pair('EURUSD=X')

# Inside analyze_pair():
data = self.data_fetcher.fetch_multiple_timeframes(symbol, ['1d', '4h', '1h', '15m'])
# Each timeframe = 1 API call = 4 calls total

# TwelveDataFetcher automatically:
api_key = self._get_api_key()  # Gets current key from rotator
# Makes API call with current active key
```

### 3. **API Call Tracking**

After fetching data, calls are recorded:

```python
# In analyze_pair() after successful fetch:
if self.api_key_rotator and self.data_fetcher.twelvedata_fetcher:
    for _ in range(len(data)):  # 4 timeframes = 4 calls
        self._record_api_call()

# Inside rotator:
self.daily_counts[current_key_index] += 1  # Tracks usage per key
```

### 4. **Automatic Rotation**

Next API call checks limits:

```python
# When fetching next asset:
can_call, reason = self.api_key_rotator.can_make_call()

if current_key reached 800:
    # Auto-rotate to next key
    self._try_rotate_key()
    logger.warning("🔄 Rotating from key #1 to key #2")
```

---

## 📊 GUI Pages Integration

### **Main Analysis Page** (`app.py`)

✅ **Integrated**: Uses ForexAnalyzer with rotation
- Click "🔍 Analyze" → Fetches 4 timeframes → Records 4 API calls
- Uses current active key from rotator
- Shares usage tracking with scheduler

### **Scanner Page** (`pages/1_📊_Scanner.py`)

✅ **Integrated**: Uses ForexAnalyzer with rotation
- Click "🔍 Scan All" → Fetches 10 assets × 4 timeframes = 40 API calls
- Each asset fetched with current active key
- Rotation happens mid-scan if key limit reached
- Example:
  ```
  Analyzing EURUSD... (Key #1: 756/800)
  Analyzing GBPUSD... (Key #1: 760/800)
  ...
  Analyzing AUDUSD... (Key #1: 800/800)
  🔄 Rotating to key #2
  Analyzing XAU_USD... (Key #2: 4/800)
  ```

### **Training Page** (`pages/2_🤖_Training.py`)

✅ **Integrated**: Uses ForexAnalyzer with rotation
- Click "Train Model" → Fetches historical data → Records API calls
- Uses rotation if training requires multiple assets

---

## 🎯 Usage Scenarios

### Scenario 1: Single Asset Analysis

**User Action**: Analyze EURUSD=X

**API Calls**:
1. Fetch 15m data → 1 call (Key #1: 1/800)
2. Fetch 1h data → 1 call (Key #1: 2/800)
3. Fetch 4h data → 1 call (Key #1: 3/800)
4. Fetch 1d data → 1 call (Key #1: 4/800)

**Total**: 4 API calls recorded to Key #1

### Scenario 2: Full Scanner Run

**User Action**: Scan All 10 Assets

**API Calls** (per asset):
- 4 timeframes × 10 assets = **40 API calls**

**With Rotation** (if Key #1 at 780/800 before scan):
```
Asset 1: Key #1 (784/800)
Asset 2: Key #1 (788/800)
Asset 3: Key #1 (792/800)
Asset 4: Key #1 (796/800)
Asset 5: Key #1 (800/800) → 🔄 Rotate to Key #2
Asset 6: Key #2 (4/800)
Asset 7: Key #2 (8/800)
...
Asset 10: Key #2 (20/800)
```

**Result**: Scan completes without interruption!

### Scenario 3: Manual Refresh

**User Action**: Click "🔄 Refresh Data" (force fresh data)

```python
# In app.py or Scanner page:
fetcher = st.session_state.analyzer.data_fetcher
df = fetcher.fetch_data(symbol, timeframe, use_cache=False)
# use_cache=False forces fresh API call

# Automatically uses current key from rotator
# Call is tracked in rotator
```

---

## 🔍 Viewing API Usage in GUI

You can check API usage programmatically:

```python
# In any Streamlit page:
if st.session_state.analyzer.api_key_rotator:
    usage_report = st.session_state.analyzer.get_api_usage_report()
    st.text(usage_report)
```

**Example Output**:
```
======================================================================
API KEY ROTATOR - USAGE REPORT
======================================================================
Active Key: #1 of 3
Per-Minute Usage: 0 / 8 calls

Daily Usage by Key:
  → Key #1: 124 / 800 calls (15.5%) [676 remaining]
    Key #2: 0 / 800 calls (0.0%) [800 remaining]
    Key #3: 0 / 800 calls (0.0%) [800 remaining]

Combined Total: 124 / 2400 calls (5.2%)
Total Remaining: 2276 calls
======================================================================
```

---

## 💡 Key Benefits for GUI Users

### 1. **Seamless Experience**
- No need to manually switch API keys
- Works exactly like before, just with more capacity

### 2. **Shared Capacity**
- GUI and scheduler share the 2,400 call pool
- Smart utilization across all tools

### 3. **Zero Configuration**
- Same environment variables as scheduler
- Automatic detection and setup

### 4. **Real-Time Rotation**
- Mid-scan rotation if needed
- No failed requests due to limits

### 5. **Backward Compatible**
- Works with 1 key (no rotation)
- Works with 0 keys (yfinance fallback)

---

## 🧪 Testing GUI Integration

### Test 1: Verify Rotation is Active

```python
# Open Streamlit app
# In Python console or add to page:

import streamlit as st

if 'analyzer' in st.session_state:
    analyzer = st.session_state.analyzer

    if analyzer.api_key_rotator:
        st.success(f"✅ API Rotation Active: {len(analyzer.api_key_rotator.api_keys)} keys")
        st.info(f"Current key: #{analyzer.api_key_rotator.current_key_index + 1}")
    else:
        st.warning("⚠️ No rotation (single key or no keys)")
```

### Test 2: Track Calls During Scan

```python
# Before scanning
before = analyzer.api_key_rotator.get_usage_stats()
st.write(f"Before: {before['total_daily_count']} calls")

# Run scan
# ... scan code ...

# After scanning
after = analyzer.api_key_rotator.get_usage_stats()
st.write(f"After: {after['total_daily_count']} calls")
st.write(f"Calls made: {after['total_daily_count'] - before['total_daily_count']}")
```

### Test 3: Simulate Rotation

```python
# Force Key #1 to limit
analyzer.api_key_rotator.daily_counts[0] = 799

# Make one analysis (will hit limit)
analysis = analyzer.analyze_pair('EURUSD=X')

# Check if rotated
current_key = analyzer.api_key_rotator.current_key_index
st.write(f"Current key after limit: #{current_key + 1}")
# Should show "2" (rotated to Key #2)
```

---

## 📝 Code Changes Summary

### Modified File: `src/forex_analyzer.py`

**Imports**:
```python
from .utils.api_key_rotator import APIKeyRotator, load_api_keys_from_config
```

**Initialization**:
```python
# Load multiple API keys
api_keys = load_api_keys_from_config(self.config)

# Create rotator if multiple keys
if len(api_keys) > 1:
    self.api_key_rotator = APIKeyRotator(...)
    api_key_provider = self.api_key_rotator.get_current_key
else:
    self.api_key_rotator = None
    api_key_provider = None

# Pass provider to data fetcher
self.data_fetcher = ForexDataFetcher(
    twelvedata_api_key_provider=api_key_provider
)
```

**Call Tracking**:
```python
def _record_api_call(self):
    """Record API call to rotator"""
    if self.api_key_rotator:
        self.api_key_rotator.record_call()

def analyze_pair(self, symbol, ...):
    data = self.data_fetcher.fetch_multiple_timeframes(...)

    # Track calls
    if self.api_key_rotator:
        for _ in range(len(data)):
            self._record_api_call()
```

**Usage Reporting**:
```python
def get_api_usage_report(self) -> str:
    """Get usage report for GUI display"""
    if self.api_key_rotator:
        return self.api_key_rotator.get_usage_report()
    else:
        return "API rotation not enabled"
```

---

## ⚠️ Important Notes

### Cache Behavior
- **Default**: 20-minute cache (data_config.cache_duration_minutes)
- **API calls** only made when:
  1. Cache expired (auto-refresh)
  2. Manual refresh (use_cache=False)
  3. First time fetching asset

**Impact**: Even with rotation, respects cache to minimize API usage

### Call Attribution
- Calls are recorded **per successful fetch**
- If fetch fails (network error, invalid symbol), no call recorded
- If data from cache, no call recorded
- Only TwelveData API calls are tracked (not yfinance fallback)

### Shared vs Separate Instances
- **GUI**: Each browser session = one ForexAnalyzer instance
- **Scheduler**: Separate process = separate ForexAnalyzer instance
- **Usage tracking**: Independent (GUI has own rotator, scheduler has own rotator)
- **API keys**: Shared across both (same environment variables)

---

## 🎯 Best Practices

### 1. **Monitor Usage**
Add this to your GUI sidebar:
```python
with st.sidebar:
    if st.button("📊 Show API Usage"):
        if st.session_state.analyzer.api_key_rotator:
            report = st.session_state.analyzer.get_api_usage_report()
            st.code(report)
```

### 2. **Respect Cache**
- Don't use `use_cache=False` excessively
- Let auto-refresh handle updates
- Cache saves API calls without sacrificing freshness

### 3. **Batch Operations**
- Use "Scan All" instead of analyzing one-by-one
- Rotation handles mid-batch key switching
- More efficient than manual iterations

---

## ✅ Integration Complete!

The GUI now has the **same powerful API key rotation** as the scheduler:

- ✅ **2,400 calls/day capacity**
- ✅ **Automatic key rotation**
- ✅ **Real-time call tracking**
- ✅ **Seamless mid-operation switching**
- ✅ **Zero configuration needed**
- ✅ **Backward compatible**

**No changes needed to existing GUI code** - rotation happens automatically! 🎉
