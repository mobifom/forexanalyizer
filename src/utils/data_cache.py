"""
In-Memory Data Cache Manager
Caches market data snapshots for fast access
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataCache:
    """Manages in-memory cache for market data"""

    def __init__(self, cache_duration_minutes: int = 15):
        """
        Initialize data cache

        Args:
            cache_duration_minutes: How long to keep cached data (default 15 minutes)
        """
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.last_update = {}

    def get_key(self, symbol: str, timeframe: str) -> str:
        """Generate cache key"""
        return f"{symbol}_{timeframe}"

    def set(self, symbol: str, timeframe: str, data: pd.DataFrame) -> None:
        """
        Store data in cache

        Args:
            symbol: Asset symbol
            timeframe: Timeframe (1d, 4h, 1h, 15m)
            data: DataFrame with market data
        """
        key = self.get_key(symbol, timeframe)
        self.cache[key] = data.copy()
        self.last_update[key] = datetime.now()
        logger.info(f"Cached {symbol} {timeframe}: {len(data)} candles")

    def get(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Retrieve data from cache

        Args:
            symbol: Asset symbol
            timeframe: Timeframe

        Returns:
            DataFrame if cached and fresh, None otherwise
        """
        key = self.get_key(symbol, timeframe)

        if key not in self.cache:
            return None

        # Check if cache is still fresh
        if self.is_fresh(key):
            logger.info(f"Cache HIT: {symbol} {timeframe}")
            return self.cache[key].copy()
        else:
            logger.info(f"Cache EXPIRED: {symbol} {timeframe}")
            # Remove expired cache
            del self.cache[key]
            del self.last_update[key]
            return None

    def is_fresh(self, key: str) -> bool:
        """Check if cached data is still fresh"""
        if key not in self.last_update:
            return False

        age = datetime.now() - self.last_update[key]
        return age < self.cache_duration

    def invalidate(self, symbol: str = None, timeframe: str = None) -> None:
        """
        Invalidate cache entries

        Args:
            symbol: If provided, only invalidate this symbol
            timeframe: If provided, only invalidate this timeframe
        """
        if symbol and timeframe:
            key = self.get_key(symbol, timeframe)
            if key in self.cache:
                del self.cache[key]
                del self.last_update[key]
                logger.info(f"Invalidated cache: {symbol} {timeframe}")
        elif symbol:
            # Invalidate all timeframes for this symbol
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(f"{symbol}_")]
            for key in keys_to_remove:
                del self.cache[key]
                del self.last_update[key]
            logger.info(f"Invalidated all cache for: {symbol}")
        else:
            # Clear all cache
            self.cache.clear()
            self.last_update.clear()
            logger.info("Cleared all cache")

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        fresh_count = sum(1 for key in self.cache.keys() if self.is_fresh(key))
        return {
            'total_entries': len(self.cache),
            'fresh_entries': fresh_count,
            'expired_entries': len(self.cache) - fresh_count,
            'symbols_cached': len(set(k.split('_')[0] for k in self.cache.keys()))
        }

    def preload_symbols(self, symbols: List[str], timeframes: List[str], data_fetcher) -> Dict:
        """
        Preload data for multiple symbols

        Args:
            symbols: List of symbols to preload
            timeframes: List of timeframes to preload
            data_fetcher: Data fetcher instance to use

        Returns:
            Dictionary with preload statistics
        """
        stats = {'success': 0, 'failed': 0, 'errors': []}

        logger.info(f"Preloading {len(symbols)} symbols across {len(timeframes)} timeframes...")

        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    # Fetch data
                    data = data_fetcher.fetch_data(symbol, timeframe, use_cache=False)

                    if data is not None and not data.empty:
                        # Store in cache
                        self.set(symbol, timeframe, data)
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1
                        stats['errors'].append(f"{symbol} {timeframe}: No data")

                except Exception as e:
                    stats['failed'] += 1
                    stats['errors'].append(f"{symbol} {timeframe}: {str(e)}")
                    logger.error(f"Failed to preload {symbol} {timeframe}: {e}")

        logger.info(f"Preload complete: {stats['success']} success, {stats['failed']} failed")
        return stats
