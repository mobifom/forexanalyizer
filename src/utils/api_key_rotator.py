"""
API Key Rotator for TwelveData
Manages multiple API keys with automatic rotation when limits are reached
"""

import logging
import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class APIKeyRotator:
    """Manages multiple API keys with automatic rotation"""

    def __init__(self, api_keys: List[str], max_per_day: int = 800, max_per_minute: int = 8):
        """
        Initialize API key rotator

        Args:
            api_keys: List of API keys to rotate between
            max_per_day: Maximum calls per day per key (default: 800)
            max_per_minute: Maximum calls per minute across all keys (default: 8)
        """
        # Filter out empty keys
        self.api_keys = [key for key in api_keys if key and key.strip()]

        if not self.api_keys:
            raise ValueError("No valid API keys provided")

        self.max_per_day = max_per_day
        self.max_per_minute = max_per_minute

        # Track usage per key
        self.daily_counts = defaultdict(int)
        self.daily_reset_times = {}
        self.calls_log = []  # For per-minute tracking (shared across all keys)

        # Current active key index
        self.current_key_index = 0

        # Lock for thread safety
        self.lock = threading.Lock()

        # Initialize reset times
        now = datetime.now()
        for i, key in enumerate(self.api_keys):
            self.daily_reset_times[i] = now.replace(hour=0, minute=0, second=0)

        logger.info(f"✅ API Key Rotator initialized with {len(self.api_keys)} keys")
        logger.info(f"   Total daily capacity: {len(self.api_keys) * max_per_day} calls")

    def get_current_key(self) -> str:
        """Get the currently active API key"""
        with self.lock:
            return self.api_keys[self.current_key_index]

    def get_current_key_index(self) -> int:
        """Get the index of the currently active key"""
        with self.lock:
            return self.current_key_index

    def can_make_call(self) -> tuple[bool, str]:
        """
        Check if we can make an API call

        Returns:
            Tuple of (can_call, reason)
        """
        with self.lock:
            now = datetime.now()

            # Reset daily counters if new day
            self._reset_daily_counters_if_needed(now)

            # Check if current key has reached daily limit
            current_count = self.daily_counts[self.current_key_index]
            if current_count >= self.max_per_day:
                # Try to rotate to next available key
                if not self._try_rotate_key(now):
                    return False, f"All API keys have reached daily limit ({self.max_per_day})"

            # Check per-minute limit (shared across all keys)
            one_minute_ago = now - timedelta(minutes=1)
            recent_calls = [t for t in self.calls_log if t > one_minute_ago]

            if len(recent_calls) >= self.max_per_minute:
                return False, f"Per-minute limit reached ({len(recent_calls)}/{self.max_per_minute})"

            return True, "OK"

    def record_call(self, key_index: Optional[int] = None):
        """
        Record that an API call was made

        Args:
            key_index: Index of the key used (default: current key)
        """
        with self.lock:
            now = datetime.now()

            if key_index is None:
                key_index = self.current_key_index

            # Increment daily counter for this key
            self.daily_counts[key_index] += 1

            # Add to calls log for per-minute tracking
            self.calls_log.append(now)

            # Clean up old entries (keep last hour)
            one_hour_ago = now - timedelta(hours=1)
            self.calls_log = [t for t in self.calls_log if t > one_hour_ago]

            logger.debug(
                f"API call recorded for key #{key_index + 1}. "
                f"Daily: {self.daily_counts[key_index]}/{self.max_per_day}"
            )

    def _reset_daily_counters_if_needed(self, now: datetime):
        """Reset daily counters if new day"""
        for key_index in range(len(self.api_keys)):
            reset_time = self.daily_reset_times.get(key_index)
            if reset_time and now >= reset_time + timedelta(days=1):
                old_count = self.daily_counts[key_index]
                self.daily_counts[key_index] = 0
                self.daily_reset_times[key_index] = now.replace(hour=0, minute=0, second=0)
                logger.info(f"🔄 Daily counter reset for API key #{key_index + 1} (was: {old_count})")

    def _try_rotate_key(self, now: datetime) -> bool:
        """
        Try to rotate to next available key

        Args:
            now: Current datetime

        Returns:
            True if rotation successful, False if all keys exhausted
        """
        # Try each key in sequence
        for i in range(len(self.api_keys)):
            next_index = (self.current_key_index + 1 + i) % len(self.api_keys)

            # Check if this key has capacity
            if self.daily_counts[next_index] < self.max_per_day:
                old_index = self.current_key_index
                self.current_key_index = next_index

                logger.warning(
                    f"🔄 Rotating from API key #{old_index + 1} "
                    f"({self.daily_counts[old_index]}/{self.max_per_day} calls) "
                    f"to key #{next_index + 1} "
                    f"({self.daily_counts[next_index]}/{self.max_per_day} calls)"
                )
                return True

        # All keys exhausted
        return False

    def force_rotate_to_key(self, key_index: int) -> bool:
        """
        Force rotation to specific key

        Args:
            key_index: Index of key to switch to

        Returns:
            True if successful
        """
        with self.lock:
            if 0 <= key_index < len(self.api_keys):
                old_index = self.current_key_index
                self.current_key_index = key_index
                logger.info(f"🔄 Forced rotation from key #{old_index + 1} to key #{key_index + 1}")
                return True
            else:
                logger.error(f"Invalid key index: {key_index}")
                return False

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        with self.lock:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            recent_calls = [t for t in self.calls_log if t > one_minute_ago]

            # Calculate stats per key
            key_stats = []
            for i in range(len(self.api_keys)):
                key_stats.append({
                    'key_number': i + 1,
                    'daily_count': self.daily_counts[i],
                    'daily_limit': self.max_per_day,
                    'daily_remaining': self.max_per_day - self.daily_counts[i],
                    'daily_percentage': (self.daily_counts[i] / self.max_per_day * 100) if self.max_per_day > 0 else 0,
                    'is_active': i == self.current_key_index
                })

            # Calculate combined stats
            total_daily = sum(self.daily_counts.values())
            total_limit = len(self.api_keys) * self.max_per_day
            total_remaining = total_limit - total_daily

            return {
                'current_key_index': self.current_key_index,
                'current_key_number': self.current_key_index + 1,
                'total_keys': len(self.api_keys),
                'key_stats': key_stats,
                'total_daily_count': total_daily,
                'total_daily_limit': total_limit,
                'total_daily_remaining': total_remaining,
                'total_daily_percentage': (total_daily / total_limit * 100) if total_limit > 0 else 0,
                'minute_count': len(recent_calls),
                'minute_limit': self.max_per_minute,
                'minute_remaining': self.max_per_minute - len(recent_calls)
            }

    def get_usage_report(self) -> str:
        """Get formatted usage report"""
        stats = self.get_usage_stats()

        report = []
        report.append("=" * 70)
        report.append("API KEY ROTATOR - USAGE REPORT")
        report.append("=" * 70)
        report.append(f"Active Key: #{stats['current_key_number']} of {stats['total_keys']}")
        report.append(f"Per-Minute Usage: {stats['minute_count']} / {stats['minute_limit']} calls")
        report.append("")
        report.append("Daily Usage by Key:")

        for key_stat in stats['key_stats']:
            active_marker = "→" if key_stat['is_active'] else " "
            report.append(
                f"  {active_marker} Key #{key_stat['key_number']}: "
                f"{key_stat['daily_count']} / {key_stat['daily_limit']} calls "
                f"({key_stat['daily_percentage']:.1f}%) "
                f"[{key_stat['daily_remaining']} remaining]"
            )

        report.append("")
        report.append(
            f"Combined Total: {stats['total_daily_count']} / {stats['total_daily_limit']} calls "
            f"({stats['total_daily_percentage']:.1f}%)"
        )
        report.append(f"Total Remaining: {stats['total_daily_remaining']} calls")
        report.append("=" * 70)

        return "\n".join(report)


def load_api_keys_from_config(config: Dict) -> List[str]:
    """
    Load API keys from config and environment variables

    Args:
        config: Configuration dictionary

    Returns:
        List of valid API keys
    """
    twelvedata_config = config.get('twelvedata', {})
    api_keys = []

    # Try to load from api_keys list
    configured_keys = twelvedata_config.get('api_keys', [])
    if configured_keys:
        for i, key in enumerate(configured_keys):
            if key and key.strip():
                api_keys.append(key.strip())
            else:
                # Try environment variable
                env_key = os.getenv(f'TWELVEDATA_API_KEY_{i + 1}')
                if env_key:
                    api_keys.append(env_key.strip())

    # Fallback to legacy single key
    if not api_keys:
        legacy_key = twelvedata_config.get('api_key') or os.getenv('TWELVEDATA_API_KEY')
        if legacy_key and legacy_key.strip():
            api_keys.append(legacy_key.strip())

    # Filter out empty strings
    api_keys = [key for key in api_keys if key]

    if api_keys:
        logger.info(f"✅ Loaded {len(api_keys)} TwelveData API key(s)")
    else:
        logger.warning("⚠️ No TwelveData API keys found")

    return api_keys
