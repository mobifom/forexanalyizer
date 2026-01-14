# 🔑 Multiple TwelveData API Keys Setup

## Overview

The system now supports **3 TwelveData API keys** with automatic rotation, giving you **2,400 API calls per day** instead of just 800!

---

## 📊 Benefits

### Single Key (Before):
- ❌ 800 calls/day limit
- ❌ Must pause when limit reached
- ❌ Can't run all 10 assets continuously

### Multiple Keys (Now):
- ✅ **2,400 calls/day** (3 keys × 800)
- ✅ **Automatic rotation** when one key hits limit
- ✅ **Zero downtime** - seamlessly switches keys
- ✅ **Run all 10 assets** with current frequency settings!

---

## 🎯 How It Works

### Automatic Key Rotation

1. **Primary Key Active** (Key #1)
   - System uses Key #1 for all API calls
   - Tracks daily usage: 0/800, 100/800, 500/800...

2. **Key #1 Reaches Limit** (800/800 calls)
   - System automatically switches to Key #2
   - Logs: `🔄 Rotating from API key #1 (800/800) to key #2 (0/800)`

3. **Key #2 Active**
   - Continues seamless operation
   - Tracks: Key #1: 800/800, Key #2: 100/800...

4. **Key #2 Reaches Limit** (800/800 calls)
   - System switches to Key #3
   - Logs: `🔄 Rotating from API key #2 (800/800) to key #3 (0/800)`

5. **All Keys Exhausted** (rare)
   - Scheduler pauses until next day
   - At midnight, all keys reset to 0/800

---

## ⚙️ Setup Instructions

### Option 1: Environment Variables (Recommended)

**Step 1**: Get 3 API Keys

1. Go to https://twelvedata.com/pricing
2. Sign up for **3 free accounts** (use different emails)
3. Get API key from each account dashboard

**Step 2**: Set Environment Variables

**On Linux/Mac** (add to `~/.bashrc` or `~/.zshrc`):
```bash
export TWELVEDATA_API_KEY_1='050ff9ccf91a4197a0e40a49d48219f8'
export TWELVEDATA_API_KEY_2='050ff9ccf91a4197a0e40a49d48219f8'
export TWELVEDATA_API_KEY_3='050ff9ccf91a4197a0e40a49d48219f8'
```

**On Windows** (Command Prompt):
```cmd
setx TWELVEDATA_API_KEY_1 "your_first_api_key_here"
setx TWELVEDATA_API_KEY_2 "your_second_api_key_here"
setx TWELVEDATA_API_KEY_3 "your_third_api_key_here"
```

**Step 3**: Reload environment
```bash
# Linux/Mac
source ~/.bashrc   # or source ~/.zshrc

# Windows - restart terminal or computer
```

**Step 4**: Verify
```bash
echo $TWELVEDATA_API_KEY_1   # Should print your first key
echo $TWELVEDATA_API_KEY_2   # Should print your second key
echo $TWELVEDATA_API_KEY_3   # Should print your third key
```

---

### Option 2: .env File

**Step 1**: Create/Edit `.env` file in project root:

```bash
# TwelveData API Keys (up to 3 for rotation)
TWELVEDATA_API_KEY_1=your_first_api_key_here
TWELVEDATA_API_KEY_2=your_second_api_key_here
TWELVEDATA_API_KEY_3=your_third_api_key_here
```

**Step 2**: Ensure `.env` is in `.gitignore`:
```bash
echo ".env" >> .gitignore
```

**Never commit API keys to git!**

---

### Option 3: Direct in Config (Not Recommended)

**Edit `config/config.yaml`**:

```yaml
twelvedata:
  enabled: true
  api_keys:
    - 'your_first_api_key_here'
    - 'your_second_api_key_here'
    - 'your_third_api_key_here'
```

⚠️ **Warning**: Don't commit config with real API keys to git!

---

## 📈 Usage with 2,400 Calls/Day

### Current Frequency Settings:

| Timeframe | Interval | Calls/Asset/Day |
|-----------|----------|-----------------|
| 15m | 15 min | 96 |
| 1h | 60 min | 24 |
| 4h | 60 min | 24 |
| 1d | 1440 min | 1 |
| **Total** | - | **145** |

### Capacity:

**All 10 Assets**:
- Daily calls needed: 10 × 145 = 1,450
- Daily calls available: **2,400** (with 3 keys)
- **Status**: ✅ **950 calls to spare!**

**With optimizations** (market hours, priority):
- Actual daily usage: ~823 calls
- Daily capacity: 2,400 calls
- **Status**: ✅ **1,577 calls to spare!**

---

## 🖥️ Monitoring Key Rotation

### Start the Scheduler:
```bash
python run_scheduler.py
```

### Expected Output on Startup:
```
✅ Loaded 3 TwelveData API key(s)
✅ API Key Rotator initialized with 3 keys
   Total daily capacity: 2400 calls
✅ Using API Key Rotation with 3 keys
   Total daily capacity: 2400 calls/day
```

### Every 5 Minutes (Usage Report):
```
======================================================================
API KEY ROTATOR - USAGE REPORT
======================================================================
Active Key: #1 of 3
Per-Minute Usage: 2 / 8 calls

Daily Usage by Key:
  → Key #1: 256 / 800 calls (32.0%) [544 remaining]
    Key #2: 0 / 800 calls (0.0%) [800 remaining]
    Key #3: 0 / 800 calls (0.0%) [800 remaining]

Combined Total: 256 / 2400 calls (10.7%)
Total Remaining: 2144 calls
======================================================================
```

### When Key Rotates:
```
WARNING - 🔄 Rotating from API key #1 (800/800 calls) to key #2 (0/800 calls)
```

### All Keys Stats:
```
Daily Usage by Key:
  → Key #1: 800 / 800 calls (100.0%) [0 remaining]
    Key #2: 650 / 800 calls (81.3%) [150 remaining]
    Key #3: 0 / 800 calls (0.0%) [800 remaining]

Combined Total: 1450 / 2400 calls (60.4%)
Total Remaining: 950 calls
```

---

## 🔄 Key Rotation Logic

### When Does Rotation Happen?

**Trigger**: When current key reaches 800/800 daily limit

**Process**:
1. Check next key (Key #2)
2. If Key #2 < 800 calls → Switch to Key #2
3. If Key #2 = 800 calls → Check Key #3
4. If Key #3 < 800 calls → Switch to Key #3
5. If all keys = 800 calls → Pause until midnight reset

### Per-Minute Limit (Shared):

The 8 calls/minute limit is **shared across all keys**:
- Can't make more than 8 calls/min total
- Even if using different keys
- System automatically throttles

---

## 🧪 Testing the Setup

### Test 1: Verify Keys Are Loaded

```bash
python run_scheduler.py
```

**Look for**:
```
✅ Loaded 3 TwelveData API key(s)
✅ Using API Key Rotation with 3 keys
   Total daily capacity: 2400 calls/day
```

**If you see**:
```
✅ Loaded 1 TwelveData API key(s)
✅ Using single API key
```
→ Only 1 key found. Check environment variables.

**If you see**:
```
⚠️ No TwelveData API keys found
```
→ No keys configured. Follow setup steps above.

### Test 2: Run for 10 Minutes

Let scheduler run and watch the usage report:
```
Active Key: #1 of 3
Daily Usage by Key:
  → Key #1: 45 / 800 calls (5.6%) [755 remaining]
```

### Test 3: Check Rotation (Optional)

To test rotation, you can temporarily set a low limit:

**Edit `config/config.yaml`** temporarily:
```yaml
scheduler:
  rate_limiting:
    max_calls_per_day: 50  # Temporarily low for testing
```

Run scheduler and watch it rotate:
```
🔄 Rotating from API key #1 (50/50 calls) to key #2 (0/50 calls)
...
🔄 Rotating from API key #2 (50/50 calls) to key #3 (0/50 calls)
```

**Remember to change back to 800!**

---

## ❓ Troubleshooting

### "No API keys found"

**Check**:
```bash
echo $TWELVEDATA_API_KEY_1
echo $TWELVEDATA_API_KEY_2
echo $TWELVEDATA_API_KEY_3
```

**If empty**:
1. Set environment variables as shown above
2. Restart terminal
3. Try again

### "Using single API key" (want multiple)

**Means**: Only 1 key detected

**Fix**:
- Verify all 3 environment variables are set
- Check for typos: `TWELVEDATA_API_KEY_1` (not `TWELVEDATA_API_KEY1`)
- Ensure underscore between KEY and number

### "401 Unauthorized" errors

**Means**: Invalid API key

**Fix**:
1. Check API key is correct (no spaces, complete)
2. Verify key is active on twelvedata.com dashboard
3. Try regenerating key in dashboard

### Keys not rotating

**Check**:
1. First key must hit 800 calls to trigger rotation
2. Look for rotation log message
3. Verify `rotation.enabled: true` in config

---

## 📊 Configuration Reference

### config.yaml Settings:

```yaml
twelvedata:
  enabled: true

  # Multiple API keys (priority: env vars > direct config)
  api_keys:
    - ''  # Set via TWELVEDATA_API_KEY_1
    - ''  # Set via TWELVEDATA_API_KEY_2
    - ''  # Set via TWELVEDATA_API_KEY_3

  # Rotation settings
  rotation:
    enabled: true           # Auto-rotate when limit reached
    check_interval: 60      # Check every 60 seconds

# Scheduler rate limits (per key)
scheduler:
  rate_limiting:
    max_calls_per_minute: 8   # Shared across all keys
    max_calls_per_day: 800    # Per individual key
```

---

## 🎯 Summary

| Metric | Single Key | 3 Keys (Rotation) |
|--------|-----------|-------------------|
| **Daily Limit** | 800 calls | 2,400 calls |
| **Assets Supported** | ~5 assets | ✅ All 10 assets |
| **Downtime** | Pauses at 800 | ✅ None |
| **Manual Switching** | Required | ✅ Automatic |
| **Setup Time** | 5 minutes | 15 minutes |
| **Cost** | Free | Free (3 accounts) |

**Recommendation**: Set up 3 API keys for maximum reliability and capacity! 🚀

---

## 🚀 Quick Start Checklist

- [ ] Sign up for 3 TwelveData accounts (different emails)
- [ ] Get API key from each account dashboard
- [ ] Set 3 environment variables:
  - `TWELVEDATA_API_KEY_1`
  - `TWELVEDATA_API_KEY_2`
  - `TWELVEDATA_API_KEY_3`
- [ ] Restart terminal
- [ ] Verify keys loaded: `python run_scheduler.py`
- [ ] Check for "Using API Key Rotation with 3 keys"
- [ ] Monitor usage report every 5 minutes
- [ ] Enjoy 2,400 calls/day! 🎉

---

## 📞 Support

**Issues**:
- Check logs for "Loaded X TwelveData API key(s)"
- Verify environment variables are set
- Ensure keys are valid in twelvedata.com dashboard

**Documentation**:
- TwelveData: https://twelvedata.com/docs
- Free tier limits: https://twelvedata.com/pricing
