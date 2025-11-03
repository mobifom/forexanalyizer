# 🥇 Precious Metals Trading Guide

## What Changed (Latest Update)

### Evolution:
1. **Original**: GLD ETF ($368/share - confusing)
2. **V1**: GC=F futures ($3982/oz - clearer)
3. **V2 (Current)**: XAU_USD/XAG_USD spot prices (Oanda) - **Most accurate!**

### Current Solution:
- **Primary**: Oanda Spot Prices (XAU_USD, XAG_USD)
- **Fallback**: Yahoo Finance Futures (GC=F, SI=F)
- **Direct per-ounce pricing**: Shows actual real-time spot prices
- **Clear display**: $3996/oz for gold, $48/oz for silver

---

## 🥇 Gold - XAU_USD Symbol

### What is XAU_USD?
**XAU_USD** = Gold Spot Price (Oanda)
- Real-time gold spot market price
- Shows price per troy ounce
- Direct from forex/commodities broker (Oanda)
- Most accurate representation of current gold value
- Fallback to GC=F (Gold Futures) when Oanda unavailable

### Price Interpretation

**Simple**: XAU_USD shows the **actual gold spot price per ounce** - no conversion needed!

#### Example:
```
XAU_USD Price:     $3,996.50/oz
That's it!         Direct real-time spot price
Data Source:       Oanda (or yfinance if Oanda unavailable)
```

### In the GUI:
When you select Gold Spot (XAU_USD), the app will show:
- **Display**: Gold Spot: $3,996.50/oz
- **Data Source**: Oanda (primary) or yfinance (fallback)
- **No conversion needed** - this is the real spot price!

---

## 🥈 Silver - XAG_USD Symbol

### What is XAG_USD?
**XAG_USD** = Silver Spot Price (Oanda)
- Real-time silver spot market price
- Shows price per troy ounce
- Direct from forex/commodities broker (Oanda)
- Most accurate representation of current silver value
- Fallback to SI=F (Silver Futures) when Oanda unavailable

### Price Interpretation

**Simple**: XAG_USD shows the **actual silver spot price per ounce** - no conversion needed!

#### Example:
```
XAG_USD Price:     $48.16/oz
That's it!         Direct real-time spot price
Data Source:       Oanda (or yfinance if Oanda unavailable)
```

### In the GUI:
When you select Silver Spot (XAG_USD), the app will show:
- **Display**: Silver Spot: $48.16/oz
- **Data Source**: Oanda (primary) or yfinance (fallback)
- **No conversion needed** - this is the real spot price!

---

## 📊 Why Oanda Spot (XAU_USD, XAG_USD)?

### Advantages:
✅ **Real-time spot pricing** - Most accurate current price
✅ **No conversion needed** - $3996 means $3996/oz exactly
✅ **True market pricing** - What traders actually pay/receive
✅ **Forex broker standard** - Industry-standard symbol format
✅ **Automatic fallback** - Uses yfinance futures if Oanda unavailable

### Data Source Strategy:
1. **Primary (Oanda)**: XAU_USD, XAG_USD - Real-time spot prices
2. **Fallback (yfinance)**: GC=F, SI=F - Futures as proxy for spot
3. **Seamless switching** - App automatically uses best available source

### Alternative Sources:
- **Futures (GC=F, SI=F)**: Good approximation of spot, 23-hour trading
- **ETFs (GLD, SLV)**: Share prices need conversion, confusing
- **Why we chose Oanda**: Most accurate spot prices, matches ForexApp V2

---

## 💡 Understanding the Prices

### Current Data (as shown in tests):

#### Gold (GLD):
- **ETF Price**: $368.12
- **Represents**: ~$3,681/oz spot gold
- **Date**: October 31, 2024

#### Silver (SLV):
- **ETF Price**: $44.01
- **Represents**: ~$44/oz spot silver
- **Date**: October 31, 2024

### Historical Context:
- **Typical Gold Range**: $1,800 - $2,800/oz (recent years)
- **Typical Silver Range**: $20 - $50/oz (recent years)

**Note**: If the displayed prices seem unusual, check:
1. Your system date/time settings
2. Market conditions (metals can be volatile)
3. The data source date (shown in the analysis)

---

## 🎯 How to Trade with ETFs

### For Gold (GLD):

#### Entry Points:
The analyzer shows entry points based on the **ETF price**:
```
Entry 1 (NOW):      $368.12
Entry 2 (Pullback): $366.50
Entry 3 (BEST):     $365.00
```

These are **ETF share prices**, not per-ounce gold prices.

#### Stop Loss & Take Profits:
All levels are calculated for the **ETF price**:
```
Stop Loss (2 ATR):  $363.00
TP1:                $370.50
TP2:                $373.00
TP3:                $375.50
TP4:                $380.00
```

