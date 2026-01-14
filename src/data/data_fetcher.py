"""
Data Fetcher Module
Handles downloading and caching forex data from multiple sources
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
import pickle
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import in-memory cache
try:
    from ..utils.data_cache import DataCache
    MEMORY_CACHE_AVAILABLE = True
except ImportError:
    MEMORY_CACHE_AVAILABLE = False
    logger.debug("In-memory cache not available")

# Import data snapshots database
try:
    from ..database.data_snapshots_db import DataSnapshotsDB
    SNAPSHOTS_DB_AVAILABLE = True
except ImportError:
    SNAPSHOTS_DB_AVAILABLE = False
    logger.debug("Data snapshots DB not available")

# Import Twelve Data fetcher
try:
    from .twelvedata_fetcher import TwelveDataFetcher
    TWELVEDATA_AVAILABLE = True
except ImportError:
    TWELVEDATA_AVAILABLE = False
    logger.info("Twelve Data fetcher not available")

# Import Finnhub fetcher
try:
    from .finnhub_fetcher import FinnhubDataFetcher
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False
    logger.info("Finnhub fetcher not available")

# Import Oanda fetcher
try:
    from .oanda_fetcher import OandaDataFetcher, OANDA_AVAILABLE
except ImportError:
    OANDA_AVAILABLE = False
    logger.info("Oanda fetcher not available")


class ForexDataFetcher:
    """Fetches and caches forex data from multiple sources (yfinance, Oanda, MT5)"""

    def __init__(
        self,
        cache_dir: str = 'data/cache',
        cache_duration_minutes: int = 60,
        data_source: str = 'yfinance',
        twelvedata_api_key: str = None,
        twelvedata_api_key_provider=None,
        finnhub_api_key: str = None,
        oanda_api_key: str = None,
        oanda_account_type: str = 'practice'
    ):
        """
        Initialize the data fetcher

        Args:
            cache_dir: Directory to store cached data
            cache_duration_minutes: How long to cache data before refreshing
            data_source: Data source to use ('twelvedata', 'finnhub', 'yfinance', 'oanda', 'auto')
            twelvedata_api_key: Twelve Data API key (FREE - supports forex!)
            twelvedata_api_key_provider: Optional callable that returns current API key (for rotation)
            finnhub_api_key: Finnhub API key (Premium required for forex)
            oanda_api_key: Oanda API key (required if using Oanda)
            oanda_account_type: 'practice' or 'live' for Oanda
        """
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.data_source = data_source.lower()
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize in-memory cache
        self.memory_cache = None
        if MEMORY_CACHE_AVAILABLE:
            try:
                self.memory_cache = DataCache(cache_duration_minutes=cache_duration_minutes)
                logger.info("✅ In-memory cache initialized")
            except Exception as e:
                logger.warning(f"Could not initialize in-memory cache: {e}")

        # Initialize snapshots database
        self.snapshots_db = None
        if SNAPSHOTS_DB_AVAILABLE:
            try:
                self.snapshots_db = DataSnapshotsDB()
                logger.info("✅ Data snapshots database initialized")
            except Exception as e:
                logger.warning(f"Could not initialize snapshots DB: {e}")

        # Initialize Twelve Data fetcher if requested (BEST for free forex!)
        self.twelvedata_fetcher = None
        if self.data_source in ['twelvedata', 'auto'] and TWELVEDATA_AVAILABLE:
            # Try to get API key from Streamlit secrets first (for cloud deployment)
            api_key_to_use = twelvedata_api_key
            if not api_key_to_use and not twelvedata_api_key_provider:
                try:
                    import streamlit as st
                    api_key_to_use = st.secrets.get("TWELVEDATA_API_KEY", "")
                except Exception:
                    pass  # Streamlit secrets not available (local dev)

            if api_key_to_use or twelvedata_api_key_provider:
                try:
                    self.twelvedata_fetcher = TwelveDataFetcher(
                        api_key=api_key_to_use,
                        api_key_provider=twelvedata_api_key_provider
                    )
                    # Test API connection (only if we have a static key, not a provider)
                    if api_key_to_use and not twelvedata_api_key_provider:
                        if self.twelvedata_fetcher.check_api_status():
                            logger.info("✅ Twelve Data API initialized - Real-time forex data available!")
                        else:
                            logger.warning("⚠️ Twelve Data API key may be invalid")
                            self.twelvedata_fetcher = None
                    elif twelvedata_api_key_provider:
                        logger.info("✅ Twelve Data API initialized with key rotation - Real-time forex data available!")
                except Exception as e:
                    logger.warning(f"Failed to initialize Twelve Data: {e}")
                    self.twelvedata_fetcher = None

        # Initialize Finnhub fetcher if requested (Note: Free tier doesn't support forex!)
        self.finnhub_fetcher = None
        if self.data_source in ['finnhub', 'auto'] and FINNHUB_AVAILABLE:
            if finnhub_api_key:
                try:
                    self.finnhub_fetcher = FinnhubDataFetcher(api_key=finnhub_api_key)
                    logger.info("⚠️ Finnhub free tier does NOT support forex - only stocks")
                except Exception as e:
                    logger.warning(f"Failed to initialize Finnhub: {e}")
                    self.finnhub_fetcher = None

        # Initialize Oanda fetcher if requested
        self.oanda_fetcher = None
        if self.data_source in ['oanda', 'auto'] and OANDA_AVAILABLE:
            if oanda_api_key:
                try:
                    self.oanda_fetcher = OandaDataFetcher(
                        api_key=oanda_api_key,
                        account_type=oanda_account_type
                    )
                    logger.info(f"✅ Oanda fetcher initialized ({oanda_account_type} mode)")
                except Exception as e:
                    logger.warning(f"Failed to initialize Oanda: {e}")
                    self.oanda_fetcher = None

        # Log active data source
        sources = []
        if self.twelvedata_fetcher:
            sources.append("Twelve Data (real-time forex)")
        if self.finnhub_fetcher:
            sources.append("Finnhub (stocks only)")
        if self.oanda_fetcher:
            sources.append("Oanda")
        sources.append("yfinance (fallback)")

        if self.data_source == 'auto':
            logger.info(f"📊 Active data source: Auto ({' → '.join(sources)})")
        elif self.data_source == 'twelvedata' and self.twelvedata_fetcher:
            logger.info("📊 Active data source: Twelve Data (real-time forex)")
        elif self.data_source == 'finnhub' and self.finnhub_fetcher:
            logger.info("📊 Active data source: Finnhub (stocks only - forex needs premium)")
        elif self.data_source == 'oanda' and self.oanda_fetcher:
            logger.info("📊 Active data source: Oanda")
        else:
            logger.info("📊 Active data source: yfinance")

    def _get_cache_path(self, symbol: str, timeframe: str) -> str:
        """Generate cache file path for a symbol and timeframe"""
        return os.path.join(self.cache_dir, f"{symbol}_{timeframe}.pkl")

    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cached data is still valid"""
        if not os.path.exists(cache_path):
            return False

        cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - cache_time < self.cache_duration

    def _convert_timeframe(self, timeframe: str) -> str:
        """
        Convert timeframe notation to yfinance format

        Args:
            timeframe: Timeframe like '1d', '4h', '1h', '15m'

        Returns:
            yfinance compatible interval string
        """
        timeframe_map = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1wk',
            '1mo': '1mo'
        }
        return timeframe_map.get(timeframe.lower(), '1d')

    def _get_period_for_timeframe(self, timeframe: str) -> str:
        """Get appropriate data period based on timeframe"""
        period_map = {
            '15m': '60d',   # 60 days for 15min data
            '1h': '730d',   # 2 years for hourly
            '4h': '730d',   # 2 years for 4h
            '1d': '10y'     # Max for daily
        }
        return period_map.get(timeframe.lower(), '1y')

    def fetch_data(
        self,
        symbol: str,
        timeframe: str = '1d',
        use_cache: bool = True,
        use_snapshot: bool = True,
        max_snapshot_age_minutes: int = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch forex data for a given symbol and timeframe

        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD=X', 'EUR_USD')
            timeframe: Time interval ('1d', '4h', '1h', '15m')
            use_cache: Whether to use cached data if available
            use_snapshot: Whether to use data snapshots from scheduler (recommended)
            max_snapshot_age_minutes: Maximum age of snapshot (None = use_cache_duration)

        Returns:
            DataFrame with OHLCV data
        """
        # Try to load from in-memory cache first (fastest)
        if use_cache and self.memory_cache:
            cached_data = self.memory_cache.get(symbol, timeframe)
            if cached_data is not None:
                return cached_data

        # Try to load from snapshot second (scheduler's latest data)
        if use_snapshot and self.snapshots_db:
            max_age = max_snapshot_age_minutes if max_snapshot_age_minutes is not None else int(self.cache_duration.total_seconds() / 60)

            snapshot_data = self.snapshots_db.get_snapshot(
                asset_symbol=symbol,
                timeframe=timeframe,
                max_age_minutes=max_age
            )

            if snapshot_data is not None:
                logger.info(f"📸 Loading {symbol} {timeframe} from snapshot (batch job data)")
                # Update in-memory cache with snapshot data
                if self.memory_cache:
                    self.memory_cache.set(symbol, timeframe, snapshot_data)
                return snapshot_data

        cache_path = self._get_cache_path(symbol, timeframe)

        # Try to load from file cache
        if use_cache and self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    logger.info(f"Loading {symbol} {timeframe} from file cache")
                    cached_df = pickle.load(f)
                    # Update in-memory cache
                    if self.memory_cache:
                        self.memory_cache.set(symbol, timeframe, cached_df)
                    return cached_df
            except Exception as e:
                logger.warning(f"Cache load failed: {e}")

        # Decide which data source to use
        df = None

        # Try Twelve Data first if configured (BEST for free forex!)
        if self.data_source in ['twelvedata', 'auto'] and self.twelvedata_fetcher:
            try:
                logger.info(f"Fetching {symbol} {timeframe} from Twelve Data (real-time forex)")
                df = self.twelvedata_fetcher.fetch_candles(symbol, timeframe, limit=500)

                if df is not None and not df.empty:
                    logger.info(f"✅ Successfully fetched {len(df)} rows from Twelve Data")
                elif self.data_source == 'auto':
                    logger.warning("Twelve Data fetch failed, trying other sources")
                    df = None  # Force fallback
            except Exception as e:
                logger.warning(f"Twelve Data fetch error: {e}")
                if self.data_source == 'auto':
                    logger.info("Falling back to other sources")
                    df = None

        # Try Finnhub if Twelve Data failed (Note: won't work for forex on free tier)
        if df is None and self.data_source in ['finnhub', 'auto'] and self.finnhub_fetcher:
            try:
                logger.info(f"Fetching {symbol} {timeframe} from Finnhub")
                df = self.finnhub_fetcher.fetch_candles(symbol, timeframe, limit=500)

                if df is not None and not df.empty:
                    logger.info(f"✅ Successfully fetched {len(df)} rows from Finnhub")
                elif self.data_source == 'auto':
                    logger.warning("Finnhub fetch failed, trying other sources")
                    df = None  # Force fallback
            except Exception as e:
                logger.warning(f"Finnhub fetch error: {e}")
                if self.data_source == 'auto':
                    logger.info("Falling back to other sources")
                    df = None

        # Try Oanda if both failed
        if df is None and self.data_source in ['oanda', 'auto'] and self.oanda_fetcher:
            try:
                logger.info(f"Fetching {symbol} {timeframe} from Oanda")
                df = self.oanda_fetcher.fetch_data(symbol, timeframe)

                if df is not None and not df.empty:
                    logger.info(f"✅ Successfully fetched {len(df)} rows from Oanda")
                elif self.data_source == 'auto':
                    logger.warning("Oanda fetch failed, falling back to yfinance")
                    df = None  # Force fallback
            except Exception as e:
                logger.warning(f"Oanda fetch error: {e}")
                if self.data_source == 'auto':
                    logger.info("Falling back to yfinance")
                    df = None

        # Use yfinance if all else failed
        if df is None:
            df = self._fetch_from_yfinance(symbol, timeframe)

        # Cache the data if successful
        if df is not None and not df.empty and use_cache:
            # Update in-memory cache
            if self.memory_cache:
                self.memory_cache.set(symbol, timeframe, df)

            # Update file cache
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(df, f)
            except Exception as e:
                logger.warning(f"Failed to cache data: {e}")

        return df

    def _convert_symbol_for_yfinance(self, symbol: str) -> str:
        """
        Convert Oanda-style symbols to yfinance format

        Args:
            symbol: Symbol like 'XAU_USD', 'EUR_USD'

        Returns:
            yfinance compatible symbol
        """
        # Map Oanda spot to yfinance futures/pairs
        symbol_map = {
            'XAU_USD': 'GC=F',     # Gold spot → Gold futures
            'XAG_USD': 'SI=F',     # Silver spot → Silver futures
            'EUR_USD': 'EURUSD=X', # Forex pairs
            'GBP_USD': 'GBPUSD=X',
            'USD_JPY': 'USDJPY=X',
            'AUD_USD': 'AUDUSD=X',
            'USD_CHF': 'USDCHF=X',
            'NZD_USD': 'NZDUSD=X',
            'USD_CAD': 'USDCAD=X',
        }
        return symbol_map.get(symbol, symbol)

    def _fetch_from_yfinance(
        self,
        symbol: str,
        timeframe: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data from yfinance

        Args:
            symbol: Symbol to fetch
            timeframe: Timeframe

        Returns:
            DataFrame or None
        """
        try:
            # Convert symbol to yfinance format if needed
            yf_symbol = self._convert_symbol_for_yfinance(symbol)
            logger.info(f"Fetching {symbol} (as {yf_symbol}) {timeframe} from yfinance")
            interval = self._convert_timeframe(timeframe)
            period = self._get_period_for_timeframe(timeframe)

            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.error(f"No data received from yfinance for {symbol}")
                return None

            # Clean the data
            df = df.dropna()
            df.index.name = 'Date'

            logger.info(f"Fetched {len(df)} rows from yfinance for {symbol} {timeframe}")
            return df

        except Exception as e:
            logger.error(f"Error fetching from yfinance for {symbol}: {e}")
            return None

    def fetch_multiple_timeframes(
        self,
        symbol: str,
        timeframes: list,
        use_cache: bool = True,
        use_snapshot: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple timeframes

        Args:
            symbol: Forex pair symbol
            timeframes: List of timeframes to fetch
            use_cache: Whether to use cached data
            use_snapshot: Whether to use data snapshots from scheduler

        Returns:
            Dictionary mapping timeframe to DataFrame
        """
        data = {}
        for tf in timeframes:
            df = self.fetch_data(symbol, tf, use_cache, use_snapshot)
            if df is not None:
                data[tf] = df

        return data

    def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = '1d',
        period: str = '365d',
        use_cache: bool = True,
        use_snapshot: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Alias for fetch_data (compatibility with scheduler)

        Args:
            symbol: Asset symbol
            interval: Timeframe
            period: Period (ignored, kept for compatibility)
            use_cache: Whether to use cache
            use_snapshot: Whether to use snapshots

        Returns:
            DataFrame with OHLCV data
        """
        return self.fetch_data(symbol, interval, use_cache, use_snapshot)

    def clear_cache(self):
        """Clear all cached data"""
        try:
            # Clear in-memory cache
            if self.memory_cache:
                self.memory_cache.invalidate()
                logger.info("In-memory cache cleared")

            # Clear file cache
            for file in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, file))
            logger.info("File cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def preload_data(self, symbols: list, timeframes: list) -> Dict:
        """
        Preload data for multiple symbols and timeframes into in-memory cache

        Args:
            symbols: List of symbols to preload
            timeframes: List of timeframes to preload

        Returns:
            Dictionary with preload statistics
        """
        if not self.memory_cache:
            logger.warning("In-memory cache not available for preloading")
            return {'success': 0, 'failed': 0, 'errors': ['In-memory cache not available']}

        logger.info(f"🚀 Preloading {len(symbols)} symbols across {len(timeframes)} timeframes...")
        stats = {'success': 0, 'failed': 0, 'errors': []}

        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    # Fetch data (will automatically populate memory cache)
                    data = self.fetch_data(symbol, timeframe, use_cache=True, use_snapshot=True)

                    if data is not None and not data.empty:
                        stats['success'] += 1
                        logger.info(f"  ✅ Preloaded {symbol} {timeframe}")
                    else:
                        stats['failed'] += 1
                        stats['errors'].append(f"{symbol} {timeframe}: No data")
                        logger.warning(f"  ❌ Failed to preload {symbol} {timeframe}: No data")

                except Exception as e:
                    stats['failed'] += 1
                    stats['errors'].append(f"{symbol} {timeframe}: {str(e)}")
                    logger.error(f"  ❌ Failed to preload {symbol} {timeframe}: {e}")

        logger.info(f"✨ Preload complete: {stats['success']} success, {stats['failed']} failed")

        # Log cache statistics
        if self.memory_cache:
            cache_stats = self.memory_cache.get_stats()
            logger.info(f"📊 Cache stats: {cache_stats['fresh_entries']} fresh, {cache_stats['expired_entries']} expired")

        return stats

    def get_cache_stats(self) -> Dict:
        """
        Get in-memory cache statistics

        Returns:
            Dictionary with cache statistics
        """
        if not self.memory_cache:
            return {'error': 'In-memory cache not available'}

        return self.memory_cache.get_stats()


# MetaTrader5 integration (optional - requires MT5 installed)
try:
    import MetaTrader5 as mt5

    class MT5DataFetcher:
        """Fetches forex data from MetaTrader5"""

        def __init__(self):
            """Initialize MT5 connection"""
            self.initialized = False

        def connect(self) -> bool:
            """Connect to MT5 terminal"""
            if not mt5.initialize():
                logger.error("MT5 initialization failed")
                return False

            self.initialized = True
            logger.info("MT5 connected successfully")
            return True

        def disconnect(self):
            """Disconnect from MT5"""
            if self.initialized:
                mt5.shutdown()
                self.initialized = False

        def fetch_data(
            self,
            symbol: str,
            timeframe: str = '1d',
            bars: int = 1000
        ) -> Optional[pd.DataFrame]:
            """
            Fetch data from MT5

            Args:
                symbol: Symbol name (e.g., 'EURUSD')
                timeframe: Timeframe
                bars: Number of bars to fetch

            Returns:
                DataFrame with OHLCV data
            """
            if not self.initialized:
                if not self.connect():
                    return None

            # Map timeframes
            tf_map = {
                '1m': mt5.TIMEFRAME_M1,
                '5m': mt5.TIMEFRAME_M5,
                '15m': mt5.TIMEFRAME_M15,
                '30m': mt5.TIMEFRAME_M30,
                '1h': mt5.TIMEFRAME_H1,
                '4h': mt5.TIMEFRAME_H4,
                '1d': mt5.TIMEFRAME_D1,
                '1w': mt5.TIMEFRAME_W1,
            }

            mt5_timeframe = tf_map.get(timeframe.lower(), mt5.TIMEFRAME_D1)

            try:
                rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, bars)

                if rates is None or len(rates) == 0:
                    logger.error(f"No data received from MT5 for {symbol}")
                    return None

                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df.set_index('time', inplace=True)
                df.rename(columns={
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'tick_volume': 'Volume'
                }, inplace=True)

                return df[['Open', 'High', 'Low', 'Close', 'Volume']]

            except Exception as e:
                logger.error(f"Error fetching MT5 data: {e}")
                return None

        def __del__(self):
            """Cleanup on object destruction"""
            self.disconnect()

except ImportError:
    logger.info("MetaTrader5 not available - only yfinance will be used")
    MT5DataFetcher = None
