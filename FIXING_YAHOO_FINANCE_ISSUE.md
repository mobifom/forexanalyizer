# Fixing Yahoo Finance Issue - Get Real-Time Data

## Why Am I Seeing Yahoo Finance Instead of Twelve Data?

The issue is that **Streamlit caches the session state** between runs. Your analyzer was initialized with an old configuration before the authentication system was added.

## Quick Fix: Restart Streamlit

### Method 1: Keyboard Shortcut (Fastest)
1. In your terminal where Streamlit is running, press `Ctrl + C` to stop it
2. Run the app again: `streamlit run app.py`
3. Login with `admin` / `admin123`
4. You should now see "✅ Real-time data enabled (Twelve Data API)"

### Method 2: Clear Cache in Browser
1. While the app is running, press `C` in the terminal (or use the menu in the app)
2. Select "Clear cache"
3. Refresh the browser page
4. Login again

### Method 3: Use the "Always Rerun" Option
1. In your Streamlit app, click the menu (☰) in the top right
2. Select "Settings"
3. Under "Run on save", select "Always rerun"
4. Edit and save any file (like adding a space to app.py)

## Verify It's Working

After restarting, you should see:
- ✅ **"Real-time data enabled (Twelve Data API) - 10 minute auto-refresh"** (Green success message)

Instead of:
- ⚠️ **"Using delayed data (Yahoo Finance)"** (Orange warning)

## Check If API Key Is Being Read

To verify your API key is being loaded correctly, add this temporary debug line to `app.py`:

```python
# Right after line 198 (analyzer = st.session_state.analyzer)
st.sidebar.write(f"🔍 Debug - TwelveData active: {analyzer.data_fetcher.twelvedata_fetcher is not None}")
```

This will show in the sidebar whether Twelve Data is active or not.

## Common Reasons for Yahoo Finance Fallback

1. **Session state cached** (Most common - fixed by restarting)
2. **API key not loaded** (Check config/config.yaml line 74)
3. **API key invalid** (Verify on twelvedata.com dashboard)
4. **API rate limit exceeded** (Free tier: 8 calls/min, 800/day)
5. **Network/firewall blocking API calls**

## Testing the API Key

Run this command to test if your API key works:

```bash
python -c "
from src.data.twelvedata_fetcher import TwelveDataFetcher

api_key = '24b8973fe3ce42acad781d9178c6f4a7'
fetcher = TwelveDataFetcher(api_key)

if fetcher.check_api_status():
    print('✅ API key is VALID and working!')
else:
    print('❌ API key is INVALID or rate limited')
"
```

## What We Verified

I tested the initialization and confirmed:
- ✅ Config file loads correctly
- ✅ API key is present in config (`24b8973fe3...`)
- ✅ Data source is set to `auto`
- ✅ Twelve Data fetcher initializes successfully
- ✅ The code shows: "Twelve Data API initialized - Real-time forex data available!"

The API configuration is **correct** - you just need to restart Streamlit to clear the old cached session.

## After Restart, You Should See:

```
INFO:src.data.data_fetcher:✅ Twelve Data API initialized - Real-time forex data available!
```

In the logs, and the app will show the green success banner.

---

**TL;DR:** Stop Streamlit (`Ctrl+C`) and run it again: `streamlit run app.py`
