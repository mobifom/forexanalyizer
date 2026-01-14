#!/usr/bin/env python3
"""
Test Timestamp and datetime conversion specifically
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json
from datetime import datetime, date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.analysis_db import convert_numpy_types

def test_timestamp_conversion():
    """Test Timestamp and datetime conversion"""
    print("=" * 70)
    print("TESTING TIMESTAMP & DATETIME CONVERSION")
    print("=" * 70)

    # Test data with various timestamp types
    test_data = {
        'pd_timestamp': pd.Timestamp('2025-11-16 10:30:00'),
        'pd_timestamp_now': pd.Timestamp.now(),
        'pd_timestamp_tz': pd.Timestamp('2025-11-16 10:30:00', tz='UTC'),
        'datetime_obj': datetime.now(),
        'date_obj': date.today(),
        'nested_timestamps': {
            'analysis_time': pd.Timestamp.now(),
            'data_time': datetime.now(),
            'nested_dict': {
                'deep_timestamp': pd.Timestamp('2025-11-16'),
                'deep_int64': np.int64(42)
            }
        },
        'list_with_timestamps': [
            pd.Timestamp('2025-11-16 10:00:00'),
            pd.Timestamp('2025-11-16 11:00:00'),
            datetime.now()
        ],
        'timeframe_analyses': {
            '1d': {
                'signal_confidence': np.float64(0.85),
                'agreement_count': np.int64(3),
                'timestamp': pd.Timestamp.now(),
                'trend_strength': np.float64(0.75)
            },
            '4h': {
                'signal_confidence': np.float64(0.72),
                'agreement_count': np.int64(2),
                'timestamp': pd.Timestamp.now(),
                'price_levels': [np.float64(1.0950), np.float64(1.0960)]
            }
        }
    }

    print("\n1. Original data types:")
    for key, value in test_data.items():
        if isinstance(value, dict):
            print(f"   {key}: {type(value)} (nested dict)")
            for nested_key, nested_value in value.items():
                print(f"     {nested_key}: {type(nested_value).__name__}")
        elif isinstance(value, list):
            print(f"   {key}: {type(value)} (list with {len(value)} items)")
            for i, item in enumerate(value):
                print(f"     [{i}]: {type(item).__name__}")
        else:
            print(f"   {key}: {type(value).__name__}")

    print("\n2. Converting...")
    converted = convert_numpy_types(test_data)

    print("\n3. Converted data types:")
    for key, value in converted.items():
        if isinstance(value, dict):
            print(f"   {key}: {type(value)} (nested dict)")
            for nested_key, nested_value in value.items():
                print(f"     {nested_key}: {type(nested_value).__name__} = {nested_value}")
        elif isinstance(value, list):
            print(f"   {key}: {type(value)} (list)")
            for i, item in enumerate(value):
                print(f"     [{i}]: {type(item).__name__} = {item}")
        else:
            print(f"   {key}: {type(value).__name__} = {value}")

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
        print(f"   Error type: {type(e).__name__}")

        # Debug: Try each field individually
        print("\n   Debugging individual fields:")
        for key, value in converted.items():
            try:
                json.dumps({key: value})
                print(f"     ✅ {key}")
            except Exception as field_error:
                print(f"     ❌ {key}: {field_error}")
                print(f"        Type: {type(value).__name__}")

        return False

    print("\n5. Testing timeframe_analyses specifically...")
    # This is the field that was causing errors
    tf_analyses = converted.get('timeframe_analyses', {})
    try:
        tf_json = json.dumps(tf_analyses)
        print("   ✅ timeframe_analyses JSON serialization successful!")
        print(f"   Length: {len(tf_json)} characters")

        # Show structure
        print("\n   Structure:")
        for tf, data in tf_analyses.items():
            print(f"     {tf}:")
            for field, value in data.items():
                print(f"       {field}: {type(value).__name__} = {value}")
    except Exception as e:
        print(f"   ❌ timeframe_analyses JSON serialization failed: {e}")
        return False

    print("\n" + "=" * 70)
    print("✅ ALL TIMESTAMP CONVERSION TESTS PASSED")
    print("=" * 70)

    return True


if __name__ == '__main__':
    success = test_timestamp_conversion()
    sys.exit(0 if success else 1)
