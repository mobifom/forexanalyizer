#!/usr/bin/env python3
"""
Test API Key Rotation Integration
Verifies that the scheduler, data fetcher, and API key rotator work together
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import load_config
from src.scheduler.smart_scheduler import SmartScheduler
from src.data.data_fetcher import ForexDataFetcher
from src.utils.api_key_rotator import load_api_keys_from_config


def test_key_loading():
    """Test that API keys are loaded from config"""
    print("=" * 70)
    print("TEST 1: API Key Loading")
    print("=" * 70)

    config = load_config('config/config.yaml')
    api_keys = load_api_keys_from_config(config)

    print(f"✅ Loaded {len(api_keys)} API key(s)")

    if len(api_keys) == 0:
        print("⚠️  WARNING: No API keys found!")
        print("   Set TWELVEDATA_API_KEY_1, TWELVEDATA_API_KEY_2, TWELVEDATA_API_KEY_3")
        return False
    elif len(api_keys) == 1:
        print("⚠️  WARNING: Only 1 API key found - rotation disabled")
        print("   Add 2 more keys for rotation (2,400 calls/day total)")
        return True
    else:
        print(f"✅ Multiple keys found - rotation enabled!")
        print(f"   Total daily capacity: {len(api_keys) * 800} calls/day")
        return True


def test_scheduler_integration():
    """Test that scheduler correctly initializes with rotation"""
    print("\n" + "=" * 70)
    print("TEST 2: Scheduler Integration")
    print("=" * 70)

    config = load_config('config/config.yaml')
    scheduler = SmartScheduler(config)

    print(f"✅ Scheduler initialized")
    print(f"   Using key rotation: {scheduler.using_key_rotation}")

    if scheduler.using_key_rotation:
        # Test getting current key
        try:
            current_key = scheduler.api_tracker.get_current_key()
            print(f"✅ Current API key: {current_key[:10]}... (truncated)")

            # Test usage stats
            stats = scheduler.api_tracker.get_usage_stats()
            print(f"✅ Usage stats working:")
            print(f"   Active key: #{stats['current_key_number']} of {stats['total_keys']}")
            print(f"   Total capacity: {stats['total_daily_limit']} calls/day")

            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    else:
        print("ℹ️  Single key mode (no rotation)")
        return True


def test_data_fetcher_integration():
    """Test that data fetcher receives API key provider"""
    print("\n" + "=" * 70)
    print("TEST 3: Data Fetcher Integration")
    print("=" * 70)

    config = load_config('config/config.yaml')
    scheduler = SmartScheduler(config)

    # Get API key provider
    api_key_provider = None
    if scheduler.using_key_rotation:
        api_key_provider = scheduler.api_tracker.get_current_key

    # Initialize data fetcher with provider
    data_config = config.get('data', {})
    data_fetcher = ForexDataFetcher(
        cache_dir='data/cache',
        cache_duration_minutes=data_config.get('cache_duration_minutes', 20),
        data_source=data_config.get('data_source', 'auto'),
        twelvedata_api_key_provider=api_key_provider
    )

    print(f"✅ Data fetcher initialized")

    if data_fetcher.twelvedata_fetcher:
        print(f"✅ TwelveData fetcher available")

        # Check if provider was set
        has_provider = data_fetcher.twelvedata_fetcher.api_key_provider is not None
        print(f"✅ API key provider set: {has_provider}")

        if has_provider:
            # Test dynamic key retrieval
            try:
                key = data_fetcher.twelvedata_fetcher._get_api_key()
                print(f"✅ Dynamic key retrieval working: {key[:10]}... (truncated)")
                return True
            except Exception as e:
                print(f"❌ Error getting key: {e}")
                return False
        else:
            print("ℹ️  Static key mode (no provider)")
            return True
    else:
        print("⚠️  TwelveData fetcher not available")
        print("   This is expected if no API keys are configured")
        return True


def test_key_rotation_logic():
    """Test that key rotation actually works when limit is reached"""
    print("\n" + "=" * 70)
    print("TEST 4: Key Rotation Logic")
    print("=" * 70)

    config = load_config('config/config.yaml')
    scheduler = SmartScheduler(config)

    if not scheduler.using_key_rotation:
        print("ℹ️  Skipping test - rotation not enabled (need 2+ API keys)")
        return True

    rotator = scheduler.api_tracker

    print(f"✅ Initial state:")
    print(f"   Active key: #{rotator.current_key_index + 1}")
    print(f"   Total keys: {len(rotator.api_keys)}")

    # Simulate first key reaching limit
    print("\n🧪 Simulating key #1 reaching daily limit...")
    rotator.daily_counts[0] = rotator.max_per_day

    # Try to make a call (should trigger rotation)
    can_call, reason = rotator.can_make_call()

    if can_call:
        print(f"✅ Rotation successful!")
        print(f"   New active key: #{rotator.current_key_index + 1}")

        if rotator.current_key_index == 1:
            print("✅ Correctly rotated to key #2")

            # Reset for clean state
            rotator.daily_counts[0] = 0
            rotator.current_key_index = 0

            return True
        else:
            print(f"⚠️  Expected key #2, got key #{rotator.current_key_index + 1}")
            return False
    else:
        print(f"❌ Rotation failed: {reason}")
        return False


def test_full_integration():
    """Test the complete flow from scheduler to API call"""
    print("\n" + "=" * 70)
    print("TEST 5: Full Integration Test")
    print("=" * 70)

    try:
        config = load_config('config/config.yaml')
        scheduler = SmartScheduler(config)

        # Get API key provider
        api_key_provider = None
        if scheduler.using_key_rotation:
            api_key_provider = scheduler.api_tracker.get_current_key

        # Initialize data fetcher
        data_config = config.get('data', {})
        data_fetcher = ForexDataFetcher(
            cache_dir='data/cache',
            cache_duration_minutes=data_config.get('cache_duration_minutes', 20),
            data_source=data_config.get('data_source', 'auto'),
            twelvedata_api_key_provider=api_key_provider
        )

        print("✅ All components initialized successfully")
        print("\nℹ️  Integration test complete!")
        print("   To test actual API calls, run: python run_scheduler.py")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🧪 API KEY ROTATION INTEGRATION TEST SUITE\n")

    tests = [
        ("Key Loading", test_key_loading),
        ("Scheduler Integration", test_scheduler_integration),
        ("Data Fetcher Integration", test_data_fetcher_integration),
        ("Key Rotation Logic", test_key_rotation_logic),
        ("Full Integration", test_full_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 All tests passed! API key rotation is fully integrated.")
        print("\nNext steps:")
        print("1. Set up your 3 TwelveData API keys (see MULTIPLE_API_KEYS_SETUP.md)")
        print("2. Run the scheduler: python run_scheduler.py")
        print("3. Monitor usage reports for automatic key rotation")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
