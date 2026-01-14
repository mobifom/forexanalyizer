# 🚀 Quick Start: API Key Rotation

## 5-Minute Setup Guide

Get from **800 calls/day** to **2,400 calls/day** in 5 minutes!

---

## Step 1: Get 3 API Keys (2 minutes)

1. Go to https://twelvedata.com/pricing
2. Sign up for **3 free accounts** (use different emails)
3. Get API key from each account dashboard

**You'll have 3 keys that look like**:
```
abc123xyz456...
def789uvw012...
ghi345rst678...
```

---

## Step 2: Set Environment Variables (1 minute)

### On Mac/Linux:

```bash
export TWELVEDATA_API_KEY_1='abc123xyz456...'
export TWELVEDATA_API_KEY_2='def789uvw012...'
export TWELVEDATA_API_KEY_3='ghi345rst678...'
```

**Make it permanent** (add to `~/.bashrc` or `~/.zshrc`):
```bash
echo "export TWELVEDATA_API_KEY_1='abc123xyz456...'" >> ~/.bashrc
echo "export TWELVEDATA_API_KEY_2='def789uvw012...'" >> ~/.bashrc
echo "export TWELVEDATA_API_KEY_3='ghi345rst678...'" >> ~/.bashrc
source ~/.bashrc
```

### On Windows:

```cmd
setx TWELVEDATA_API_KEY_1 "abc123xyz456..."
setx TWELVEDATA_API_KEY_2 "def789uvw012..."
setx TWELVEDATA_API_KEY_3 "ghi345rst678..."
```

Then **restart your terminal**.

---

## Step 3: Verify Setup (1 minute)

```bash
python test_api_rotation.py
```

**Expected output**:
```
✅ Loaded 3 API key(s)
✅ Multiple keys found - rotation enabled!
   Total daily capacity: 2400 calls/day

✅ PASS: Scheduler Integration
✅ PASS: Data Fetcher Integration
✅ PASS: Key Rotation Logic
✅ PASS: Full Integration

🎉 All tests passed! API key rotation is fully integrated.
```

---

## Step 4: Run Scheduler (1 minute)

```bash
python run_scheduler.py
```

**You'll see**:
```
✅ Loaded 3 TwelveData API key(s)
✅ API Key Rotator initialized with 3 keys
   Total daily capacity: 2400 calls
✅ Twelve Data API initialized with key rotation
✅ Using API Key Rotation with 3 keys

🚀 STARTING FOREX ANALYZER SCHEDULER
```

---

## Step 5: Watch It Work!

### Usage Report (every 5 minutes):

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

### Automatic Rotation (when key hits 800 calls):

```
WARNING - 🔄 Rotating from API key #1 (800/800 calls) to key #2 (0/800 calls)
```

**That's it!** Scheduler continues running with **zero downtime**! 🎉

---

## ❓ Troubleshooting

### "Using single API key" (expected rotation)

**Fix**: Check environment variables are set correctly:
```bash
echo $TWELVEDATA_API_KEY_1  # Should print your key
echo $TWELVEDATA_API_KEY_2  # Should print your key
echo $TWELVEDATA_API_KEY_3  # Should print your key
```

If empty, restart terminal after setting variables.

### "No API keys found"

**Fix**:
1. Verify you ran the `export` commands
2. Restart terminal
3. Try again

### "401 Unauthorized" errors

**Fix**: One of your API keys is invalid
1. Check each key individually
2. Regenerate invalid keys in TwelveData dashboard

---

## 📚 Need More Info?

- **Complete Setup**: `MULTIPLE_API_KEYS_SETUP.md`
- **Technical Details**: `API_KEY_ROTATION_INTEGRATION.md`
- **What's New**: `WHATS_NEW.md`

---

## ✅ Success Checklist

- [ ] Signed up for 3 TwelveData accounts
- [ ] Got 3 API keys
- [ ] Set 3 environment variables
- [ ] Restarted terminal
- [ ] Ran `python test_api_rotation.py` - all tests pass
- [ ] Ran `python run_scheduler.py` - sees "Using API Key Rotation with 3 keys"
- [ ] Watching usage reports every 5 minutes
- [ ] Enjoying 2,400 calls/day! 🚀

---

**Time to complete**: ~5 minutes
**Cost**: $0 (100% free)
**Benefit**: 3× API capacity + zero downtime
