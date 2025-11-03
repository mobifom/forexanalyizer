# Installation Guide

## Quick Installation (Recommended)

### Step 1: Install Core Dependencies

```bash
pip install -r requirements.txt
```

This installs all the essential dependencies needed to run the application.

### Step 2: Verify Installation

```bash
# Test that everything works
python test_gold_silver.py

# Or run a quick analysis
python main.py analyze --symbol EURUSD=X --no-ml
```

## Platform-Specific Notes

### macOS / Linux

The core application works perfectly on macOS and Linux with just the main requirements.

**Note**: MetaTrader5 is **not available** on macOS/Linux. The application uses yfinance by default, which works on all platforms.

### Windows

On Windows, you have the option to use MetaTrader5 for data fetching:

```bash
# Install core dependencies
pip install -r requirements.txt

# Optional: Install MetaTrader5 (Windows only)
pip install MetaTrader5>=5.0.45
```

## Optional Dependencies

For additional features like advanced visualization:

```bash
pip install -r requirements-optional.txt
```

This includes:
- Seaborn (enhanced plots)
- Plotly (interactive charts)
- Jupyter (notebook support)

## Troubleshooting Installation

### Error: "No matching distribution found for MetaTrader5"

**Solution**: This is normal on macOS/Linux. MetaTrader5 has been removed from the core requirements.

The application works perfectly without it using yfinance for data.

### Warning: "dependency conflicts" with streamlit/packaging

**Solution**: This is just a warning and won't affect the forex analyzer. If you want to fix it:

**Option 1** (Recommended): Use a virtual environment to isolate dependencies
```bash
python -m venv forex_env
source forex_env/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

**Option 2**: Downgrade packaging (if needed for streamlit)
```bash
pip install "packaging<25,>=20"
```

**Option 3**: Ignore it - the forex analyzer will work fine regardless

### Error: "No module named 'ta'"

**Solution**: Install the technical analysis library:
```bash
pip install ta
```

### Error: "Could not install pandas-ta"

**Solution**: Try installing from source:
```bash
pip install git+https://github.com/twopirllc/pandas-ta
```

Or skip it - the application uses its own technical indicator implementations.

### Error with xgboost on macOS with Apple Silicon

**Solution**: Use conda or install compatible version:
```bash
conda install xgboost
# OR
pip install xgboost --no-cache-dir
```

## Minimal Installation

If you just want to test the application quickly:

```bash
# Absolute minimum dependencies
pip install pandas numpy yfinance scikit-learn pyyaml joblib
```

This will allow basic analysis without ML features.

## Virtual Environment (Recommended)

### Create Virtual Environment

**Using venv:**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

**Using conda:**
```bash
conda create -n forex python=3.10
conda activate forex
```

### Install in Virtual Environment

```bash
pip install -r requirements.txt
```

## Verify Installation

Run the test script to verify everything works:

```bash
# Test gold and silver data fetching
python test_gold_silver.py

# Should output:
# ✓ Successfully fetched data for Gold
# ✓ Successfully fetched data for Silver
```

## Python Version

**Required**: Python 3.8 or higher

**Recommended**: Python 3.10 or 3.11

Check your version:
```bash
python --version
```

## Common Installation Issues

### Issue: pandas installation fails

**Solution**: Update pip first
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: NumPy compatibility errors

**Solution**: Install compatible versions
```bash
pip install numpy<2.0
pip install pandas
```

### Issue: Scikit-learn build errors

**Solution**: Install pre-built wheels
```bash
pip install --upgrade pip setuptools wheel
pip install scikit-learn
```

## Data Sources

After installation, the application will use:

1. **yfinance** (default, all platforms)
   - Forex pairs: EURUSD=X, GBPUSD=X, etc.
   - Precious metals: GC=F, SI=F
   - Free, no API key needed

2. **MetaTrader5** (optional, Windows only)
   - Requires MT5 terminal installed
   - More reliable for some pairs
   - Better for high-frequency data

## Next Steps

After successful installation:

1. **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
2. **Configure**: Edit `config/config.yaml`
3. **Train Model**: `python main.py train`
4. **Start Trading Analysis**: `python main.py analyze --symbol EURUSD=X`

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review [QUICKSTART.md](QUICKSTART.md) troubleshooting
3. Check [README.md](README.md) for detailed documentation
4. Verify Python version: `python --version`
5. Ensure pip is updated: `pip install --upgrade pip`

## System Requirements

**Minimum**:
- Python 3.8+
- 4 GB RAM
- 500 MB disk space
- Internet connection (for data fetching)

**Recommended**:
- Python 3.10+
- 8 GB RAM
- 1 GB disk space
- Fast internet connection

## Installation Complete ✓

You're ready to go! Try:

```bash
python main.py analyze --symbol GC=F
```
