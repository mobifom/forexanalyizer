# Gold & Silver Quick Reference

## Symbols
- **Gold**: `GC=F`
- **Silver**: `SI=F`

## Quick Commands

### Analyze Gold
```bash
python main.py analyze --symbol GC=F
```

### Analyze Silver
```bash
python main.py analyze --symbol SI=F
```

### Scan Both
```bash
python main.py scan --pairs GC=F SI=F
```

### Train on Gold
```bash
python main.py train --symbol GC=F
```

## Test Support
```bash
python test_gold_silver.py
```

## Lot Sizes
- **Standard Lot**: 100 oz
- **Mini Lot**: 10 oz
- **Micro Lot**: 1 oz

## Key Differences from Forex

| Feature | Forex Pairs | Gold/Silver |
|---------|-------------|-------------|
| Quote | Currency ratio | USD per oz |
| Volatility | Lower | Higher |
| Gaps | Rare | More common |
| Hours | 24/5 | 23/5 |
| Lot Size | 100k units | 100 oz |

## Position Size Example

For $10,000 account with 2% risk:
```
Gold at $2,050/oz
ATR: $15
Stop: 2x ATR = $30
Risk: $200 (2%)
Position: $200 / $30 = 6.67 oz (~0.07 lots)
```

## Common Issues

**Symbol not found?**
- Use `GC=F` (not `GOLD`)
- Use `SI=F` (not `SILVER`)
- Check internet connection
- Run: `python test_gold_silver.py`

**High volatility?**
- Increase ATR multiplier (2.5-3.0)
- Reduce risk per trade (1-1.5%)
- Use daily timeframe primarily

## See Also
- [GOLD_SILVER_GUIDE.md](GOLD_SILVER_GUIDE.md) - Complete guide
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
