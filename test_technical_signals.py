#!/usr/bin/env python3
"""
Test technical signals without ML interference
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.forex_analyzer import ForexAnalyzer

print("=" * 70)
print("TECHNICAL SIGNALS TEST (No ML)")
print("=" * 70)

analyzer = ForexAnalyzer()

# Test multiple pairs
test_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'XAU_USD', 'XAG_USD']

results = []

for symbol in test_pairs:
    print(f"\nAnalyzing {symbol}...")
    result = analyzer.analyze_pair(symbol, account_balance=10000, use_ml=False)

    if 'error' not in result:
        signal = result['final_decision']['signal']
        confidence = result['final_decision']['confidence']
        tech_signal = result['final_decision']['technical_signal']
        agreement = result['final_decision'].get('timeframe_agreement', 'N/A')

        results.append({
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence,
            'tech_signal': tech_signal,
            'agreement': agreement
        })

        print(f"  ✓ {signal} ({confidence:.1%}) - {agreement} timeframes agree")
    else:
        print(f"  ✗ Error: {result['error']}")

print("\n" + "=" * 70)
print("SUMMARY - TECHNICAL SIGNALS ONLY")
print("=" * 70)

buy_count = sum(1 for r in results if r['signal'] == 'BUY')
sell_count = sum(1 for r in results if r['signal'] == 'SELL')
hold_count = sum(1 for r in results if r['signal'] == 'HOLD')

print(f"\nTotal Analyzed: {len(results)}")
print(f"BUY Signals: {buy_count}")
print(f"SELL Signals: {sell_count}")
print(f"HOLD Signals: {hold_count}")

if results:
    print("\nDetailed Results:")
    print("-" * 70)
    print(f"{'Symbol':<12} {'Signal':<8} {'Confidence':<12} {'Agreement':<15}")
    print("-" * 70)

    for r in results:
        print(f"{r['symbol']:<12} {r['signal']:<8} {r['confidence']:<11.1%} {r['agreement']:<15}")

print("\n" + "=" * 70)
print("Note: Using technical analysis only (ML disabled)")
print("=" * 70)
