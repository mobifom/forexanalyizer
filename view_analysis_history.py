#!/usr/bin/env python3
"""
View Analysis History Tool
CLI tool to view stored analysis results and changes
"""

import sys
import os
from datetime import datetime, timedelta
import argparse

sys.path.insert(0, os.path.dirname(__file__))

from src.database.analysis_db import AnalysisDB
from src.analysis.analysis_comparison import AnalysisComparison


def format_timestamp(ts_str: str) -> str:
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts_str


def print_latest_analyses(db: AnalysisDB, asset: str = None):
    """Print latest analyses"""
    print("\n" + "=" * 80)
    print("LATEST ANALYSIS RESULTS")
    print("=" * 80)

    if asset:
        result = db.get_latest_analysis(asset)
        if result:
            results = [result]
        else:
            results = []
    else:
        # Get all assets
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT asset_symbol FROM analysis_results WHERE is_latest = 1')
        assets = [row[0] for row in cursor.fetchall()]
        conn.close()

        results = []
        for a in assets:
            r = db.get_latest_analysis(a)
            if r:
                results.append(r)

    if not results:
        print("No analysis results found.")
        return

    for result in results:
        emoji = AnalysisComparison.get_signal_emoji(result['consensus'])

        print(f"\n{emoji} {result['asset_symbol']} ({result['timeframe']})")
        print(f"  Signal: {result['consensus']}")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Price: ${result['price']:.5f}" if result['price'] else "  Price: N/A")

        if result['rsi']:
            print(f"  RSI: {result['rsi']:.1f}")

        if result['trend_strength']:
            print(f"  Trend Strength: {result['trend_strength']:.1%}")

        if result['reversal_detected']:
            print(f"  ⚠️  Reversal: {result['reversal_type']}")

        print(f"  Analyzed: {format_timestamp(result['created_at'])}")

    print("\n" + "=" * 80)


def print_recent_changes(db: AnalysisDB, asset: str = None, hours: int = 24):
    """Print recent changes"""
    print("\n" + "=" * 80)
    print(f"RECENT CHANGES (Last {hours} hours)")
    print("=" * 80)

    changes = db.get_analysis_changes(asset, hours)

    if not changes:
        print("No changes detected in the specified period.")
        return

    for change in changes:
        timestamp = format_timestamp(change['created_at'])

        if change['signal_changed']:
            print(f"\n🔄 {change['asset_symbol']} ({change['timeframe']}) - {timestamp}")
            print(f"  Signal: {change['previous_signal']} → {change['current_signal']}")
            print(f"  Change Type: {change['change_type']}")
            print(f"  Description: {change['change_description']}")

            if change['confidence_change']:
                direction = '↑' if change['confidence_change'] > 0 else '↓'
                print(f"  Confidence: {direction} {abs(change['confidence_change']):.1%}")

    print("\n" + "=" * 80)


def print_history(db: AnalysisDB, asset: str, timeframe: str, days: int = 7):
    """Print analysis history"""
    print("\n" + "=" * 80)
    print(f"ANALYSIS HISTORY: {asset} ({timeframe}) - Last {days} days")
    print("=" * 80)

    history = db.get_analysis_history(asset, timeframe, days)

    if not history:
        print("No history found for the specified asset/timeframe.")
        return

    print(f"\nFound {len(history)} analyses\n")

    for i, result in enumerate(history, 1):
        emoji = AnalysisComparison.get_signal_emoji(result['consensus'])
        timestamp = format_timestamp(result['created_at'])

        print(f"{i}. {emoji} {timestamp}")
        print(f"   Signal: {result['consensus']} (Confidence: {result['confidence']:.1%})")

        if result['price']:
            print(f"   Price: ${result['price']:.5f}")

        if result['rsi']:
            zone = ''
            if result['rsi'] < 30:
                zone = ' [OVERSOLD]'
            elif result['rsi'] > 70:
                zone = ' [OVERBOUGHT]'
            print(f"   RSI: {result['rsi']:.1f}{zone}")

        if result['reversal_detected']:
            print(f"   ⚠️  {result['reversal_type']} reversal")

        print()

    print("=" * 80)


