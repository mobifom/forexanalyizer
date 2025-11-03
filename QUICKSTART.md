# Quick Start Guide

Get up and running with the Forex Forecasting Application in 5 minutes!

## Installation

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

**Note**: If you see an error about MetaTrader5, that's normal on macOS/Linux. It's been removed from requirements and isn't needed. The app works great with yfinance!

**Having issues?** See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting.

## Basic Usage

### Step 1: Analyze a Forex Pair (Without ML)

Start with a simple technical analysis:

```bash
python main.py analyze --symbol EURUSD=X --no-ml
```

This will:
- Fetch data for EURUSD across 4 timeframes (1D, 4H, 1H, 15M)
- Calculate technical indicators
- Generate BUY/SELL/HOLD signal
- Provide a complete trade plan

### Step 2: Train the ML Model (Optional but Recommended)

For better predictions, train the machine learning model:

```bash
python main.py train --symbol EURUSD=X
```

This downloads historical data and trains an ensemble model. Takes 1-2 minutes.

### Step 3: Analyze with ML

Now analyze with both technical indicators AND ML:

```bash
python main.py analyze --symbol EURUSD=X
```

### Step 4: Scan Multiple Pairs

Find the best opportunities across multiple pairs:

```bash
python main.py scan --pairs EURUSD=X GBPUSD=X USDJPY=X AUDUSD=X
```

Or scan including gold and silver:

```bash
python main.py scan --pairs EURUSD=X GC=F SI=F
```

## Common Forex Symbols

For yfinance, forex pairs use the format: `XXXYYY=X`

### Popular Currency Pairs:
- `EURUSD=X` - Euro / US Dollar
- `GBPUSD=X` - British Pound / US Dollar
- `USDJPY=X` - US Dollar / Japanese Yen
- `AUDUSD=X` - Australian Dollar / US Dollar
- `USDCHF=X` - US Dollar / Swiss Franc
- `NZDUSD=X` - New Zealand Dollar / US Dollar
- `USDCAD=X` - US Dollar / Canadian Dollar

### Precious Metals (Commodities):
- `GC=F` - Gold / US Dollar
- `SI=F` - Silver / US Dollar

## Interpreting Results

### Signal Types
- **BUY**: Open a long position (buy the base currency)
- **SELL**: Open a short position (sell the base currency)
- **HOLD**: No clear signal, wait for better opportunity

### Confidence Score
- **> 70%**: Strong signal, high confidence
- **60-70%**: Moderate signal
- **< 60%**: Weak signal, trade may be rejected by risk manager

### Trade Plan
If approved, you'll see:
- **Entry Price**: Where to enter the trade
- **Stop Loss**: Exit if price moves against you (limit loss)
- **Take Profit**: Exit if price moves in your favor (secure profit)
- **Position Size**: How many lots/units to trade
- **Risk Amount**: Dollar amount at risk

## Example Output Walkthrough

```
FINAL RECOMMENDATION
Signal: BUY
Confidence: 75.50%
```
This means: Strong BUY signal with high confidence.

```
TRADE PLAN
Entry Price: 1.09450
Stop Loss: 1.09200
Take Profit: 1.09825
```
- Enter at 1.09450
- Exit at 1.09200 if it drops (25 pips loss)
- Exit at 1.09825 if it rises (37.5 pips profit)

```
Position Size: 0.80 lots
Risk Amount: $200.00 (2.00%)
```
- Trade 0.8 standard lots (80,000 units)
- Risking $200 or 2% of account

## Tips for Beginners

1. **Start Small**: Use `--balance 1000` to see smaller position sizes
2. **Paper Trade First**: Test signals without real money
3. **Check Multiple Timeframes**: Look at the detailed analysis for each timeframe
4. **Respect the Risk**: Never override the 2% risk rule
5. **Train Regularly**: Retrain the ML model weekly for best results

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize `config/config.yaml` for your preferences
- Track your trades and calculate win rate
- Experiment with different currency pairs

## Troubleshooting

**Error: "No data received"**
- Check internet connection
- Verify symbol format (must end with =X for yfinance)

**Signal is always HOLD**
- Market may be consolidating
- Try different pairs
- Lower the confidence threshold in config

**Position size too small**
- Increase account balance parameter
- Reduce risk percentage in config

## Support

Questions? Check the main README or examine the code in the `src/` directory.

Happy trading!
