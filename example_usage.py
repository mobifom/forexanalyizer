#!/usr/bin/env python3
"""
Example Usage Script
Demonstrates how to use the Forex Analyzer programmatically
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.forex_analyzer import ForexAnalyzer


def example_1_basic_analysis():
    """Example 1: Basic single pair analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Analysis")
    print("="*70)

    # Initialize analyzer
    analyzer = ForexAnalyzer()

    # Analyze EURUSD
    analysis = analyzer.analyze_pair(
        symbol='EURUSD=X',
        account_balance=10000.0,
        use_ml=False  # Start without ML
    )

    # Print report
    report = analyzer.generate_report(analysis)
    print(report)


def example_2_with_ml():
    """Example 2: Analysis with ML model"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Analysis with ML Model")
    print("="*70)

    analyzer = ForexAnalyzer()

    # Check if model exists, if not train it
    if not os.path.exists('models/forex_model.pkl'):
        print("\nModel not found. Training now...")
        analyzer.train_model('EURUSD=X')

    # Analyze with ML
    analysis = analyzer.analyze_pair(
        symbol='EURUSD=X',
        account_balance=10000.0,
        use_ml=True
    )

    report = analyzer.generate_report(analysis)
    print(report)


def example_3_scan_multiple():
    """Example 3: Scan multiple pairs including gold and silver"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Scan Multiple Pairs (Including Gold & Silver)")
    print("="*70)

    analyzer = ForexAnalyzer()

    pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'XAU_USD', 'XAG_USD']

    results = analyzer.scan_multiple_pairs(
        pairs=pairs,
        account_balance=10000.0
    )

    # Print summary
    print("\n" + "="*70)
    print("SCAN RESULTS SUMMARY")
    print("="*70)

    for pair, analysis in results.items():
        if 'error' in analysis:
            print(f"\n{pair}: ERROR - {analysis['error']}")
            continue

        final = analysis['final_decision']
        consensus = analysis['multi_timeframe_consensus']

        print(f"\n{pair}:")
        print(f"  Price: {analysis['current_price']:.5f}")
        print(f"  Signal: {final['signal']} ({final['confidence']:.2%} confidence)")
        print(f"  Consensus: {consensus['agreement_count']}/{consensus['total_timeframes']} timeframes agree")

        # Show trade plan if available
        if analysis.get('trade_plan') and analysis['trade_plan'].get('approved'):
            tp = analysis['trade_plan']
            print(f"  Entry: {tp['entry_price']:.5f}")
            print(f"  Stop Loss: {tp['stop_loss']:.5f}")
            print(f"  Take Profit: {tp['take_profit']:.5f}")
            print(f"  Risk: ${tp['risk_amount']:.2f}")


def example_4_custom_analysis():
    """Example 4: Custom analysis with specific settings"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Access Detailed Analysis Data")
    print("="*70)

    analyzer = ForexAnalyzer()

    analysis = analyzer.analyze_pair('EURUSD=X', use_ml=False)

    if 'error' in analysis:
        print(f"Error: {analysis['error']}")
        return

    # Access specific timeframe data
    print("\nDetailed 1D Timeframe Analysis:")
    print("-" * 70)

    if '1d' in analysis['timeframe_analyses']:
        tf_1d = analysis['timeframe_analyses']['1d']

        print(f"Current Price: {tf_1d['current_data']['price']:.5f}")
        print(f"RSI: {tf_1d['current_data']['rsi']:.2f}")
        print(f"MACD: {tf_1d['current_data']['macd']:.5f}")
        print(f"ATR: {tf_1d['current_data']['atr']:.5f}")
        print(f"\nTrend Strength: {tf_1d['trend_strength']:.2%}")
        print(f"Momentum: {tf_1d['momentum']}")

        print("\nIndividual Signals:")
        for signal_name, signal_value in tf_1d['signals'].items():
            print(f"  {signal_name}: {signal_value}")

        print("\nSupport Levels:")
        for i, level in enumerate(tf_1d['support_levels'][:3], 1):
            print(f"  S{i}: {level:.5f}")

        print("\nResistance Levels:")
        for i, level in enumerate(tf_1d['resistance_levels'][:3], 1):
            print(f"  R{i}: {level:.5f}")


def example_5_risk_analysis():
    """Example 5: Focus on risk management"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Risk Management Analysis")
    print("="*70)

    analyzer = ForexAnalyzer()

    # Analyze with different account sizes
    account_sizes = [1000, 5000, 10000, 50000]

    for balance in account_sizes:
        analysis = analyzer.analyze_pair(
            'EURUSD=X',
            account_balance=balance,
            use_ml=False
        )

        if 'error' in analysis or not analysis.get('trade_plan'):
            continue

        tp = analysis['trade_plan']

        if tp.get('approved'):
            print(f"\nAccount Balance: ${balance:,.2f}")
            print(f"  Position Size: {tp['position_size_lots']:.2f} lots")
            print(f"  Risk Amount: ${tp['risk_amount']:.2f} ({tp['risk_percentage']:.2f}%)")
            print(f"  Potential Profit: ${tp['potential_profit']:.2f}")
            print(f"  Risk:Reward: 1:{tp['risk_reward_ratio']:.2f}")


def main():
    """Run all examples"""
    print("\n")
    print("#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  FOREX ANALYZER - EXAMPLE USAGE DEMONSTRATIONS".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)

    try:
        # Run examples
        example_1_basic_analysis()

        # Uncomment to run other examples:
        # example_2_with_ml()
        # example_3_scan_multiple()
        # example_4_custom_analysis()
        # example_5_risk_analysis()

        print("\n" + "="*70)
        print("Examples completed successfully!")
        print("="*70)
        print("\nTip: Uncomment other examples in the main() function to try them.")

    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
