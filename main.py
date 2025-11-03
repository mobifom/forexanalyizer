#!/usr/bin/env python3
"""
Forex Analyzer CLI
Command-line interface for the forex forecasting application
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.forex_analyzer import ForexAnalyzer


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Forex Forecasting Application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Analyze a single pair
  python main.py analyze --symbol EURUSD=X

  # Analyze with custom account balance
  python main.py analyze --symbol EURUSD=X --balance 5000

  # Scan multiple pairs from config
  python main.py scan

  # Scan specific pairs
  python main.py scan --pairs EURUSD=X GBPUSD=X USDJPY=X

  # Train the ML model
  python main.py train --symbol EURUSD=X

  # Analyze without ML
  python main.py analyze --symbol EURUSD=X --no-ml
        '''
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single forex pair')
    analyze_parser.add_argument(
        '--symbol', '-s',
        type=str,
        default='EURUSD=X',
        help='Forex pair symbol (default: EURUSD=X)'
    )
    analyze_parser.add_argument(
        '--balance', '-b',
        type=float,
        default=10000.0,
        help='Account balance for position sizing (default: 10000)'
    )
    analyze_parser.add_argument(
        '--no-ml',
        action='store_true',
        help='Disable ML predictions'
    )
    analyze_parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan multiple forex pairs')
    scan_parser.add_argument(
        '--pairs', '-p',
        nargs='+',
        help='List of pairs to scan (uses config if not specified)'
    )
    scan_parser.add_argument(
        '--balance', '-b',
        type=float,
        default=10000.0,
        help='Account balance for position sizing (default: 10000)'
    )
    scan_parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )

    # Train command
    train_parser = subparsers.add_parser('train', help='Train the ML model')
    train_parser.add_argument(
        '--symbol', '-s',
        type=str,
        default='EURUSD=X',
        help='Forex pair to train on (default: EURUSD=X)'
    )
    train_parser.add_argument(
        '--output', '-o',
        type=str,
        default='models/forex_model.pkl',
        help='Path to save trained model'
    )
    train_parser.add_argument(
        '--config', '-c',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Initialize analyzer
        analyzer = ForexAnalyzer(config_path=args.config)

        if args.command == 'analyze':
            print(f"\nAnalyzing {args.symbol}...")
            print("=" * 70)

            # Perform analysis
            analysis = analyzer.analyze_pair(
                symbol=args.symbol,
                account_balance=args.balance,
                use_ml=not args.no_ml
            )

            # Generate and print report
            report = analyzer.generate_report(analysis)
            print(report)

        elif args.command == 'scan':
            print("\nScanning forex pairs...")
            print("=" * 70)

            # Scan pairs
            results = analyzer.scan_multiple_pairs(
                pairs=args.pairs,
                account_balance=args.balance
            )

            # Print summary
            print("\n" + "=" * 70)
            print("SCAN SUMMARY")
            print("=" * 70)

            for pair, analysis in results.items():
                if 'error' in analysis:
                    print(f"\n{pair}: ERROR - {analysis['error']}")
                else:
                    final = analysis['final_decision']
                    trade_plan = analysis.get('trade_plan')

                    print(f"\n{pair}:")
                    print(f"  Signal: {final['signal']} (Confidence: {final['confidence']:.2%})")

                    if trade_plan and trade_plan.get('approved'):
                        print(f"  Entry: {trade_plan['entry_price']:.5f}")
                        print(f"  Stop Loss: {trade_plan['stop_loss']:.5f}")
                        print(f"  Take Profit: {trade_plan['take_profit']:.5f}")
                        print(f"  Position: {trade_plan['position_size_lots']:.2f} lots")
                        print(f"  Risk: ${trade_plan['risk_amount']:.2f}")

            print("\n" + "=" * 70)

        elif args.command == 'train':
            print(f"\nTraining ML model on {args.symbol}...")
            print("=" * 70)

            # Train model
            results = analyzer.train_model(
                symbol=args.symbol,
                save_path=args.output
            )

            if results:
                print("\nTraining Results:")
                print(f"  Train Accuracy: {results.get('train_score', 0):.2%}")
                print(f"  Test Accuracy: {results.get('test_score', 0):.2%}")
                print(f"  Features Used: {results.get('feature_count', 0)}")
                print(f"\nModel saved to: {args.output}")
            else:
                print("\nTraining failed. Check logs for details.")

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
