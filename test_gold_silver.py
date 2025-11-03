#!/usr/bin/env python3
"""
Test script to verify Gold and Silver support
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data.data_fetcher import ForexDataFetcher


def test_commodity(symbol, name):
    """Test fetching data for a commodity"""
    print(f"\nTesting {name} ({symbol})...")
    print("-" * 60)

    fetcher = ForexDataFetcher(cache_duration_minutes=1)

    # Test daily data
    df = fetcher.fetch_data(symbol, '1d', use_cache=False)

    if df is not None and len(df) > 0:
        print(f"✓ Successfully fetched {len(df)} days of data")
        print(f"  Latest price: {df['Close'].iloc[-1]:.2f}")
        print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print(f"  High: {df['High'].max():.2f}")
        print(f"  Low: {df['Low'].min():.2f}")
        return True
    else:
        print(f"✗ Failed to fetch data for {symbol}")
        return False


def main():
    """Test gold and silver"""
    print("=" * 60)
    print("GOLD AND SILVER SUPPORT TEST")
    print("=" * 60)

    results = {}

    # Test Gold (using spot symbol with yfinance fallback)
    results['Gold Spot'] = test_commodity('XAU_USD', 'Gold Spot (XAU_USD)')

    # Test Silver (using spot symbol with yfinance fallback)
    results['Silver Spot'] = test_commodity('XAG_USD', 'Silver Spot (XAG_USD)')

    # Test alternative sources (optional)
    print("\n" + "=" * 60)
    print("Testing Alternative Sources (optional):")
    print("=" * 60)
    results['Gold Futures (GC=F)'] = test_commodity('GC=F', 'Gold Futures (GC=F)')
    results['Silver Futures (SI=F)'] = test_commodity('SI=F', 'Silver Futures (SI=F)')
    results['Gold ETF (GLD)'] = test_commodity('GLD', 'Gold ETF (GLD)')
    results['Silver ETF (SLV)'] = test_commodity('SLV', 'Silver ETF (SLV)')

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for commodity, success in results.items():
        status = "✓ SUPPORTED" if success else "✗ NOT SUPPORTED"
        print(f"{commodity}: {status}")

    print("\n" + "=" * 60)

    if all(results.values()):
        print("All commodities are supported!")
        return 0
    else:
        print("Some commodities are not available.")
        print("Note: You may need to use alternative symbols or data sources.")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
