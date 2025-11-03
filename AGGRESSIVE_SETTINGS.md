# Aggressive Trading Settings Guide

## How to Get More Trading Opportunities

To increase trading opportunities (more BUY/SELL signals), you need to lower the quality thresholds. This means accepting signals with lower confidence and less timeframe agreement.

## Risk vs Reward Trade-off

⚠️ **Important**: More signals = Higher risk of false signals

- **Conservative** (default): Fewer but higher quality signals
- **Moderate**: Balanced approach
- **Aggressive**: Many signals but lower quality
- **Very Aggressive**: Maximum signals but highest risk

---

## Configuration Changes

Edit `config/config.yaml` and adjust these settings:

### Current Settings (Moderate)
```yaml
confluence:
  min_timeframes_agree: 2  # 50% of timeframes must agree
  min_confidence: 0.5      # 50% confidence minimum
```

### Option 1: Aggressive Settings (Recommended for More Signals)
```yaml
confluence:
  min_timeframes_agree: 1  # Just 1 timeframe needed (25%)
  min_confidence: 0.4      # 40% confidence minimum
```

**Expected Results**:
- 2-3x more signals than current
- Confidence: 40-60% range
- More false signals but more opportunities

### Option 2: Very Aggressive (Maximum Signals - High Risk!)
```yaml
confluence:
  min_timeframes_agree: 1  # Just 1 timeframe needed
  min_confidence: 0.3      # 30% confidence minimum
```

**Expected Results**:
- 4-5x more signals than current
- Confidence: 30-50% range
- Many false signals - use with caution!

### Option 3: Single Timeframe Trading
```yaml
confluence:
  min_timeframes_agree: 1  # Single timeframe
  min_confidence: 0.35     # 35% confidence

# Also adjust timeframe weights to favor one:
timeframe_weights:
  '1d': 0.7    # Focus on daily (swing trading)
  '4h': 0.2
  '1h': 0.1
  '15m': 0.0   # Ignore 15m
```

**Expected Results**:
- Signals based primarily on daily timeframe
- Reduces conflicts between timeframes
- Better for swing trading

---

## Additional Risk Adjustments

### 1. Adjust Risk Per Trade

In `config/config.yaml`:

```yaml
risk_management:
  risk_per_trade: 0.01  # 1% per trade (conservative)
  # OR
  risk_per_trade: 0.03  # 3% per trade (aggressive)
```

### 2. Adjust Stop Loss Distance

```yaml
risk_management:
  atr_multiplier: 1.5   # Tighter stop loss = more trades fit in account
  # OR
  atr_multiplier: 3.0   # Wider stop loss = fewer trades but more breathing room
```

### 3. Adjust Risk:Reward Ratio

```yaml
risk_management:
  min_risk_reward: 1.0  # Accept 1:1 trades (more opportunities)
  # OR
  min_risk_reward: 2.0  # Require 1:2 trades (fewer but better quality)
```

### 4. Adjust Indicator Thresholds

Make indicators more sensitive:

```yaml
indicators:
  rsi_overbought: 65    # Was 70 - triggers earlier
  rsi_oversold: 35      # Was 30 - triggers earlier
```

---

## Quick Implementation

I'll create three preset configurations for you:

1. **CONSERVATIVE** (default) - High quality, fewer signals
2. **AGGRESSIVE** - More signals, moderate quality
3. **VERY_AGGRESSIVE** - Maximum signals, lower quality

---

## Step-by-Step: Switch to Aggressive Mode

### Method 1: Manual Edit

1. Open `config/config.yaml`
2. Find the `confluence:` section
3. Change values:
   ```yaml
   confluence:
     min_timeframes_agree: 1
     min_confidence: 0.4
   ```
4. Save and close
5. Run analysis: `python main.py analyze --symbol EURUSD=X`

### Method 2: Backup and Use Presets (Recommended)

```bash
# Backup current config
cp config/config.yaml config/config.yaml.backup

# Copy aggressive preset (once I create it)
cp config/config_aggressive.yaml config/config.yaml

# Run analysis
python main.py analyze --symbol EURUSD=X

# To restore conservative settings:
cp config/config.yaml.backup config/config.yaml
```

---

## Testing Your Settings

After changing settings, test with:

```bash
# Test single pair
python main.py analyze --symbol EURUSD=X

# Scan multiple pairs to see signal count
python main.py scan --pairs EURUSD=X GBPUSD=X USDJPY=X GC=F SI=F

# Run diagnostics
python diagnose.py
```

**Look for**:
- More BUY/SELL signals vs HOLD
- Lower confidence scores (40-60% range)
- More timeframe disagreements accepted

---

## Recommended Aggressive Settings

For **balanced aggressive** approach, use:

```yaml
# Signal Confluence Settings
confluence:
  min_timeframes_agree: 1      # Accept single timeframe
  min_confidence: 0.4          # 40% minimum confidence

# Risk Management
risk_management:
  risk_per_trade: 0.02         # Keep at 2%
  atr_multiplier: 2.0          # Keep standard stop loss
  max_drawdown: 0.15           # 15% maximum drawdown
  min_risk_reward: 1.2         # Slightly lower target (1:1.2)

# Technical Indicators (more sensitive)
indicators:
  rsi_overbought: 65           # Trigger earlier
  rsi_oversold: 35             # Trigger earlier
  # ... other settings stay same
```

---

## Warning Signs - Too Aggressive

If you see these, dial back:

❌ **Too many conflicting signals**
- Getting both BUY and SELL on same pair
- Solution: Increase min_timeframes_agree

❌ **Very low confidence scores**
- Consistently below 35%
- Solution: Increase min_confidence

❌ **Rapid losses in backtesting**
- Win rate below 40%
- Solution: Increase quality thresholds

❌ **Signals on every pair**
- Every scan shows 90%+ signals
- Solution: Market might be consolidating, increase thresholds

---

## Comparison Table

| Setting | Conservative | Moderate | Aggressive | Very Aggressive |
|---------|-------------|----------|------------|-----------------|
| min_timeframes_agree | 3 | 2 | 1 | 1 |
| min_confidence | 0.6 | 0.5 | 0.4 | 0.3 |
| Expected Signals | 10-20% | 30-40% | 60-70% | 80-90% |
| Signal Quality | Very High | High | Moderate | Low |
| False Signals | Very Few | Few | Many | Very Many |
| Best For | Conservative traders | Balanced approach | Active traders | Day traders |

---

## Best Practices with Aggressive Settings

1. **Start Small**: Test with paper trading first
2. **Use Stop Losses**: Always use the calculated stop losses
3. **Monitor Performance**: Track win rate and adjust if below 45%
4. **Position Size**: Consider smaller position sizes with aggressive settings
5. **Time of Day**: Trade during high liquidity (London/NY overlap)
6. **News Awareness**: Avoid trading during major news with aggressive settings
7. **Review Daily**: Check which signals worked and which didn't

---

## Quick Reference Commands

```bash
# After changing config, test immediately:
python main.py analyze --symbol EURUSD=X

# Scan all pairs to see signal increase:
python main.py scan

# Check what changed:
python diagnose.py

# View your current settings:
cat config/config.yaml | grep -A 2 "confluence:"
```

---

## Next Steps

1. I'll create the aggressive preset files for you
2. You can easily switch between conservative/aggressive
3. Test with small amounts first
4. Track your results over time
5. Adjust based on your win rate

**Ready to implement?** Let me create the preset configuration files now!
