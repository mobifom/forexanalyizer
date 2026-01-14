#!/usr/bin/env python3
"""
Test JSON conversion for numpy types
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.analysis_db import convert_numpy_types

def test_conversion():
    """Test the convert_numpy_types function"""
    print("=" * 70)
    print("TESTING NUMPY TYPE CONVERSION")
    print("=" * 70)

    # Test data with various numpy types
    test_data = {
        'int64_value': np.int64(42),
        'int32_value': np.int32(100),
        'float64_value': np.float64(3.14),
        'float32_value': np.float32(2.71),
        'bool_value': np.bool_(True),
        'array_value': np.array([1, 2, 3]),
        'nested_dict': {
            'inner_int64': np.int64(999),
            'inner_float64': np.float64(1.23),
            'inner_list': [np.int64(1), np.int64(2), np.int64(3)]
        },
        'list_with_numpy': [np.int64(10), np.float64(20.5), np.bool_(False)],
        'nan_value': np.float64(np.nan),
        'inf_value': np.float64(np.inf),
        'string_value': 'test',
        'int_value': 42,
        'float_value': 3.14,
        'none_value': None
    }

    print("\n1. Original data types:")
    for key, value in test_data.items():
        print(f"   {key}: {type(value)}")

    print("\n2. Converting...")
    converted = convert_numpy_types(test_data)

    print("\n3. Converted data types:")
    for key, value in converted.items():
        print(f"   {key}: {type(value)} = {value}")

    print("\n4. Testing JSON serialization...")
    try:
        json_str = json.dumps(converted)
        print("   ✅ JSON serialization successful!")
        print(f"   Length: {len(json_str)} characters")

        # Test deserialization
        decoded = json.loads(json_str)
        print("   ✅ JSON deserialization successful!")

    except Exception as e:
        print(f"   ❌ JSON serialization failed: {e}")
        return False

    print("\n5. Testing with DataFrame...")
    # Test DataFrame conversion
    df = pd.DataFrame({
        'price': [np.float64(1.0950), np.float64(1.0960), np.float64(1.0970)],
        'volume': [np.int64(1000), np.int64(2000), np.int64(3000)],
        'signal': ['BUY', 'HOLD', 'SELL']
    })

    print(f"   Original DataFrame type: {type(df)}")
    converted_df = convert_numpy_types(df)
    print(f"   Converted type: {type(converted_df)}")

    try:
        json_df = json.dumps(converted_df)
        print("   ✅ DataFrame JSON serialization successful!")
        print(f"   Length: {len(json_df)} characters")
    except Exception as e:
        print(f"   ❌ DataFrame JSON serialization failed: {e}")
        return False

    print("\n6. Testing with real-world example...")
    # Simulate actual analysis data structure with DataFrame
    real_world = {
        'symbol': 'EURUSD=X',
        'current_price': np.float64(1.0950),
        'timestamp': pd.Timestamp.now().isoformat(),
        'multi_timeframe_consensus': {
            'consensus': 'BUY',
            'confidence': np.float64(0.75),
            'agreement_count': np.int64(3),
            'total_timeframes': np.int64(4),
            'buy_timeframes': [
                {'timeframe': '1h', 'confidence': np.float64(0.72)},
                {'timeframe': '4h', 'confidence': np.float64(0.78)},
                {'timeframe': '1d', 'confidence': np.float64(0.80)}
            ]
        },
        'timeframe_analyses': {
            '1d': {
                'trend_strength': np.float64(0.85),
                'signal_confidence': np.float64(0.80),
                'support_levels': [np.float64(1.0900), np.float64(1.0850)],
                'resistance_levels': [np.float64(1.1000), np.float64(1.1050)],
                'data': df  # Include DataFrame in the structure
            }
        }
    }

    print("   Converting real-world example...")
    converted_real = convert_numpy_types(real_world)

    try:
        json_real = json.dumps(converted_real)
        print("   ✅ Real-world JSON serialization successful!")
        print(f"   Length: {len(json_real)} characters")

    except Exception as e:
        print(f"   ❌ Real-world JSON serialization failed: {e}")
        print(f"   Error type: {type(e)}")
        return False

    print("\n" + "=" * 70)
    print("✅ ALL CONVERSION TESTS PASSED")
    print("=" * 70)

    return True


if __name__ == '__main__':
    success = test_conversion()
    sys.exit(0 if success else 1)
