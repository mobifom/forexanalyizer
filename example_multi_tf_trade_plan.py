"""
Example: Generate Multi-Timeframe Trade Plans
Demonstrates how to use the new create_multi_timeframe_trade_plans method
"""

import sys
import yaml
import json
from datetime import datetime

from src.data.data_fetcher import ForexDataFetcher
from src.risk.risk_manager import RiskManager
from src.indicators.technical_indicators import TechnicalIndicators


def print_separator(char='=', length=80):
    """Print a separator line"""
    print(char * length)


def print_timeframe_plan(tf, plan):
    """Pretty print a timeframe-specific trade plan"""
    print(f"\n{'='*80}")
    print(f"TIMEFRAME: {tf.upper()} - {plan['timeframe_description']}")
    print(f"{'='*80}")

    # Trading Strategy
    strategy = plan['trading_strategy']
    print(f"\n📊 TRADING STRATEGY:")
    print(f"   Style: {strategy['style']}")
    print(f"   Holding Period: {strategy['holding_period']}")
    print(f"   Description: {strategy['description']}")
    print(f"   Monitoring: {strategy['monitoring']}")
    print(f"   Suitable For: {strategy['suitable_for']}")

    # Expected Execution
    execution = plan['expected_execution']
    print(f"\n⏱️  EXPECTED EXECUTION TIME:")
    print(f"   Duration: {execution['duration_readable']}")
    print(f"   Estimated Completion: {execution['estimated_completion_readable']}")
    print(f"   Candles to Target: {execution['candles_to_target']}")

    # Entry Points
    print(f"\n🎯 ENTRY POINTS:")
    for entry_name, entry_data in plan['entry_points'].items():
        marker = "⭐" if 'immediate' in entry_name else "📌"
        print(f"   {marker} {entry_name.replace('_', ' ').title()}:")
        print(f"      Price: {entry_data['price']}")
        print(f"      Description: {entry_data['description']}")
        print(f"      Type: {entry_data['type']} ({entry_data['urgency']})")

    # Stop Losses
    print(f"\n🛑 STOP LOSS OPTIONS:")
    for sl_name, sl_data in plan['stop_losses'].items():
        marker = "⭐" if sl_data.get('recommended') else "  "
        print(f"   {marker} {sl_name.replace('_', ' ').title()}:")
        print(f"      Price: {sl_data['price']}")
        print(f"      Risk: {sl_data['risk_pct']}%")
        print(f"      Description: {sl_data['description']}")

    # Take Profit Targets
    print(f"\n💰 TAKE PROFIT TARGETS:")
    for tp_name, tp_data in plan['take_profits'].items():
        marker = "⭐" if tp_data.get('recommended') else "  "
        rr_ratio = plan['risk_reward_ratios'].get(tp_name, 'N/A')
        print(f"   {marker} {tp_name.replace('_', ' ').title()}:")
        print(f"      Price: {tp_data['price']}")
        print(f"      Gain: {tp_data['gain_pct']}%")
        print(f"      Risk/Reward: 1:{rr_ratio}")
        print(f"      Position Close: {tp_data['position_close_pct']}%")
        print(f"      Description: {tp_data['description']}")

    # Position Sizing
    position = plan['position_sizing']
    print(f"\n💵 POSITION SIZING:")
    print(f"   Position Size: {position['position_size_lots']:.4f} lots ({position['position_size_units']:.0f} units)")
    print(f"   Risk Amount: ${position['risk_amount']:.2f}")
    print(f"   Risk Percentage: {position['risk_percentage']:.2f}%")

    # Current Indicators
    if plan['current_indicators']:
        print(f"\n📈 CURRENT INDICATORS:")
        indicators = plan['current_indicators']
        if 'RSI' in indicators:
            print(f"   RSI: {indicators['RSI']}")
        if 'MACD' in indicators:
            print(f"   MACD: {indicators['MACD']} | Signal: {indicators.get('MACD_Signal', 'N/A')}")
        if 'MA_20' in indicators:
            print(f"   MA 20: {indicators['MA_20']} | MA 50: {indicators.get('MA_50', 'N/A')}")
        if 'ATR' in indicators:
            print(f"   ATR: {indicators['ATR']}")


