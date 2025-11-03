#!/usr/bin/env python3
"""
Test different gold and silver symbols to find what works with yfinance
"""

import yfinance as yf
from datetime import datetime

# Test different symbols
symbols_to_test = {
    'Gold': [
        'XAU_USD',   # Gold Spot (Oanda format, may fallback to GC=F)
        'GC=F',      # Gold Futures
        'GLD',       # SPDR Gold ETF
        'IAU',       # iShares Gold Trust
    ],
    'Silver': [
        'XAG_USD',   # Silver Spot (Oanda format, may fallback to SI=F)
        'SI=F',      # Silver Futures
        'SLV',       # iShares Silver Trust
    ]
}

print("=" * 70)
print("TESTING GOLD AND SILVER SYMBOLS WITH YFINANCE")
print("=" * 70)

working_symbols = {}

for metal, symbols in symbols_to_test.items():
    print(f"\n{metal.upper()}:")
    print("-" * 70)

    working_symbols[metal] = []

    for symbol in symbols:
        try:
            # Try to fetch data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='5d')

            if len(data) > 0:
                latest_price = data['Close'].iloc[-1]
                print(f"✓ {symbol:15} WORKS - Latest: ${latest_price:.2f}")
                working_symbols[metal].append({
                    'symbol': symbol,
                    'price': latest_price,
                    'data_points': len(data)
                })
            else:
                print(f"✗ {symbol:15} No data available")
        except Exception as e:
            print(f"✗ {symbol:15} Error: {str(e)[:50]}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY - RECOMMENDED SYMBOLS")
print("=" * 70)

for metal, syms in working_symbols.items():
    if syms:
        best = syms[0]
        print(f"\n{metal}:")
        print(f"  Recommended: {best['symbol']}")
        print(f"  Current Price: ${best['price']:.2f}")
        print(f"  Data Points: {best['data_points']}")

        if len(syms) > 1:
            print(f"  Alternatives: {', '.join([s['symbol'] for s in syms[1:]])}")
    else:
        print(f"\n{metal}: No working symbols found!")

print("\n" + "=" * 70)
