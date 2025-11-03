# Multi-Timeframe Trade Plans

The ForexAnalyzer now supports **multi-timeframe trade plans** that provide comprehensive trading strategies across different time horizons.

## Overview

When the analyzer generates a BUY or SELL signal, it automatically creates detailed trade plans for 4 different timeframes:

- **15 Minutes** - Scalping (Quick in and out)
- **1 Hour** - Intraday Trading
- **4 Hours** - Swing Trading
- **1 Day** - Position Trading

Each timeframe plan includes:
- Multiple entry point options
- Multiple stop loss levels
- Multiple take profit targets
- Position sizing calculations
- Expected execution time
- Risk/reward ratios
- Trading strategy recommendations

## How to Access

### 1. **Streamlit Web App** (Recommended)

```bash
streamlit run app.py
```

1. Enter a currency pair (e.g., EURUSD=X, GBPUSD=X)
2. Click "🔍 Analyze"
3. Navigate to the **"💼 Multi-Timeframe Trade Plans"** tab
4. You'll see tabs for each timeframe: **⏰ 15M**, **⏰ 1H**, **⏰ 4H**, **⏰ 1D**

### 2. **Python API**

```python
from src.forex_analyzer import ForexAnalyzer

# Initialize analyzer
analyzer = ForexAnalyzer()

# Analyze a currency pair
result = analyzer.analyze_pair('EURUSD=X', account_balance=10000)

# Access multi-timeframe plans
if result.get('multi_tf_trade_plans'):
    plans = result['multi_tf_trade_plans']

    # Check if approved
    if plans['approved']:
        # Iterate through each timeframe
        for tf, plan in plans['timeframe_plans'].items():
            print(f"\n{tf.upper()} Plan:")
            print(f"  Style: {plan['trading_strategy']['style']}")
            print(f"  Expected Duration: {plan['expected_execution']['duration_readable']}")

            # Entry points
            for entry_name, entry_data in plan['entry_points'].items():
                print(f"  {entry_name}: ${entry_data['price']}")

            # Stop losses
            for sl_name, sl_data in plan['stop_losses'].items():
                print(f"  {sl_name}: ${sl_data['price']} (Risk: {sl_data['risk_pct']}%)")

            # Take profits
            for tp_name, tp_data in plan['take_profits'].items():
                print(f"  {tp_name}: ${tp_data['price']} (Gain: {tp_data['gain_pct']}%)")
```

### 3. **Example Script**

Run the included example script:

```bash
python example_multi_tf_trade_plan.py
```

This will:
- Fetch data for all timeframes
- Generate comprehensive trade plans
- Display detailed information for each timeframe
- Save the plans to a JSON file

## Features by Timeframe

### 15 Minutes (Scalping)
- **Style**: Scalping
- **Holding Period**: 15 minutes to 2 hours
- **Expected Duration**: ~5 hours
- **Monitoring**: Requires active monitoring
- **Suitable For**: Day traders, active traders
- **Stop Loss Range**: 0.03% - 0.1%
- **Take Profit Range**: 0.03% - 0.16%

### 1 Hour (Intraday)
- **Style**: Intraday Trading
- **Holding Period**: 1 hour to 8 hours
- **Expected Duration**: ~1 day
- **Monitoring**: Check every 1-2 hours
- **Suitable For**: Day traders, part-time traders
- **Stop Loss Range**: 0.1% - 0.31%
- **Take Profit Range**: 0.1% - 0.52%

### 4 Hours (Swing)
- **Style**: Swing Trading
- **Holding Period**: 4 hours to 3 days
- **Expected Duration**: ~3 days
- **Monitoring**: Check 2-3 times per day
- **Suitable For**: Swing traders, working professionals
- **Stop Loss Range**: 0.24% - 0.72%
- **Take Profit Range**: 0.24% - 1.19%

### 1 Day (Position)
- **Style**: Position Trading
- **Holding Period**: 1 day to several weeks
- **Expected Duration**: ~10 days
- **Monitoring**: Check once per day
- **Suitable For**: Position traders, long-term investors
- **Stop Loss Range**: 0.48% - 1.43%
- **Take Profit Range**: 0.48% - 2.38%

## Entry Point Options

Each timeframe provides 3 entry point options:

### 1. **Immediate Entry** ⚡
- **Type**: Market Order
- **Price**: Current market price
- **When to use**: Strong signal, enter immediately
- **Urgency**: IMMEDIATE

### 2. **Pullback Entry** 📝
- **Type**: Limit Order
- **Price**: Entry on minor pullback (0.5x ATR)
- **When to use**: Wait for better price
- **Urgency**: LIMIT ORDER

### 3. **Best Entry** 📝
- **Type**: Limit Order
- **Price**: Near support/resistance (Bollinger Bands)
- **When to use**: Patient traders, best risk/reward
- **Urgency**: LIMIT ORDER

## Stop Loss Options

Each timeframe offers 5 stop loss levels:

### 1. **Tight (1x ATR)**
- Quick exit if wrong
- Lower risk, higher chance of being stopped out
- **Risk**: ~0.03% - 0.48% (depending on timeframe)

### 2. **Standard (2x ATR)** ⭐ RECOMMENDED
- Allows for normal market volatility
- Balanced approach
- **Risk**: ~0.06% - 0.96% (depending on timeframe)

### 3. **Wide (3x ATR)**
- More breathing room
- Higher risk, less chance of being stopped out
- **Risk**: ~0.1% - 1.43% (depending on timeframe)

### 4. **Percentage-based (2%)**
- Fixed 2% risk regardless of volatility
- Simple and consistent

### 5. **Percentage-based (3%)**
- Fixed 3% risk for more aggressive traders
- Higher risk, higher potential reward

