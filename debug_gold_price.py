"""
Debug gold price - compare all data sources
"""

import sys
sys.path.append('/Users/mohamedhamdi/Work/Forex/ForexAnalyzer')

from src.data.data_fetcher import ForexDataFetcher
from src.data.twelvedata_fetcher import TwelveDataFetcher
import yfinance as yf
from datetime import datetime

print("=" * 70)
print("GOLD PRICE COMPARISON - ALL SOURCES")
print(f"Current time: {datetime.now()}")
print("=" * 70)

# Test 1: Twelve Data API directly
print("\n1. TWELVE DATA (Real-time API):")
try:
    fetcher = TwelveDataFetcher(api_key='24b8973fe3ce42acad781d9178c6f4a7')

    # Get quote (current price)
    quote = fetcher.get_quote('XAU_USD')
    if quote:
        print(f"   Current: ${quote.get('current', 0):.2f}")
        print(f"   Open: ${quote.get('open', 0):.2f}")
        print(f"   High: ${quote.get('high', 0):.2f}")
        print(f"   Low: ${quote.get('low', 0):.2f}")
        print(f"   Time: {quote.get('timestamp')}")

    # Get latest candle
    df = fetcher.fetch_candles('XAU_USD', '1d', limit=1)
    if not df.empty:
        print(f"\n   Latest Daily Candle:")
        print(f"   Close: ${df['Close'].iloc[-1]:.2f}")
        print(f"   Date: {df.index[-1]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Yahoo Finance (GC=F - Gold Futures)
print("\n2. YAHOO FINANCE - GC=F (Gold Futures):")
try:
    ticker = yf.Ticker('GC=F')
    df = ticker.history(period='1d', interval='1d')
    if not df.empty:
        print(f"   Close: ${df['Close'].iloc[-1]:.2f}")
        print(f"   Date: {df.index[-1]}")

    # Get current info
    info = ticker.info
    current = info.get('regularMarketPrice', info.get('currentPrice', 0))
    if current:
        print(f"   Current: ${current:.2f}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: ForexDataFetcher (with auto source selection)
print("\n3. FOREX DATA FETCHER (Auto mode):")
try:
    data_fetcher = ForexDataFetcher(
        cache_dir='data/cache',
        cache_duration_minutes=60,
        data_source='auto',
        twelvedata_api_key='24b8973fe3ce42acad781d9178c6f4a7'
    )

    # Try XAU_USD (Oanda/Twelve Data format)
    print("\n   a) Using symbol: XAU_USD")
    df = data_fetcher.fetch_data('XAU_USD', '1d', use_cache=False)
    if df is not None and not df.empty:
        print(f"      Close: ${df['Close'].iloc[-1]:.2f}")
        print(f"      Date: {df.index[-1]}")
    else:
        print("      No data")

    # Try GC=F (Yahoo format)
    print("\n   b) Using symbol: GC=F")
    df = data_fetcher.fetch_data('GC=F', '1d', use_cache=False)
    if df is not None and not df.empty:
        print(f"      Close: ${df['Close'].iloc[-1]:.2f}")
        print(f"      Date: {df.index[-1]}")
    else:
        print("      No data")

    # Try XAUUSD=X
    print("\n   c) Using symbol: XAUUSD=X")
    df = data_fetcher.fetch_data('XAUUSD=X', '1d', use_cache=False)
    if df is not None and not df.empty:
        print(f"      Close: ${df['Close'].iloc[-1]:.2f}")
        print(f"      Date: {df.index[-1]}")
    else:
        print("      No data")

except Exception as e:
    print(f"   Error: {e}")

# Test 4: Check what symbol the app uses
print("\n4. CHECKING CONFIG:")
try:
    from src.utils.config_loader import load_config
    config = load_config('config/config.yaml')
    pairs = config.get('currency_pairs', [])
    print(f"   Currency pairs in config:")
    for pair in pairs:
        if 'XAU' in pair or 'GC' in pair or 'GOLD' in pair.upper():
            print(f"   - {pair} (GOLD)")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
