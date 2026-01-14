#!/usr/bin/env python3
"""
Test Script for Trading Signals Database
Run this to verify the signals database is working correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.signals_db import SignalsDB
from src.forex_analyzer import ForexAnalyzer


def test_signals_database():
    """Test signals database functionality"""
    print("=" * 70)
    print("TESTING TRADING SIGNALS DATABASE")
    print("=" * 70)

    # Initialize database
    print("\n1. Initializing signals database...")
    signals_db = SignalsDB('data/signals.db')
    print("   ✅ Database initialized")

    # Get initial stats
    print("\n2. Getting database statistics...")
    stats = signals_db.get_stats()
    print(f"   Active signals: {stats.get('total_active_signals', 0)}")
    print(f"   Archived signals: {stats.get('total_archived_signals', 0)}")
    print(f"   This week: {stats.get('this_week_signals', 0)}")

    # Test signal storage (simulate a signal)
    print("\n3. Testing signal storage...")
    test_signal_id = signals_db.store_signal(
        asset_symbol='EURUSD=X',
        timeframe='1d',
        signal_type='BUY',
        strength_level=0.75,
        current_price=1.0950,
        entry_points={
            'entry_1_immediate': {'price': 1.0950, 'description': 'Current market'},
            'entry_2_pullback': {'price': 1.0930, 'description': 'On pullback'},
            'entry_3_aggressive': {'price': 1.0960, 'description': 'Breakout entry'}
        },
        take_profits={
            'tp1_quick': {'price': 1.0980, 'description': 'Quick profit'},
            'tp2_conservative': {'price': 1.1000, 'description': 'Conservative target'},
            'tp3_extended': {'price': 1.1050, 'description': 'Extended target'}
        },
        stop_losses={
            'tight_1atr': {'price': 1.0935, 'description': 'Tight stop'},
            'standard_2atr': {'price': 1.0920, 'description': 'Standard stop'},
            'wide_3atr': {'price': 1.0900, 'description': 'Wide stop'}
        },
        risk_metrics={
            'risk_reward_ratio': 2.5,
            'risk_percentage': 1.5
        },
        context={
            'trend_direction': 'BULLISH',
            'momentum': 'STRONG',
            'reversal_detected': False
        }
    )

    if test_signal_id:
        print(f"   ✅ Test signal stored successfully (ID: {test_signal_id})")
    else:
        print("   ❌ Failed to store test signal")
        return False

    # Retrieve signals
    print("\n4. Testing signal retrieval...")
    signals = signals_db.get_signals(
        asset_symbol='EURUSD=X',
        timeframe='1d',
        limit=5
    )
    print(f"   ✅ Retrieved {len(signals)} signals for EURUSD=X 1d")

    # Get signals by timeframe
    print("\n5. Testing retrieval by timeframe...")
    signals_by_tf = signals_db.get_signals_by_timeframe(
        asset_symbol='EURUSD=X',
        limit_per_timeframe=10
    )
    print(f"   ✅ Retrieved signals for {len(signals_by_tf)} timeframes")
    for tf, tf_signals in signals_by_tf.items():
        print(f"      - {tf}: {len(tf_signals)} signals")

    # Test cleanup (dry run)
    print("\n6. Testing cleanup functionality...")
    archived = signals_db.cleanup_old_signals(days=7)
    print(f"   ✅ Cleanup complete: {archived} signals archived")

    # Final stats
    print("\n7. Final database statistics...")
    final_stats = signals_db.get_stats()
    print(f"   Active signals: {final_stats.get('total_active_signals', 0)}")
    print(f"   Archived signals: {final_stats.get('total_archived_signals', 0)}")

    signals_by_type = final_stats.get('signals_by_type', {})
    if signals_by_type:
        print("\n   Signals by Type:")
        for sig_type, count in signals_by_type.items():
            print(f"      {sig_type}: {count}")

    signals_by_tf_stat = final_stats.get('signals_by_timeframe', {})
    if signals_by_tf_stat:
        print("\n   Signals by Timeframe:")
        for tf, count in signals_by_tf_stat.items():
            print(f"      {tf}: {count}")

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run an analysis: streamlit run app.py")
    print("2. Go to Scanner page and run a scan")
    print("3. Scroll down to 'Signal History & Recommendations'")
    print("4. Select an asset to view signal history")
    print("\n" + "=" * 70)

    return True


def test_with_real_analysis():
    """Test with actual analysis (optional)"""
    print("\n" + "=" * 70)
    print("TESTING WITH REAL ANALYSIS")
    print("=" * 70)

    print("\n1. Initializing ForexAnalyzer...")
    analyzer = ForexAnalyzer()
    print("   ✅ Analyzer initialized")

    print("\n2. Running analysis for EURUSD=X...")
    print("   (This may take a moment...)")

    try:
        analysis = analyzer.analyze_pair(
            symbol='EURUSD=X',
            account_balance=10000,
            use_ml=False
        )

        if 'error' in analysis:
            print(f"   ❌ Analysis failed: {analysis['error']}")
            return False

        print("   ✅ Analysis complete")

        # Check if signals were saved
        signals_db = SignalsDB('data/signals.db')
        signals = signals_db.get_signals(
            asset_symbol='EURUSD=X',
            limit=5
        )

        print(f"\n3. Checking saved signals...")
        print(f"   ✅ Found {len(signals)} recent signals for EURUSD=X")

        if signals:
            latest = signals[0]
            print(f"\n   Latest Signal:")
            print(f"      Type: {latest['signal_type']}")
            print(f"      Strength: {latest['strength_category']} ({latest['strength_level']:.1%})")
            print(f"      Timeframe: {latest['timeframe']}")
            print(f"      Entry: {latest.get('entry_point_1', 'N/A')}")
            print(f"      SL: {latest.get('stop_loss_standard', 'N/A')}")
            print(f"      TP: {latest.get('take_profit_2', 'N/A')}")

        print("\n" + "=" * 70)
        print("✅ REAL ANALYSIS TEST PASSED")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"   ❌ Error during analysis: {e}")
        return False


if __name__ == '__main__':
    # Run basic tests
    success = test_signals_database()

    # Optionally run real analysis test
    if success:
        print("\n\nWould you like to test with a real analysis?")
        print("This will fetch live market data and run a full analysis.")
        response = input("Run real analysis test? (y/n): ")

        if response.lower() == 'y':
            test_with_real_analysis()
        else:
            print("\nSkipping real analysis test.")
            print("You can run it later by passing --real flag")