#### What This Means:
- You trade the ETF shares, not physical gold
- Entry at $368 means buying GLD shares at $368 each
- TP at $370 means selling when GLD reaches $370

### For Silver (SLV):

#### Similar Approach:
All trading levels are for SLV shares:
```
Entry 1 (NOW):      $44.01
Stop Loss (2 ATR):  $42.50
TP1:                $45.50
TP2:                $47.00
```

Since SLV ≈ spot silver, these also represent approximate per-ounce prices.

---

## 📈 Technical Analysis with ETFs

### Advantages:
1. **Reliable Charts**: Clean, continuous price data
2. **All Indicators Work**: RSI, MACD, Bollinger Bands, etc.
3. **No Gaps**: Unlike futures with contract rollovers
4. **Volume Data**: Accurate volume for confirmation

### Example Analysis:

```
GLD Analysis (Daily Timeframe)

Current Price: $368.12
RSI: 45.23 (Neutral)
MACD: Bullish crossover
MA 20: $365.50
MA 50: $362.00
Bollinger Bands: $360 - $376

Recommendation: BUY
Score: +2

Entry 1: $368.12 (NOW)
Entry 2: $366.50 (Pullback to MA 20)
Entry 3: $365.00 (Support zone)

Stop Loss: $363.00 (2 ATR)
TP1: $370.50 (1:1 R:R)
TP2: $373.00 (1:2 R:R)
TP3: $375.50 (1:3 R:R)
TP4: $380.00 (1:5 R:R)
```

All these levels are **ETF share prices**, which you can trade directly.

---

## 💰 Position Sizing

### Example Trade Setup:

#### Account: $10,000
#### Risk per Trade: 2% = $200

#### Gold Trade (GLD):
```
Entry:          $368.00
Stop Loss:      $363.00
Risk per Share: $5.00

Position Size:  $200 ÷ $5.00 = 40 shares
Total Cost:     40 shares × $368 = $14,720

❌ Too expensive for $10K account!
```

#### Solution:
Use fractional shares (if your broker allows) or adjust position size.

#### Silver Trade (SLV):
```
Entry:          $44.00
Stop Loss:      $42.50
Risk per Share: $1.50

Position Size:  $200 ÷ $1.50 = 133 shares
Total Cost:     133 shares × $44 = $5,852

✅ Fits within $10K account
```

Silver is more accessible for smaller accounts.

---

## 🔍 Comparison: Data Sources

| Feature | Oanda Spot (XAU_USD, XAG_USD) | Futures (GC=F, SI=F) | ETFs (GLD, SLV) |
|---------|-------------------------------|---------------------|-----------------|
| **Price Display** | ✅ Direct $/oz (spot) | ✅ Direct $/oz (futures) | ⚠️ Share price |
| **Accuracy** | ✅ Exact spot price | ✅ Very close to spot | ⚠️ Tracking error |
| **Conversion Needed** | ✅ No | ✅ No | ❌ Yes (GLD×10) |
| **Data Reliability** | ✅ Excellent (real-time) | ✅ Good | ✅ Excellent |
| **API Required** | ⚠️ Yes (Oanda key) | ✅ No (free) | ✅ No (free) |
| **Contract Rollovers** | ✅ No | ⚠️ Yes (infrequent) | ✅ No |
| **Trading Hours** | 24 hours/day | 23 hours/day | Regular market hours |
| **Clarity for Users** | ✅ Perfect | ✅ Intuitive | ⚠️ Requires math |
| **Matches ForexApp V2** | ✅ Yes | ⚠️ Close | ❌ No |

**Our Choice**: Oanda Spot (XAU_USD, XAG_USD) for maximum accuracy, with automatic fallback to futures.

---

## 🛠️ How to Use in the App

### Step 0: Configure Oanda (Optional but Recommended)
1. Sign up for Oanda account (free practice account available)
2. Get API key from Oanda dashboard
3. Edit `config/config.yaml`:
   - Set `oanda: enabled: true`
   - Add your `api_key`
   - Set `data_source: 'auto'` (tries Oanda first, falls back to yfinance)
4. Without Oanda, app automatically uses yfinance futures (still works great!)

### Step 1: Select Metal
1. Go to sidebar
2. Choose "Precious Metals"
3. Select either:
   - 🥇 Gold Spot (XAU_USD) - Oanda spot or yfinance futures
   - 🥈 Silver Spot (XAG_USD) - Oanda spot or yfinance futures

### Step 2: Refresh Data (Optional)
- Click "🔄 Refresh Latest Data"
- Ensures you have most recent prices

### Step 3: Analyze
- Click "🔍 Analyze"
- Wait for analysis to complete

