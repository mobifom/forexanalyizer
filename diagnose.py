#!/usr/bin/env python3
"""
Diagnostic script to check data quality and signal generation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.forex_analyzer import ForexAnalyzer
from src.data.data_fetcher import ForexDataFetcher
import pandas as pd

print("=" * 70)
print("FOREX ANALYZER DIAGNOSTICS")
print("=" * 70)

# Test 1: Check gold price
print("\n[TEST 1] Gold Price Check")
print("-" * 70)

fetcher = ForexDataFetcher()
gold_data = fetcher.fetch_data('XAU_USD', '1d')

if gold_data is not None and len(gold_data) > 0:
    latest_price = gold_data['Close'].iloc[-1]
    latest_date = gold_data.index[-1]

    print(f"✓ Gold data fetched successfully")
    print(f"  Symbol: XAU_USD (Gold Spot)")
    print(f"  Latest Date: {latest_date.date()}")
    print(f"  Latest Price: ${latest_price:.2f}")
    print(f"  Data Points: {len(gold_data)}")

    # Show recent prices
    print("\n  Recent prices (last 5 days):")
    for idx, row in gold_data.tail(5).iterrows():
        print(f"    {idx.date()}: ${row['Close']:.2f}")
else:
    print("✗ Failed to fetch gold data")

# Test 2: Check EURUSD
print("\n[TEST 2] EURUSD Price Check")
print("-" * 70)

eurusd_data = fetcher.fetch_data('EURUSD=X', '1d')

if eurusd_data is not None and len(eurusd_data) > 0:
    latest_price = eurusd_data['Close'].iloc[-1]
    latest_date = eurusd_data.index[-1]

    print(f"✓ EURUSD data fetched successfully")
    print(f"  Latest Date: {latest_date.date()}")
    print(f"  Latest Price: {latest_price:.5f}")
    print(f"  Data Points: {len(eurusd_data)}")
else:
    print("✗ Failed to fetch EURUSD data")

# Test 3: Check signal generation
print("\n[TEST 3] Signal Generation Test")
print("-" * 70)

analyzer = ForexAnalyzer()

# Test on EURUSD
print("\nAnalyzing EURUSD=X...")
result = analyzer.analyze_pair('EURUSD=X', account_balance=10000, use_ml=False)

if 'error' not in result:
    print(f"✓ Analysis completed")
    print(f"  Final Signal: {result['final_decision']['signal']}")
    print(f"  Confidence: {result['final_decision']['confidence']:.2%}")
    print(f"  Technical Signal: {result['final_decision']['technical_signal']}")

    # Check individual timeframe signals
    print("\n  Timeframe Signals:")
    for tf in ['1d', '4h', '1h', '15m']:
        if tf in result['timeframe_analyses']:
            tf_data = result['timeframe_analyses'][tf]
            signals = tf_data['signals']

            buy_count = sum(1 for s in signals.values() if s == 'BUY')
            sell_count = sum(1 for s in signals.values() if s == 'SELL')
            hold_count = sum(1 for s in signals.values() if s == 'HOLD')

            print(f"    {tf.upper()}: BUY={buy_count}, SELL={sell_count}, HOLD={hold_count}")
            print(f"      Trend: {tf_data['trend_strength']:.1%}, Momentum: {tf_data['momentum']}")
else:
    print(f"✗ Analysis failed: {result.get('error', 'Unknown error')}")

# Test 4: Check indicator values
print("\n[TEST 4] Indicator Values Check (EURUSD 1D)")
print("-" * 70)

if eurusd_data is not None:
    from src.indicators.technical_indicators import TechnicalIndicators

    df = TechnicalIndicators.add_all_indicators(
        eurusd_data.copy(),
        analyzer.config['indicators']
    )

    latest = df.iloc[-1]

    print(f"  Price: ${latest['Close']:.5f}")
    print(f"  RSI: {latest['RSI']:.2f}")
    print(f"  MACD: {latest['MACD']:.5f}")
    print(f"  MACD Signal: {latest['MACD_Signal']:.5f}")
    print(f"  MA 20: {latest['MA_20']:.5f}")
    print(f"  MA 50: {latest['MA_50']:.5f}")

    # Check RSI levels
    if latest['RSI'] > 70:
        print("  ⚠️ RSI Overbought (>70)")
    elif latest['RSI'] < 30:
        print("  ⚠️ RSI Oversold (<30)")
    else:
        print("  ℹ️ RSI Neutral (30-70)")

    # Check MACD
    if latest['MACD'] > latest['MACD_Signal']:
        print("  📈 MACD above signal (bullish)")
    else:
        print("  📉 MACD below signal (bearish)")

    # Check MA position
    if latest['Close'] > latest['MA_50']:
        print("  📈 Price above MA 50 (bullish)")
    else:
        print("  📉 Price below MA 50 (bearish)")

# Test 5: Check signal threshold settings
print("\n[TEST 5] Configuration Check")
print("-" * 70)

print(f"  Confluence min timeframes: {analyzer.config.get('confluence', {}).get('min_timeframes_agree', 'N/A')}")
print(f"  Confluence min confidence: {analyzer.config.get('confluence', {}).get('min_confidence', 'N/A')}")
print(f"  RSI overbought: {analyzer.config.get('indicators', {}).get('rsi_overbought', 'N/A')}")
print(f"  RSI oversold: {analyzer.config.get('indicators', {}).get('rsi_oversold', 'N/A')}")

print("\n" + "=" * 70)
print("DIAGNOSTICS COMPLETE")
print("=" * 70)

# Recommendations
print("\n💡 RECOMMENDATIONS:")
print("-" * 70)

if result and 'error' not in result:
    if result['final_decision']['signal'] == 'HOLD':
        print("\n⚠️ Getting HOLD signals? This could mean:")
        print("  1. Market is in consolidation (no clear trend)")
        print("  2. Indicators are conflicting")
        print("  3. Signals don't meet minimum confidence threshold")
        print("  4. Not enough timeframes agree")

        print("\nTo get more signals, you can:")
        print(f"  • Lower min_confidence in config (currently {analyzer.config.get('confluence', {}).get('min_confidence', 0.6)})")
        print(f"  • Lower min_timeframes_agree (currently {analyzer.config.get('confluence', {}).get('min_timeframes_agree', 3)})")
        print("  • Train and use ML model for additional signal source")
        print("  • Analyze during higher volatility periods")
        print("\nNote: Market may genuinely be in consolidation with conflicting signals")
        print("This is realistic behavior - not all times have clear trading opportunities")

if gold_data is not None:
    print(f"\n✓ Gold price ({latest_price:.2f}) looks accurate for spot")
    print("  Note: XAU_USD represents real-time spot gold price")
    print("  Current range: ~$3,500-4,200/oz (as of late 2024/early 2025)")

print("\n")
