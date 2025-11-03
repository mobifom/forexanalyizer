# MetaTrader5 Installation Issue - FIXED ✓

## Problem

When running `pip install -r requirements.txt` on macOS or Linux, you encountered:

```
ERROR: Could not find a version that satisfies the requirement MetaTrader5>=5.0.45
ERROR: No matching distribution found for MetaTrader5>=5.0.45
```

## Root Cause

MetaTrader5 Python package is **only available on Windows**. It was incorrectly included in the core requirements, causing installation to fail on macOS and Linux.

## Solution Applied ✓

### 1. Updated requirements.txt
**Removed** MetaTrader5 from the core requirements file.

**Before:**
```
yfinance>=0.2.28
MetaTrader5>=5.0.45
```

**After:**
```
yfinance>=0.2.28
```

### 2. Created requirements-optional.txt
Created a new file for optional dependencies:
- MetaTrader5 (Windows only, commented out by default)
- Additional visualization libraries (seaborn, plotly)
- Jupyter notebook support

### 3. Created INSTALLATION.md
Comprehensive installation guide covering:
- Platform-specific instructions
- Troubleshooting common issues
- Virtual environment setup
- Optional dependencies

### 4. Updated Documentation
- Updated README.md with note about MetaTrader5
- Updated QUICKSTART.md with installation note
- Updated DOCUMENTATION_INDEX.md with installation guide

## Impact

### ✅ No Functionality Lost

The application **does not require** MetaTrader5 to function. It works perfectly with yfinance, which:
- Works on all platforms (Windows, macOS, Linux)
- Supports all forex pairs and metals
- Is free and requires no API key
- Provides all necessary data for the application

### ✅ Full Feature Parity

All features work identically with yfinance:
- Multi-timeframe analysis ✓
- Technical indicators ✓
- Machine learning ✓
- Risk management ✓
- Gold and silver support ✓

## What Changed

| File | Change |
|------|--------|
| requirements.txt | Removed MetaTrader5 |
| requirements.txt | Removed seaborn, plotly (moved to optional) |
| requirements-optional.txt | Created (optional dependencies) |
| INSTALLATION.md | Created (installation guide) |
| README.md | Updated installation section |
| QUICKSTART.md | Added installation note |
| DOCUMENTATION_INDEX.md | Added installation guide reference |

## Installation Now Works! ✓

### On macOS / Linux

```bash
pip install -r requirements.txt
```

This will install all core dependencies **without errors**.

### On Windows

```bash
# Install core dependencies
pip install -r requirements.txt

# Optional: Install MetaTrader5 (if you have MT5 terminal)
pip install MetaTrader5>=5.0.45
```

## Verify Installation

```bash
# Test that everything works
python test_gold_silver.py

# Should output:
# ✓ Successfully fetched data for Gold
# ✓ Successfully fetched data for Silver
```

## Data Source

The application uses **yfinance** by default:

```python
from src.data.data_fetcher import ForexDataFetcher

# This works on all platforms
fetcher = ForexDataFetcher()
data = fetcher.fetch_data('EURUSD=X', '1d')
```

The code already handles MT5 gracefully:

```python
try:
    import MetaTrader5 as mt5
    # MT5 code...
except ImportError:
    logger.info("MetaTrader5 not available - only yfinance will be used")
    MT5DataFetcher = None
```

## Next Steps

You can now proceed with:

1. ✅ Installation: `pip install -r requirements.txt`
2. ✅ Test: `python test_gold_silver.py`
3. ✅ Analyze: `python main.py analyze --symbol EURUSD=X`
4. ✅ Train model: `python main.py train`

## For Windows Users Who Want MT5

If you're on Windows and have MetaTrader5 terminal installed:

```bash
# After installing core requirements
pip install MetaTrader5>=5.0.45

# Then you can use MT5DataFetcher in the code
from src.data.data_fetcher import MT5DataFetcher
```

But this is **completely optional** - yfinance works great!

## Summary

✅ **Problem Fixed**: MetaTrader5 removed from core requirements
✅ **Installation Works**: On all platforms (macOS, Linux, Windows)
✅ **No Features Lost**: yfinance provides all necessary data
✅ **Documentation Updated**: Installation guide added
✅ **Ready to Use**: Just run `pip install -r requirements.txt`

---

**You're all set!** The application is ready to use on macOS. 🎉
