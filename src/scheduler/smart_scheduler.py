"""
Smart Scheduler for Optimized Data Retrieval
Manages automatic data fetching with API rate limiting and market hours awareness
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
import threading
from collections import defaultdict
import pytz
from src.utils.api_key_rotator import APIKeyRotator, load_api_keys_from_config

logger = logging.getLogger(__name__)


class APIUsageTracker:
    """Track API usage to respect rate limits"""

    def __init__(self, max_per_minute: int = 8, max_per_day: int = 800):
        """
        Initialize usage tracker

        Args:
            max_per_minute: Maximum API calls per minute
            max_per_day: Maximum API calls per day
        """
        self.max_per_minute = max_per_minute
        self.max_per_day = max_per_day

        # Track calls with timestamps
        self.calls_log = []
        self.daily_count = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0)

        self.lock = threading.Lock()

    def can_make_call(self) -> tuple[bool, str]:
        """
        Check if we can make an API call without exceeding limits

        Returns:
            Tuple of (can_call, reason)
        """
        with self.lock:
            now = datetime.now()

            # Reset daily counter if new day
            if now >= self.daily_reset_time + timedelta(days=1):
                self.daily_count = 0
                self.daily_reset_time = now.replace(hour=0, minute=0, second=0)
                logger.info("Daily API counter reset")

            # Check daily limit
            if self.daily_count >= self.max_per_day:
                return False, f"Daily limit reached ({self.daily_count}/{self.max_per_day})"

            # Check per-minute limit
            one_minute_ago = now - timedelta(minutes=1)
            recent_calls = [t for t in self.calls_log if t > one_minute_ago]

            if len(recent_calls) >= self.max_per_minute:
                return False, f"Per-minute limit reached ({len(recent_calls)}/{self.max_per_minute})"

            return True, "OK"

    def record_call(self):
        """Record that an API call was made"""
        with self.lock:
            now = datetime.now()
            self.calls_log.append(now)
            self.daily_count += 1

            # Clean up old entries (keep last hour)
            one_hour_ago = now - timedelta(hours=1)
            self.calls_log = [t for t in self.calls_log if t > one_hour_ago]

            logger.debug(f"API call recorded. Daily: {self.daily_count}/{self.max_per_day}")

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        with self.lock:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)
            recent_calls = [t for t in self.calls_log if t > one_minute_ago]

            return {
                'daily_count': self.daily_count,
                'daily_limit': self.max_per_day,
                'daily_remaining': self.max_per_day - self.daily_count,
                'daily_percentage': (self.daily_count / self.max_per_day * 100) if self.max_per_day > 0 else 0,
                'minute_count': len(recent_calls),
                'minute_limit': self.max_per_minute,
                'minute_remaining': self.max_per_minute - len(recent_calls)
            }

    def wait_if_needed(self) -> float:
        """
        Wait if necessary to respect rate limits

        Returns:
            Seconds waited
        """
        wait_time = 0
        while True:
            can_call, reason = self.can_make_call()
            if can_call:
                break

            # Calculate wait time
            if "minute" in reason:
                # Wait until oldest call in last minute expires
                now = datetime.now()
                one_minute_ago = now - timedelta(minutes=1)
                recent_calls = [t for t in self.calls_log if t > one_minute_ago]
                if recent_calls:
                    oldest = min(recent_calls)
                    sleep_time = (oldest + timedelta(minutes=1) - now).total_seconds() + 1
                else:
                    sleep_time = 10
            else:
                # Daily limit reached
                logger.warning(f"Daily API limit reached. Scheduler will pause until tomorrow.")
                sleep_time = 300  # Check again in 5 minutes

            logger.info(f"Rate limiting: {reason}. Waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)
            wait_time += sleep_time

        return wait_time


class MarketHoursChecker:
    """Check if market is open for different asset types"""

    def __init__(self, config: Dict):
        """
        Initialize market hours checker

        Args:
            config: Scheduler configuration with market hours
        """
        self.config = config.get('market_hours', {})
        self.respect_hours = config.get('respect_market_hours', True)
        self.timezone = pytz.timezone('US/Eastern')  # Default to ET

    def is_market_open(self, asset: str, asset_type: str = 'forex') -> bool:
        """
        Check if market is open for the given asset

        Args:
            asset: Asset symbol
            asset_type: Type of asset ('forex', 'indices', 'crypto')

        Returns:
            True if market is open
        """
        if not self.respect_hours:
            return True

        # Determine asset type if not provided
        if asset_type == 'forex':
            if 'US30' in asset or 'US100' in asset:
                asset_type = 'indices'
            elif 'BTC' in asset or 'ETH' in asset:
                asset_type = 'crypto'
            elif 'XAU' in asset or 'XAG' in asset:
                asset_type = 'forex'  # Commodities follow forex hours

        hours_config = self.config.get(asset_type, {})
        if not hours_config.get('enabled', True):
            return True  # If disabled, always open

        now = datetime.now(self.timezone)
        current_day = now.weekday()  # 0 = Monday, 6 = Sunday
        current_hour = now.hour

        # Check if current day is trading day
        trading_days = hours_config.get('days', [0, 1, 2, 3, 4])
        if current_day not in trading_days:
            return False

        # Check if within trading hours
        start_hour = hours_config.get('start_hour', 0)
        end_hour = hours_config.get('end_hour', 24)

        return start_hour <= current_hour < end_hour


class SmartScheduler:
    """Smart scheduler for optimized data retrieval"""

    def __init__(self, config: Dict):
        """
        Initialize smart scheduler

        Args:
            config: Configuration dictionary with scheduler settings
        """
        self.config = config
        self.scheduler_config = config.get('scheduler', {})
        self.enabled = self.scheduler_config.get('enabled', True)

        # Initialize API key management
        rate_limiting = self.scheduler_config.get('rate_limiting', {})
        max_per_minute = rate_limiting.get('max_calls_per_minute', 8)
        max_per_day = rate_limiting.get('max_calls_per_day', 800)

        # Try to load multiple API keys
        api_keys = load_api_keys_from_config(config)

        if len(api_keys) > 1:
            # Use API key rotator for multiple keys
            self.api_tracker = APIKeyRotator(
                api_keys=api_keys,
                max_per_day=max_per_day,
                max_per_minute=max_per_minute
            )
            self.using_key_rotation = True
            logger.info(f"✅ Using API Key Rotation with {len(api_keys)} keys")
            logger.info(f"   Total daily capacity: {len(api_keys) * max_per_day} calls/day")
        else:
            # Use single key tracker
            self.api_tracker = APIUsageTracker(
                max_per_minute=max_per_minute,
                max_per_day=max_per_day
            )
            self.using_key_rotation = False
            if api_keys:
                logger.info(f"✅ Using single API key")
            else:
                logger.warning(f"⚠️ No API keys configured - using fallback data sources")

        self.market_checker = MarketHoursChecker(self.scheduler_config)

        # Fetch intervals (in minutes)
        self.fetch_intervals = self.scheduler_config.get('fetch_intervals', {
            '15m': 15,
            '1h': 60,
            '4h': 240,
            '1d': 360
        })

        # Asset priorities
        priorities = self.scheduler_config.get('asset_priority', {})
        self.high_priority = set(priorities.get('high', []))
        self.medium_priority = set(priorities.get('medium', []))
        self.low_priority = set(priorities.get('low', []))

        # Auto-analysis settings
        self.auto_analysis = self.scheduler_config.get('auto_analysis', {})

        # Track last fetch times
        self.last_fetch = defaultdict(lambda: defaultdict(lambda: datetime.min))

        # Callbacks
        self.fetch_callback = None
        self.analysis_callback = None

        # Scheduler thread
        self.running = False
        self.scheduler_thread = None

        logger.info("SmartScheduler initialized")

    def register_fetch_callback(self, callback: Callable):
        """
        Register callback for data fetching

        Args:
            callback: Function to call for fetching data
                      Signature: callback(asset: str, timeframe: str) -> bool
        """
        self.fetch_callback = callback
        logger.info("Fetch callback registered")

    def register_analysis_callback(self, callback: Callable):
        """
        Register callback for analysis

        Args:
            callback: Function to call for analysis
                      Signature: callback(asset: str, timeframes: List[str]) -> None
        """
        self.analysis_callback = callback
        logger.info("Analysis callback registered")

    def should_fetch(self, asset: str, timeframe: str) -> bool:
        """
        Check if we should fetch data for this asset/timeframe

        Args:
            asset: Asset symbol
            timeframe: Timeframe identifier

        Returns:
            True if should fetch
        """
        # Check if enabled
        if not self.enabled:
            return False

        # Check market hours
        if not self.market_checker.is_market_open(asset):
            return False

        # Check if enough time has passed since last fetch
        interval_minutes = self._get_fetch_interval(asset, timeframe)
        last_time = self.last_fetch[asset][timeframe]
        now = datetime.now()

        time_elapsed = (now - last_time).total_seconds() / 60

        return time_elapsed >= interval_minutes

    def _get_fetch_interval(self, asset: str, timeframe: str) -> int:
        """
        Get fetch interval for asset/timeframe based on priority

        Args:
            asset: Asset symbol
            timeframe: Timeframe identifier

        Returns:
            Interval in minutes
        """
        base_interval = self.fetch_intervals.get(timeframe, 60)

        # Adjust based on priority
        if timeframe == '15m':
            if asset in self.high_priority:
                return base_interval  # Full frequency
            elif asset in self.medium_priority:
                return base_interval * 2  # Half frequency (30 min)
            else:  # Low priority
                return base_interval * 4  # Quarter frequency (1 hour)

        return base_interval

    def fetch_with_rate_limit(self, asset: str, timeframe: str) -> bool:
        """
        Fetch data for asset/timeframe with rate limiting

        Args:
            asset: Asset symbol
            timeframe: Timeframe identifier

        Returns:
            True if fetch successful
        """
        if not self.fetch_callback:
            logger.error("No fetch callback registered")
            return False

        # Check if we can make the call
        can_call, reason = self.api_tracker.can_make_call()
        if not can_call:
            logger.warning(f"Cannot fetch {asset} {timeframe}: {reason}")
            return False

        # Wait if needed (should rarely happen with smart scheduling)
        self.api_tracker.wait_if_needed()

        # Make the call
        try:
            logger.info(f"📊 Fetching {asset} {timeframe}")
            success = self.fetch_callback(asset, timeframe)

            if success:
                self.api_tracker.record_call()
                self.last_fetch[asset][timeframe] = datetime.now()
                logger.info(f"✅ Fetched {asset} {timeframe}")

                # Trigger analysis if enabled
                if self.auto_analysis.get('enabled', True):
                    self._trigger_analysis(asset, timeframe)

                return True
            else:
                logger.warning(f"❌ Failed to fetch {asset} {timeframe}")
                return False

        except Exception as e:
            logger.error(f"Error fetching {asset} {timeframe}: {e}")
            return False

    def _trigger_analysis(self, asset: str, timeframe: str):
        """
        Trigger analysis after data fetch

        Args:
            asset: Asset symbol
            timeframe: Timeframe that was fetched
        """
        if not self.analysis_callback:
            return

        trigger_timeframes = self.auto_analysis.get('trigger_on_timeframes', ['15m', '1h', '4h', '1d'])
        if timeframe not in trigger_timeframes:
            return

        # Delay before analysis
        delay = self.auto_analysis.get('delay_seconds', 2)
        if delay > 0:
            time.sleep(delay)

        try:
            # Batch analysis if enabled
            if self.auto_analysis.get('batch_analysis', True):
                # Analyze multiple timeframes if they were recently fetched
                recent_timeframes = [timeframe]
                for tf in ['15m', '1h', '4h', '1d']:
                    if tf != timeframe:
                        last_time = self.last_fetch[asset].get(tf, datetime.min)
                        if (datetime.now() - last_time).total_seconds() < 60:
                            recent_timeframes.append(tf)

                logger.info(f"🔍 Analyzing {asset} timeframes: {recent_timeframes}")
                self.analysis_callback(asset, recent_timeframes)
            else:
                logger.info(f"🔍 Analyzing {asset} {timeframe}")
                self.analysis_callback(asset, [timeframe])

        except Exception as e:
            logger.error(f"Error triggering analysis for {asset}: {e}")

    def run_scheduler_loop(self, assets: List[str], timeframes: List[str]):
        """
        Run the scheduler loop (blocking)

        Args:
            assets: List of asset symbols to monitor
            timeframes: List of timeframes to fetch
        """
        logger.info(f"Starting scheduler for {len(assets)} assets, {len(timeframes)} timeframes")
        self.running = True

        while self.running:
            try:
                cycle_start = time.time()

                # Check each asset/timeframe combination
                for asset in assets:
                    for timeframe in timeframes:
                        if not self.running:
                            break

                        if self.should_fetch(asset, timeframe):
                            self.fetch_with_rate_limit(asset, timeframe)

                        # Small delay between checks
                        time.sleep(0.1)

                    if not self.running:
                        break

                # Calculate sleep time until next check
                cycle_duration = time.time() - cycle_start
                sleep_time = max(60 - cycle_duration, 10)  # Check at least every minute

                # Log usage stats periodically
                stats = self.api_tracker.get_usage_stats()
                logger.info(
                    f"API Usage - Daily: {stats['daily_count']}/{stats['daily_limit']} "
                    f"({stats['daily_percentage']:.1f}%), "
                    f"Last Minute: {stats['minute_count']}/{stats['minute_limit']}"
                )

                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)

        logger.info("Scheduler stopped")

    def start(self, assets: List[str], timeframes: List[str]):
        """
        Start the scheduler in a background thread

        Args:
            assets: List of asset symbols to monitor
            timeframes: List of timeframes to fetch
        """
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.scheduler_thread = threading.Thread(
            target=self.run_scheduler_loop,
            args=(assets, timeframes),
            daemon=True
        )
        self.scheduler_thread.start()
        logger.info("Scheduler started in background thread")

    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            logger.warning("Scheduler not running")
            return

        logger.info("Stopping scheduler...")
        self.running = False

        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
            logger.info("Scheduler stopped")

    def get_usage_report(self) -> str:
        """
        Get formatted usage report

        Returns:
            Formatted string with usage statistics
        """
        if self.using_key_rotation:
            # Use the rotator's detailed report
            return self.api_tracker.get_usage_report()
        else:
            # Use single key report
            stats = self.api_tracker.get_usage_stats()

            report = []
            report.append("=" * 60)
            report.append("API USAGE REPORT")
            report.append("=" * 60)
            report.append(f"Daily Usage: {stats['daily_count']} / {stats['daily_limit']} calls")
            report.append(f"Daily Remaining: {stats['daily_remaining']} calls")
            report.append(f"Daily Percentage: {stats['daily_percentage']:.1f}%")
            report.append(f"Last Minute: {stats['minute_count']} / {stats['minute_limit']} calls")
            report.append("=" * 60)

            return "\n".join(report)
