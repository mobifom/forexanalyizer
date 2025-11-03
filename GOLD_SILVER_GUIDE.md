# Gold and Silver Trading Guide

This guide explains how to use the Forex Analyzer for precious metals (Gold and Silver) trading.

## Supported Symbols

The application supports the following precious metals symbols:

- **GC=F** - Gold / US Dollar (spot price)
- **SI=F** - Silver / US Dollar (spot price)

These are the standard forex symbols for gold and silver trading against the US Dollar.

## Quick Start

### Analyze Gold

```bash
python main.py analyze --symbol GC=F
```

### Analyze Silver

```bash
python main.py analyze --symbol SI=F
```

### Train ML Model on Gold

```bash
python main.py train --symbol GC=F
```

### Scan Both Metals

```bash
python main.py scan --pairs GC=F SI=F
```

### Combined Scan (Forex + Metals)

```bash
python main.py scan --pairs EURUSD=X GBPUSD=X GC=F SI=F
```

## Understanding Gold/Silver Analysis

### Price Levels

Gold and silver prices are quoted differently than currency pairs:

- **Gold (XAUUSD)**: Price per troy ounce in USD
  - Example: 2050.50 means $2,050.50 per ounce

- **Silver (XAGUSD)**: Price per troy ounce in USD
  - Example: 24.75 means $24.75 per ounce

### Position Sizing for Metals

The application calculates position sizes appropriately for metals:

- **Standard Lot**: 100 troy ounces
- **Mini Lot**: 10 troy ounces
- **Micro Lot**: 1 troy ounce

Example output:
```
Position Size: 0.50 lots (50 ounces)
```

### Risk Management for Metals

Precious metals can be more volatile than currency pairs, so:

1. **ATR-based stops** adapt to volatility automatically
2. **Position sizing** adjusts based on metal price
3. **Risk percentage** remains consistent (default 2%)

## Example: Gold Analysis

```bash
python main.py analyze --symbol GC=F --balance 10000
```

Sample output:
```
FINAL RECOMMENDATION
Signal: BUY
Confidence: 72.50%

TRADE PLAN
Entry Price: 2050.50
Stop Loss: 2035.25    (ATR-based)
Take Profit: 2073.38  (1:1.5 R:R)
Position Size: 1.30 lots (130 ounces)
Risk Amount: $200.00 (2.00%)
Potential Profit: $300.00
Risk:Reward Ratio: 1:1.50
```

## Gold/Silver Specific Considerations

### 1. Market Hours

Unlike 24/5 forex, gold and silver markets have specific characteristics:
- Most liquid during US and European hours
- Can have gaps over weekends
- News events heavily impact prices (FOMC, inflation data, etc.)

### 2. Correlation Analysis

Gold and silver often move together, but not always:
- **High correlation periods**: Both trending same direction
- **Divergence**: Silver may lag or lead gold
- Use the scanner to find the best opportunities

### 3. Fundamental Factors

The technical analysis works well, but be aware of:
- **Dollar strength**: Inverse relationship
- **Inflation expectations**: Direct relationship
- **Geopolitical events**: Flight to safety
- **Industrial demand** (especially silver): Economic indicators

## Advanced Usage

### Train Separate Models

Train dedicated models for each metal:

```bash
# Gold model
python main.py train --symbol GC=F --output models/gold_model.pkl

# Silver model
python main.py train --symbol SI=F --output models/silver_model.pkl
```

### Custom Configuration for Metals

Create a custom config file `config/metals_config.yaml`:

```yaml
# Focus only on metals
currency_pairs:
  - 'GC=F'
  - 'SI=F'

# Adjust for metal volatility
risk_management:
  risk_per_trade: 0.015      # 1.5% for more volatile metals
  atr_multiplier: 2.5        # Wider stops
  min_risk_reward: 2.0       # Higher reward targets

# Metal-specific indicator tuning
indicators:
  ma_periods: [20, 50, 100]  # Shorter MAs for faster moves
  rsi_period: 14
  atr_period: 14
```

Then use it:
```bash
python main.py analyze --symbol GC=F --config config/metals_config.yaml
```

## Test Gold/Silver Support

Run the test script to verify connectivity:

```bash
python test_gold_silver.py
```

This will:
- Fetch current gold data
- Fetch current silver data
- Display latest prices
- Verify all features work correctly

## Programmatic Usage

```python
from src.forex_analyzer import ForexAnalyzer

# Initialize analyzer
analyzer = ForexAnalyzer()

# Analyze gold
gold_analysis = analyzer.analyze_pair('GC=F', account_balance=10000)

# Analyze silver
silver_analysis = analyzer.analyze_pair('SI=F', account_balance=10000)

# Print reports
print(analyzer.generate_report(gold_analysis))
print(analyzer.generate_report(silver_analysis))

# Compare opportunities
if gold_analysis['final_decision']['confidence'] > silver_analysis['final_decision']['confidence']:
    print("Gold has stronger signal")
else:
    print("Silver has stronger signal")
```

## Tips for Trading Gold and Silver

1. **Use Longer Timeframes**: Daily and 4H signals are often more reliable for metals
2. **Watch the Dollar**: Strong inverse correlation with USD/DXY
3. **Respect Volatility**: Metals can gap significantly
4. **Consider Both**: Sometimes silver leads, sometimes gold leads
5. **Economic Calendar**: Be aware of key releases (CPI, FOMC, NFP)

## Example Workflow

### Morning Routine

```bash
# Scan all pairs including metals
python main.py scan --pairs EURUSD=X GBPUSD=X GC=F SI=F

# If gold shows strong signal, get details
python main.py analyze --symbol GC=F

# Review the complete report and trade plan
# Execute trade based on your broker platform
```

### Weekly Model Update

```bash
# Retrain on latest data
python main.py train --symbol GC=F
python main.py train --symbol SI=F
```

## Symbol Alternatives

If you have issues with the primary symbols, try these alternatives:

### Gold
- `GC=F` - Gold Futures (CME)
- `GOLD` - Some platforms (check your data provider)

### Silver
- `SI=F` - Silver Futures (CME)
- `SILVER` - Some platforms (check your data provider)

Note: You may need to modify the data fetcher if using alternative symbols.

## Troubleshooting

### "No data received for GC=F"

1. Check internet connection
2. Verify yfinance is installed: `pip install yfinance --upgrade`
3. Try the test script: `python test_gold_silver.py`
4. Try alternative symbol: `GC=F` for gold

### Position Sizes Seem Wrong

Gold and silver use different lot sizes than forex:
- This is normal - the calculator accounts for this
- 1 lot = 100 oz for metals
- Verify your broker's contract specifications

### High Volatility Warnings

Metals can be more volatile:
- The ATR-based stops handle this automatically
- Consider reducing risk per trade to 1-1.5%
- Use wider stop loss multipliers (2.5-3.0x ATR)

## Disclaimer

Gold and silver trading involves substantial risk:
- Prices can gap significantly
- Leverage magnifies both gains and losses
- This tool is for analysis only, not financial advice
- Always use proper risk management
- Consider starting with a demo account

## Support

For issues specific to gold/silver:
1. Run `python test_gold_silver.py` first
2. Check your data provider supports these symbols
3. Verify symbol format for your broker

Happy trading!