## Take Profit Targets

Each timeframe provides 4 take profit levels with position scaling:

### 1. **TP1 - Quick/Scalp**
- **Distance**: 1x ATR
- **Position Close**: 25%
- **Purpose**: Lock in quick profit
- **R:R**: Typically 1:0.5

### 2. **TP2 - Conservative** ⭐ RECOMMENDED
- **Distance**: 2x ATR
- **Position Close**: 25%
- **Purpose**: Conservative target
- **R:R**: Typically 1:1.0

### 3. **TP3 - Moderate**
- **Distance**: 3x ATR
- **Position Close**: 25%
- **Purpose**: Medium-term target
- **R:R**: Typically 1:1.5

### 4. **TP4 - Aggressive**
- **Distance**: 5x ATR
- **Position Close**: 25%
- **Purpose**: Let it run!
- **R:R**: Typically 1:2.5

## Position Sizing

Position sizing is calculated based on the **Standard (2x ATR)** stop loss:

- **Default Risk**: 2% of account balance
- **Calculation**: Risk Amount / Stop Loss Distance
- **Units**: Displayed in both lots and currency units

Example for $10,000 account:
- **Risk Amount**: $200 (2% of $10,000)
- **Entry**: $1.15433
- **Stop Loss**: $1.15193 (2x ATR)
- **Risk per unit**: $0.0024
- **Position Size**: 83,176 units = 0.83 lots

## Expected Execution Time

Each plan includes estimated execution time based on:
- Number of candles to reach TP2 target
- Timeframe duration
- Historical volatility (ATR)

**Example:**
- **15m timeframe**: 20 candles × 15 minutes = 5 hours
- **1h timeframe**: 24 candles × 1 hour = 1 day
- **4h timeframe**: 18 candles × 4 hours = 3 days
- **1d timeframe**: 10 candles × 1 day = 10 days

## Trading Strategy Recommendations

### For Scalpers (15m)
✅ Use tight stops (1x ATR)
✅ Take quick profits (TP1, TP2)
✅ Active monitoring required
✅ Multiple trades per day

### For Day Traders (1h)
✅ Use standard stops (2x ATR)
✅ Target TP2-TP3
✅ Check every 1-2 hours
✅ Close all positions by EOD

### For Swing Traders (4h)
✅ Use standard to wide stops (2-3x ATR)
✅ Target TP3-TP4
✅ Check 2-3 times daily
✅ Hold for 1-3 days

### For Position Traders (1d)
✅ Use wide stops (3x ATR)
✅ Target TP4 and beyond
✅ Check once daily
✅ Hold for weeks

## Risk Management

All plans follow these risk management principles:

1. **Maximum risk per trade**: 2% of account (configurable)
2. **Risk/Reward ratio**: Minimum 1:1.5
3. **Position scaling**: Close 25% at each TP level
4. **ATR-based stops**: Adaptive to market volatility
5. **Multiple timeframe confirmation**: Only trade when multiple TFs align

## Notes

- **Trade plans are only generated for BUY and SELL signals** (not for HOLD)
- **All plans require signal confidence ≥ 60%** (configurable)
- **Plans respect maximum drawdown limits** (default: 15%)
- **ATR values are specific to each timeframe**, so stop losses and take profits are optimized for that timeframe's volatility

## Configuration

You can customize the risk management settings in `config/config.yaml`:

```yaml
risk_management:
  risk_per_trade: 0.02          # 2% risk per trade
  atr_multiplier: 2.0           # Standard stop at 2x ATR
  min_risk_reward: 1.5          # Minimum R:R ratio
  max_drawdown: 0.15            # Maximum 15% drawdown
```

## Example Output

When you view the multi-timeframe trade plans in the Streamlit app, you'll see:

**Trade Summary**
- Signal: BUY
- Confidence: 75%
- Entry Price: $1.15433
- Timeframes: 4

**Tabs for each timeframe:**

**⏰ 15M** | **⏰ 1H** | **⏰ 4H** | **⏰ 1D**

Each tab shows:
- 🎯 Entry Points (3 options)
- 🛑 Stop Loss Options (5 levels)
- 💰 Take Profit Targets (4 levels with R:R ratios)
- 💵 Position Sizing
- 📈 Current Technical Indicators
- ⏱️ Expected Execution Time

## Tips for Success

1. **Choose the right timeframe for your trading style**
   - Scalpers → 15m
   - Day traders → 1h
   - Swing traders → 4h
   - Position traders → 1d

2. **Use multiple entry points**
   - Enter partial position immediately
   - Add on pullbacks for better average price

3. **Scale out at profit targets**
   - Close 25% at each TP level
   - Protect profits while letting winners run

4. **Respect the stop loss**
   - Choose appropriate stop for your risk tolerance
   - Never widen stops after entry

5. **Monitor according to timeframe**
   - Don't check 1d positions every 15 minutes
   - Match monitoring frequency to holding period

## Troubleshooting

**Q: I don't see multi-timeframe plans**
- A: Plans are only generated for BUY/SELL signals, not HOLD
- Check that the signal confidence is ≥ 60%
- Ensure you're on the "💼 Multi-Timeframe Trade Plans" tab

**Q: Some timeframes are missing**
- A: Data might not be available for all timeframes
- Try analyzing a more liquid pair (e.g., EURUSD=X, GBPUSD=X)

**Q: Expected duration seems too long/short**
- A: Estimates are based on historical volatility (ATR)
- Actual execution time may vary based on market conditions

## Support

For issues or questions:
- Check the example script: `python example_multi_tf_trade_plan.py`
- Review the code: `src/risk/risk_manager.py` (line 269)
- Open an issue on GitHub

---

**Happy Trading! 📈**
