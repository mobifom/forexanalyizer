#!/usr/bin/env python3
"""
Check Twelve Data API Status and Usage
"""

from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

api_key = os.getenv('TWELVEDATA_API_KEY', '')

if not api_key:
    print("❌ TWELVEDATA_API_KEY not found in environment")
    print("   Make sure .env file exists with your API key")
    exit(1)

print("=" * 60)
print("TWELVE DATA API STATUS CHECK")
print("=" * 60)
print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")

# Try to get a quote
url = "https://api.twelvedata.com/quote"
params = {
    'symbol': 'EUR/USD',
    'apikey': api_key
}

print("\nTesting API with EUR/USD quote...")
response = requests.get(url, params=params, timeout=10)

print(f"Response Status: {response.status_code}")
print(f"Response Data:")
print("-" * 60)

data = response.json()

# Pretty print the response
import json
print(json.dumps(data, indent=2))

print("-" * 60)

# Check for errors
if 'code' in data:
    error_code = data.get('code')
    error_msg = data.get('message', '')

    print(f"\n❌ API ERROR")
    print(f"   Code: {error_code}")
    print(f"   Message: {error_msg}")

    if '429' in str(error_code) or 'credits' in error_msg.lower():
        print(f"\n⚠️  RATE LIMIT EXCEEDED")
        print(f"   You've used up your daily quota (800 calls/day)")
        print(f"\n   Solutions:")
        print(f"   1. Wait until tomorrow (resets every 24 hours)")
        print(f"   2. Get a new free API key from https://twelvedata.com/pricing")
        print(f"   3. Upgrade to paid plan ($7.99/month for 30K calls/day)")
        print(f"   4. Use Yahoo Finance for now (delayed data)")

elif 'name' in data and 'close' in data:
    print(f"\n✅ API IS WORKING!")
    print(f"   Symbol: {data.get('name', 'N/A')}")
    print(f"   Price: ${data.get('close', 'N/A')}")
    print(f"   Exchange: {data.get('exchange', 'N/A')}")
    print(f"\n   Your Twelve Data API is functioning correctly!")

else:
    print(f"\n⚠️  UNEXPECTED RESPONSE")
    print(f"   Check the response data above")

print("\n" + "=" * 60)