### Step 4: Review V2 Recommendations
Go to "🎯 V2 Recommendations" tab to see:
- Multi-timeframe summary
- Entry points for ETF shares
- Stop loss levels for ETF shares
- Take profit targets for ETF shares
- Interactive chart with all levels marked

### Step 5: Interpret Prices
- For **XAU_USD**: Price shown IS the spot gold price per ounce
- For **XAG_USD**: Price shown IS the spot silver price per ounce
- **Data source** will be logged (Oanda or yfinance)
- All trading levels are direct per-ounce prices - no conversion needed!

### Step 6: Execute
- Trade gold/silver spot CFDs on your forex broker
- Or trade futures contracts (GC, SI) using the same levels
- Or trade ETFs (GLD, SLV) - multiply gold levels by 0.1
- Or trade spot metals on your brokerage platform
- Levels work for any gold/silver trading instrument

---

## ❓ FAQ

### Q: Why use Oanda spot (XAU_USD) instead of futures (GC=F)?
**A**: Oanda provides real-time spot prices which are more accurate than futures. It matches ForexApp V2 implementation. If Oanda is unavailable, the app automatically falls back to futures.

### Q: Do I need an Oanda account?
**A**: No! The app works perfectly with yfinance (free). Oanda is optional for:
- More accurate real-time spot prices
- Better data for intraday trading
- Professional-grade forex data
Without Oanda, you get good-quality futures data from yfinance.

### Q: Can I still use ETFs like GLD/SLV?
**A**: Yes! Use "Custom" symbol option and enter GLD or SLV. Just remember:
- GLD price × 10 ≈ gold spot price
- SLV price ≈ silver spot price

### Q: Is $3,996/oz realistic for gold?
**A**: Yes! Gold has been trading in the $3,500-$4,200 range recently. To verify current prices:
- Check [Kitco.com](https://www.kitco.com/charts/livegold.html)
- Verify system date/time is correct
- Click "Refresh Latest Data" button
- Check logs to see if using Oanda or yfinance

### Q: Why does silver show $48/oz?
**A**: That's the current spot silver price. Silver typically trades $20-$50/oz range. Check [Kitco Silver](https://www.kitco.com/charts/livesilver.html) for real-time verification.

### Q: Which data source is the app using?
**A**: Check the terminal logs when you analyze:
- "Fetching XAU_USD from Oanda" = Using Oanda spot
- "Fetching XAU_USD (as GC=F) from yfinance" = Using futures fallback
- Both provide good data quality!

### Q: Can I trade other precious metals?
**A**: Yes! Use "Custom" option and enter:
- Platinum: PL=F
- Palladium: PA=F
- Copper: HG=F

### Q: How often is data updated?
**A**:
- Auto-cached for 60 minutes
- Click "Refresh Latest Data" for immediate update
- Market data delayed 15-20 minutes (Yahoo Finance free tier)

---

## 📚 Additional Resources

### Learning:
- [SPDR Gold Shares (GLD) - Official Site](https://www.spdrgoldshares.com/)
- [iShares Silver Trust (SLV) - Official Site](https://www.ishares.com/us/products/239855/)

### Trading:
- Check your broker for:
  - GLD availability
  - SLV availability
  - Fractional shares
  - Margin requirements

### Market Data:
- [Gold Spot Price - Kitco](https://www.kitco.com/charts/livegold.html)
- [Silver Spot Price - Kitco](https://www.kitco.com/charts/livesilver.html)

---

## ✅ Summary

### Key Takeaways:

1. **2 Precious Metals**: XAU_USD (Gold Spot) and XAG_USD (Silver Spot)
2. **Dual data sources**: Oanda (primary) + yfinance (automatic fallback)
3. **Price interpretation**:
   - XAU_USD: Real-time gold spot price (e.g., $3,996/oz)
   - XAG_USD: Real-time silver spot price (e.g., $48.16/oz)
   - **No conversion needed!**
4. **All analysis levels**: Calculated as per-ounce prices
5. **Trade directly**: Use levels for spot CFDs, futures, ETFs, or physical
6. **Matches ForexApp V2**: Same symbols and data approach

### In the GUI:
- Clear price display: "Gold Spot: $3,996.50/oz"
- Data source indicator: (Oanda) or (yfinance)
- All trading levels in per-ounce terms
- Interactive charts with entry/stop/TP marked
- Multi-timeframe analysis (15m, 1h, 4h, 1d)

### Getting Started:
1. **Without Oanda**: Works immediately with yfinance (free, good quality)
2. **With Oanda**: Edit config.yaml, add API key, get real-time spot prices
3. **Either way**: You get accurate gold/silver analysis!

---

**Happy Trading! 🥇🥈📈**

*Remember: This is analysis software. Precious metals can be volatile. Always do your own research and never risk more than you can afford to lose.*
