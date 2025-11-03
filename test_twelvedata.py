"""
Test Twelve Data API connection and data retrieval
"""

import sys
sys.path.append('/Users/mohamedhamdi/Work/Forex/ForexAnalyzer')

from src.data.twelvedata_fetcher import TwelveDataFetcher

# Your API key
API_KEY = '24b8973fe3ce42acad781d9178c6f4a7'

print("=" * 70)
print("TESTING TWELVE DATA API")
print("=" * 70)

# Initialize fetcher
fetcher = TwelveDataFetcher(api_key=API_KEY)

# Test 1: Check API status
print("\n1. Checking API status...")
status = fetcher.check_api_status()
if status:
    print("   ✅ API is working!")
else:
    print("   ❌ API is not working")

# Test 2: Get EUR/USD quote
print("\n2. Testing EUR/USD quote...")
quote = fetcher.get_quote('EURUSD=X')
if quote and quote.get('current', 0) > 0:
    print(f"   ✅ EUR/USD: ${quote['current']:.5f}")
    print(f"      Change: {quote.get('percent_change', 0):.2f}%")
else:
    print("   ❌ Failed to get EUR/USD quote")

# Test 3: Get Gold (XAU/USD) data
print("\n3. Testing Gold (XAU/USD) candles...")
gold_df = fetcher.fetch_candles('XAU_USD', '1d', limit=5)
if not gold_df.empty:
    print(f"   ✅ Retrieved {len(gold_df)} candles for Gold")
    print(f"      Latest price: ${gold_df['Close'].iloc[-1]:.2f}")
    print(f"      Date: {gold_df.index[-1]}")
else:
    print("   ❌ Failed to get Gold data")

# Test 4: Get Silver (XAG/USD) data
print("\n4. Testing Silver (XAG/USD) candles...")
silver_df = fetcher.fetch_candles('XAG_USD', '1d', limit=5)
if not silver_df.empty:
    print(f"   ✅ Retrieved {len(silver_df)} candles for Silver")
    print(f"      Latest price: ${silver_df['Close'].iloc[-1]:.2f}")
    print(f"      Date: {silver_df.index[-1]}")
else:
    print("   ❌ Failed to get Silver data")

# Test 5: Get GBP/USD data
print("\n5. Testing GBP/USD candles...")
gbp_df = fetcher.fetch_candles('GBPUSD=X', '1h', limit=5)
if not gbp_df.empty:
    print(f"   ✅ Retrieved {len(gbp_df)} candles for GBP/USD")
    print(f"      Latest price: ${gbp_df['Close'].iloc[-1]:.5f}")
    print(f"      Date: {gbp_df.index[-1]}")
else:
    print("   ❌ Failed to get GBP/USD data")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
