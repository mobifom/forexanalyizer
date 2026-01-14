#!/usr/bin/env python3
"""
Quick test to verify signal storage and retrieval
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.signals_db import SignalsDB

def test_signal_retrieval():
    """Test signal retrieval"""
    print("=" * 70)
    print("TESTING SIGNAL RETRIEVAL")
    print("=" * 70)

    # Initialize database
    signals_db = SignalsDB('data/signals.db')

    # Get all active signals
    print("\n1. Getting all active signals...")
    all_signals = signals_db.get_signals(limit=100, active_only=True)
    print(f"   Total active signals: {len(all_signals)}")

    if all_signals:
        print("\n2. Sample signals:")
        for signal in all_signals[:5]:
            print(f"   - {signal['asset_symbol']} {signal['timeframe']} {signal['signal_type']} @ {signal['current_price']}")

        print("\n3. Assets with signals:")
        assets = set(s['asset_symbol'] for s in all_signals)
        for asset in sorted(assets):
            count = sum(1 for s in all_signals if s['asset_symbol'] == asset)
            print(f"   - {asset}: {count} signals")

        print("\n4. Signals by timeframe:")
        timeframes = set(s['timeframe'] for s in all_signals)
        for tf in sorted(timeframes):
            count = sum(1 for s in all_signals if s['timeframe'] == tf)
            print(f"   - {tf}: {count} signals")

        print("\n5. Testing XAU_USD signals (from your log):")
        xau_signals = signals_db.get_signals(
            asset_symbol='XAU_USD',
            limit=20,
            active_only=True
        )
        print(f"   Total XAU_USD signals: {len(xau_signals)}")

        if xau_signals:
            print("\n   XAU_USD signal details:")
            for signal in xau_signals:
                print(f"   - ID:{signal['id']} {signal['timeframe']} {signal['signal_type']} @ {signal['current_price']} ({signal['created_at']})")

        print("\n6. Testing get_signals_by_timeframe for XAU_USD:")
        xau_by_tf = signals_db.get_signals_by_timeframe(
            asset_symbol='XAU_USD',
            limit_per_timeframe=20,
            active_only=True
        )
        print(f"   Timeframes with data: {list(xau_by_tf.keys())}")
        for tf, signals in xau_by_tf.items():
            print(f"   - {tf}: {len(signals)} signals")
    else:
        print("\n⚠️  No signals found in database!")
        print("   Possible reasons:")
        print("   1. No analysis has been run yet")
        print("   2. All signals are archived (older than 7 days)")
        print("   3. Database file doesn't exist or is empty")

    # Check database stats
    print("\n7. Database statistics:")
    stats = signals_db.get_stats()
    print(f"   Active signals: {stats.get('total_active_signals', 0)}")
    print(f"   Archived signals: {stats.get('total_archived_signals', 0)}")
    print(f"   This week: {stats.get('this_week_signals', 0)}")
    print(f"   By type: {stats.get('signals_by_type', {})}")
    print(f"   By timeframe: {stats.get('signals_by_timeframe', {})}")

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    test_signal_retrieval()
