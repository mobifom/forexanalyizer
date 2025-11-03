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
            finnhub_api_key: Finnhub API key (Premium required for forex)
            oanda_api_key: Oanda API key (required if using Oanda)
            oanda_account_type: 'practice' or 'live' for Oanda
        """
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.data_source = data_source.lower()
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize Twelve Data fetcher if requested (BEST for free forex!)
        self.twelvedata_fetcher = None
        if self.data_source in ['twelvedata', 'auto'] and TWELVEDATA_AVAILABLE:
            # Try to get API key from Streamlit secrets first (for cloud deployment)
            api_key_to_use = twelvedata_api_key
            if not api_key_to_use:
                try:
                    import streamlit as st
                    api_key_to_use = st.secrets.get("TWELVEDATA_API_KEY", "")
                except Exception:
                    pass  # Streamlit secrets not available (local dev)

            if api_key_to_use:
                try:
                    self.twelvedata_fetcher = TwelveDataFetcher(api_key=api_key_to_use)
                    # Test API connection
                    if self.twelvedata_fetcher.check_api_status():
                        logger.info("✅ Twelve Data API initialized - Real-time forex data available!")
                    else:
                        logger.warning("⚠️ Twelve Data API key may be invalid")
                        self.twelvedata_fetcher = None
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
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Fetch forex data for a given symbol and timeframe

        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD=X', 'EUR_USD')
            timeframe: Time interval ('1d', '4h', '1h', '15m')
            use_cache: Whether to use cached data if available

        Returns:
            DataFrame with OHLCV data
        """
        cache_path = self._get_cache_path(symbol, timeframe)

        # Try to load from cache
        if use_cache and self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    logger.info(f"Loading {symbol} {timeframe} from cache")
                    return pickle.load(f)
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
        use_cache: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple timeframes

        Args:
            symbol: Forex pair symbol
            timeframes: List of timeframes to fetch
            use_cache: Whether to use cached data

        Returns:
            Dictionary mapping timeframe to DataFrame
        """
        data = {}
        for tf in timeframes:
            df = self.fetch_data(symbol, tf, use_cache)
            if df is not None:
                data[tf] = df

        return data

    def clear_cache(self):
        """Clear all cached data"""
        try:
            for file in os.listdir(self.cache_dir):
                os.remove(os.path.join(self.cache_dir, file))
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


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
