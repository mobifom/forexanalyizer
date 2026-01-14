#!/usr/bin/env python3
"""
Test DataFrame with DatetimeIndex conversion - this is what's causing the error!
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.analysis_db import convert_numpy_types

def test_datetime_index():
    """Test DataFrame with DatetimeIndex (common in financial data)"""
    print("=" * 70)
    print("TESTING DATAFRAME WITH DATETIMEINDEX")
    print("=" * 70)

    # Create a DataFrame with DatetimeIndex - like real market data
    dates = pd.date_range(start='2025-11-01', periods=5, freq='1D')
    df = pd.DataFrame({
        'Open': [np.float64(100.0), np.float64(101.0), np.float64(102.0), np.float64(103.0), np.float64(104.0)],
        'High': [np.float64(105.0), np.float64(106.0), np.float64(107.0), np.float64(108.0), np.float64(109.0)],
        'Close': [np.float64(102.0), np.float64(103.0), np.float64(104.0), np.float64(105.0), np.float64(106.0)],
        'Volume': [np.int64(1000), np.int64(2000), np.int64(3000), np.int64(4000), np.int64(5000)]
    }, index=dates)

    print("\n1. Original DataFrame:")
    print(f"   Index type: {type(df.index)}")
    print(f"   Index[0] type: {type(df.index[0])}")
    print(f"   Index values: {df.index.tolist()[:3]}")
    print(f"\n   DataFrame:\n{df}")

    print("\n2. Converting DataFrame...")
    converted = convert_numpy_types(df)

    print("\n3. Converted structure:")
    print(f"   Type: {type(converted)}")
    print(f"   Keys: {converted.keys()}")
    print(f"   Index type: {type(converted['index'])}")
    print(f"   Index[0] type: {type(converted['index'][0])}")
    print(f"   Index values: {converted['index'][:3]}")

    print("\n4. Testing JSON serialization of DataFrame...")
    try:
        json_str = json.dumps(converted)
        print(f"   ✅ DataFrame with DatetimeIndex JSON serialization successful!")
        print(f"   Length: {len(json_str)} characters")
    except Exception as e:
        print(f"   ❌ JSON serialization failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

    print("\n5. Testing nested structure (like real analysis data)...")
    # Simulate the actual nested structure from your analysis
    analysis_data = {
        'timeframe_analyses': {
            '1d': {
                'signals': {'ma_cross': 'BUY', 'ema_cross': 'BUY'},
                'enhanced_signal': 'BUY',
                'signal_confidence': np.float64(0.8),
                'trend_strength': np.float64(0.75),
                'current_data': {
                    'price': np.float64(4080.42),
                    'rsi': np.float64(55.86),
                    'timestamp': pd.Timestamp.now()  # This is a common culprit!
                },
                'dataframe': df,  # DataFrame with DatetimeIndex
                'enhanced_recommendation': {
                    'timeframe': '1d',
                    'recommendation': 'BUY',
                    'score': 3.5,
                    'current_price': np.float64(4080.42),
                    'ohlc': {
                        'open': np.float64(4050.0),
                        'high': np.float64(4100.0),
                        'low': np.float64(4040.0),
                        'close': np.float64(4080.42),
                        'time': pd.Timestamp.now()  # Another common place for Timestamps!
                    }
                }
            }
        }
    }

    print("   Converting nested analysis data...")
    converted_analysis = convert_numpy_types(analysis_data)

    print("\n6. Testing JSON serialization of nested structure...")
    try:
        json_str = json.dumps(converted_analysis)
        print(f"   ✅ Nested analysis data JSON serialization successful!")
        print(f"   Length: {len(json_str)} characters")

        # Decode to verify it worked
        decoded = json.loads(json_str)
        print("   ✅ JSON deserialization successful!")

        # Check the converted types
        tf_data = decoded['timeframe_analyses']['1d']
        print(f"\n   Verification:")
        print(f"   - signal_confidence type: {type(tf_data['signal_confidence'])} (should be float)")
        print(f"   - current_data.timestamp type: {type(tf_data['current_data']['timestamp'])} (should be str)")
        print(f"   - ohlc.time type: {type(tf_data['enhanced_recommendation']['ohlc']['time'])} (should be str)")
        print(f"   - dataframe.index[0] type: {type(tf_data['dataframe']['index'][0])} (should be str)")

    except Exception as e:
        print(f"   ❌ JSON serialization failed: {e}")
        print(f"   Error type: {type(e).__name__}")

        # Debug: find the problematic field
        for key, value in converted_analysis.items():
            try:
                json.dumps({key: value})
                print(f"     ✅ {key}")
            except Exception as field_error:
                print(f"     ❌ {key}: {field_error}")
        return False

    print("\n" + "=" * 70)
    print("✅ ALL DATETIMEINDEX TESTS PASSED")
    print("=" * 70)

    return True


if __name__ == '__main__':
    success = test_datetime_index()
    sys.exit(0 if success else 1)