def print_stats(db: AnalysisDB):
    """Print database statistics"""
    stats = db.get_stats()

    print("\n" + "=" * 80)
    print("📊 DATABASE STATISTICS")
    print("=" * 80)

    print(f"\nTotal analyses stored: {stats.get('total_analyses', 0)}")
    print(f"Current (latest) analyses: {stats.get('latest_analyses', 0)}")
    print(f"Total changes tracked: {stats.get('total_changes', 0)}")
    print(f"Changes in last 24h: {stats.get('recent_changes_24h', 0)}")

    if stats.get('oldest_record'):
        print(f"Oldest record: {format_timestamp(stats.get('oldest_record'))}")

    signal_dist = stats.get('signal_distribution', {})
    if signal_dist:
        print("\nCurrent Signal Distribution:")
        total = sum(signal_dist.values())
        for signal, count in signal_dist.items():
            emoji = AnalysisComparison.get_signal_emoji(signal)
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {emoji} {signal}: {count} ({percentage:.1f}%)")

    print("\n" + "=" * 80)


def print_cleanup_info(db: AnalysisDB):
    """Print cleanup information"""
    print("\n" + "=" * 80)
    print("🧹 DATA ROTATION & CLEANUP")
    print("=" * 80)

    stats = db.get_stats()

    print("\nConfiguration:")
    print("  • Retention Period: 7 days")
    print("  • Cleanup Schedule: Daily (automatic)")
    print("  • Latest analyses: Always kept")

    print("\nCurrent Status:")
    print(f"  • Total stored: {stats.get('total_analyses', 0)} analyses")
    print(f"  • Latest: {stats.get('latest_analyses', 0)} analyses")
    print(f"  • Historical: {stats.get('total_analyses', 0) - stats.get('latest_analyses', 0)} analyses")

    if stats.get('oldest_record'):
        oldest = datetime.fromisoformat(stats.get('oldest_record'))
        age_days = (datetime.now() - oldest).days
        print(f"  • Oldest record: {age_days} days old")

    print("\nTo manually run cleanup:")
    print("  python -c \"from src.database.analysis_db import AnalysisDB; AnalysisDB().cleanup_old_data(7)\"")

    print("\n" + "=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='View Forex Analysis History')

    parser.add_argument('--asset', '-a', help='Asset symbol (e.g., EURUSD=X, BTC/USD)')
    parser.add_argument('--timeframe', '-t', default='1d', help='Timeframe (default: 1d)')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back for changes (default: 24)')
    parser.add_argument('--days', '-d', type=int, default=7, help='Days to look back for history (default: 7)')

    parser.add_argument('--latest', '-l', action='store_true', help='Show latest analyses')
    parser.add_argument('--changes', '-c', action='store_true', help='Show recent changes')
    parser.add_argument('--history', action='store_true', help='Show analysis history')
    parser.add_argument('--stats', '-s', action='store_true', help='Show database statistics')
    parser.add_argument('--cleanup-info', action='store_true', help='Show cleanup information')

    args = parser.parse_args()

    # Initialize database
    db = AnalysisDB()

    # If no action specified, show latest
    if not any([args.latest, args.changes, args.history, args.stats, args.cleanup_info]):
        args.latest = True

    # Execute actions
    if args.latest:
        print_latest_analyses(db, args.asset)

    if args.changes:
        print_recent_changes(db, args.asset, args.hours)

    if args.history:
        if not args.asset:
            print("Error: --history requires --asset to be specified")
            sys.exit(1)
        print_history(db, args.asset, args.timeframe, args.days)

    if args.stats:
        print_stats(db)

    if args.cleanup_info:
        print_cleanup_info(db)


if __name__ == '__main__':
    main()