def main():
    """Main function to demonstrate multi-timeframe trade plans"""

    # Load configuration
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Parameters
    symbol = 'EURUSD=X'  # Yahoo Finance format for EUR/USD
    timeframes = ['15m', '1h', '4h', '1d']
    account_balance = 10000  # $10,000 account

    print_separator()
    print(f"MULTI-TIMEFRAME TRADE PLAN GENERATOR")
    print_separator()
    print(f"Symbol: {symbol}")
    print(f"Account Balance: ${account_balance:,.2f}")
    print(f"Timeframes: {', '.join(timeframes)}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()

    # Initialize components
    data_fetcher = ForexDataFetcher(
        cache_dir='data/cache',
        cache_duration_minutes=config.get('data', {}).get('cache_duration_minutes', 60)
    )
    risk_manager = RiskManager(config)
    tech_indicators = TechnicalIndicators()

    # Fetch data for all timeframes
    print("\nFetching market data for all timeframes...")
    dataframes = {}

    for tf in timeframes:
        print(f"  Fetching {tf} data...", end=' ')
        df = data_fetcher.fetch_data(symbol, tf)

        if df is not None and not df.empty:
            # Calculate indicators
            df = tech_indicators.add_all_indicators(df)
            dataframes[tf] = df
            print("✓")
        else:
            print("✗ (Failed)")

    if not dataframes:
        print("ERROR: Could not fetch data for any timeframe")
        return

    # Get current price from the most recent data
    current_price = None
    for tf in timeframes:
        if tf in dataframes and not dataframes[tf].empty:
            current_price = dataframes[tf]['Close'].iloc[-1]
            break

    if current_price is None:
        print("ERROR: Could not determine current price")
        return

    print(f"\nCurrent Price: {current_price}")

    # For this example, let's assume a BUY signal with 75% confidence
    signal = 'BUY'
    confidence = 0.75

    print(f"Signal: {signal}")
    print(f"Confidence: {confidence:.1%}")

    # Generate multi-timeframe trade plans
    print("\nGenerating multi-timeframe trade plans...")

    multi_tf_plans = risk_manager.create_multi_timeframe_trade_plans(
        signal=signal,
        entry_price=current_price,
        confidence=confidence,
        account_balance=account_balance,
        dataframes=dataframes,
        timeframes=timeframes
    )

    # Check if approved
    if not multi_tf_plans['approved']:
        print("\n❌ TRADE NOT APPROVED")
        print("Reasons:")
        for reason in multi_tf_plans['reasons']:
            print(f"  - {reason}")
        return

    print("\n✅ TRADE APPROVED")

    # Print summary
    print_separator()
    print("TRADE PLAN SUMMARY")
    print_separator()
    print(f"Signal: {multi_tf_plans['signal']}")
    print(f"Confidence: {multi_tf_plans['confidence']:.1%}")
    print(f"Entry Price: {multi_tf_plans['entry_price']}")
    print(f"Generated At: {multi_tf_plans['generated_at']}")
    print(f"Number of Timeframes: {len(multi_tf_plans['timeframe_plans'])}")

    # Print each timeframe plan
    for tf, plan in multi_tf_plans['timeframe_plans'].items():
        print_timeframe_plan(tf, plan)

    # Print comparison table
    print(f"\n{'='*80}")
    print("QUICK COMPARISON TABLE")
    print(f"{'='*80}")
    print(f"{'Timeframe':<12} | {'Style':<20} | {'Duration':<25} | {'Best R:R':<10}")
    print(f"{'-'*80}")

    for tf, plan in multi_tf_plans['timeframe_plans'].items():
        strategy = plan['trading_strategy']
        execution = plan['expected_execution']
        best_rr = max(plan['risk_reward_ratios'].values()) if plan['risk_reward_ratios'] else 0

        print(f"{tf.upper():<12} | {strategy['style']:<20} | {execution['duration_readable']:<25} | 1:{best_rr:.2f}")

    print(f"{'='*80}")

    # Save to JSON file for reference
    output_file = f"trade_plan_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(multi_tf_plans, f, indent=2)

    print(f"\n💾 Trade plan saved to: {output_file}")
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
