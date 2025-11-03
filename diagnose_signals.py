"""
Diagnostic tool to understand signal differences across timeframes
"""

from src.forex_analyzer import ForexAnalyzer
from src.indicators.technical_indicators import TechnicalIndicators, SignalGenerator
import pandas as pd
from datetime import datetime

def diagnose_signals(symbol='EURUSD=X'):
    """Show why signals differ across timeframes"""

    print("=" * 80)
    print(f"SIGNAL DIAGNOSIS FOR {symbol}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    analyzer = ForexAnalyzer()

    # Fetch data for all timeframes
    timeframes = ['15m', '1h', '4h', '1d']

    for tf in timeframes:
        print(f"\n{'='*80}")
        print(f"TIMEFRAME: {tf.upper()}")
        print("="*80)

        # Fetch fresh data (no cache)
        df = analyzer.data_fetcher.fetch_data(symbol, tf, use_cache=False)

        if df is None or df.empty:
            print(f"  ❌ No data available")
            continue

        # Add indicators
        df = TechnicalIndicators.add_all_indicators(df, analyzer.config['indicators'])

        # Get last 3 candles
        recent = df.tail(3)

        print(f"\n📊 Last 3 Candles:")
        print(f"  Oldest: {recent.index[0]} - Close: ${recent['Close'].iloc[0]:.5f}")
        print(f"  Middle: {recent.index[1]} - Close: ${recent['Close'].iloc[1]:.5f}")
        print(f"  Latest: {recent.index[2]} - Close: ${recent['Close'].iloc[2]:.5f}")

        # Show indicators
        print(f"\n📈 Current Indicator Values:")

        if 'MA_20' in df.columns and 'MA_50' in df.columns:
            ma20 = df['MA_20'].iloc[-1]
            ma50 = df['MA_50'].iloc[-1]
            print(f"  MA 20: ${ma20:.5f}")
            print(f"  MA 50: ${ma50:.5f}")
            print(f"  Position: {'MA20 ABOVE MA50 ✅' if ma20 > ma50 else 'MA20 BELOW MA50 ❌'}")

        if 'RSI' in df.columns:
            rsi = df['RSI'].iloc[-1]
            rsi_prev = df['RSI'].iloc[-2]
            print(f"  RSI Current: {rsi:.2f}")
            print(f"  RSI Previous: {rsi_prev:.2f}")
            print(f"  RSI Change: {rsi - rsi_prev:+.2f}")

            if rsi < 30:
                print(f"  Status: OVERSOLD ⬇️")
            elif rsi > 70:
                print(f"  Status: OVERBOUGHT ⬆️")
            else:
                print(f"  Status: NEUTRAL ➡️")

        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            macd = df['MACD'].iloc[-1]
            macd_signal = df['MACD_Signal'].iloc[-1]
            macd_hist = df['MACD_Hist'].iloc[-1]
            print(f"  MACD: {macd:.5f}")
            print(f"  MACD Signal: {macd_signal:.5f}")
            print(f"  MACD Histogram: {macd_hist:.5f}")
            print(f"  Position: {'MACD ABOVE Signal ✅' if macd > macd_signal else 'MACD BELOW Signal ❌'}")

        # Generate signals
        signals = SignalGenerator.generate_all_signals(df, analyzer.config['indicators'])

        print(f"\n🎯 Generated Signals:")
        for indicator, signal in signals.items():
            emoji = "🟢" if signal == "BUY" else ("🔴" if signal == "SELL" else "🟡")
            print(f"  {emoji} {indicator}: {signal}")

        # Count signals
        buy_count = sum(1 for s in signals.values() if s == 'BUY')
        sell_count = sum(1 for s in signals.values() if s == 'SELL')
        hold_count = sum(1 for s in signals.values() if s == 'HOLD')

        print(f"\n📊 Signal Summary:")
        print(f"  BUY signals: {buy_count}/{len(signals)}")
        print(f"  SELL signals: {sell_count}/{len(signals)}")
        print(f"  HOLD signals: {hold_count}/{len(signals)}")

        # Overall consensus
        if buy_count > sell_count:
            overall = "BUY"
        elif sell_count > buy_count:
            overall = "SELL"
        else:
            overall = "HOLD"

        print(f"  Overall: {overall}")

        # Show why signals might differ
        print(f"\n💡 Why Signals May Differ:")
        print(f"  • Cache age: Data may be up to 10 minutes old")
        print(f"  • Candle timing: {tf.upper()} candles close at different times")
        print(f"  • Volatility: Shorter timeframes change faster")
        print(f"  • Data points: More recent candles = different momentum")

if __name__ == '__main__':
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'EURUSD=X'
    diagnose_signals(symbol)
