"""
Twelve Data Real-Time Data Fetcher
Provides real-time forex OHLC data using Twelve Data API
FREE tier: 8 calls/minute, 800/day - Supports Forex!
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)


class TwelveDataFetcher:
    """Fetch real-time forex data from Twelve Data API"""

    BASE_URL = "https://api.twelvedata.com"

    # Timeframe mapping
    TIMEFRAME_MAP = {
        '1m': '1min',
        '5m': '5min',
        '15m': '15min',
        '30m': '30min',
        '1h': '1h',
        '2h': '2h',
        '4h': '4h',
        '1d': '1day',
        '1w': '1week',
        '1M': '1month'
    }

    # Symbol mapping (Yahoo Finance to Twelve Data format)
    SYMBOL_MAP = {
        'EURUSD=X': 'EUR/USD',
        'GBPUSD=X': 'GBP/USD',
        'USDJPY=X': 'USD/JPY',
        'AUDUSD=X': 'AUD/USD',
        'USDCHF=X': 'USD/CHF',
        'NZDUSD=X': 'NZD/USD',
        'USDCAD=X': 'USD/CAD',
        'EURJPY=X': 'EUR/JPY',
        'GBPJPY=X': 'GBP/JPY',
        'EURGBP=X': 'EUR/GBP',
        # Gold and Silver
        'XAUUSD=X': 'XAU/USD',
        'XAGUSD=X': 'XAG/USD',
        'XAU_USD': 'XAU/USD',
        'XAG_USD': 'XAG/USD',
        'GC=F': 'XAU/USD',
        'SI=F': 'XAG/USD',
    }

    def __init__(self, api_key: str, min_request_interval: float = 10.0):
        """
        Initialize Twelve Data fetcher

        Args:
            api_key: Twelve Data API key (get from https://twelvedata.com)
            min_request_interval: Minimum seconds between API calls (default: 10)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.min_request_interval = min_request_interval
        self.last_request_time = 0

    def _rate_limit(self):
        """
        Enforce rate limiting between API calls
        Ensures at least min_request_interval seconds between requests
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.info(f"⏱️  Rate limiting: waiting {sleep_time:.1f}s before next API call")
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _convert_symbol(self, symbol: str) -> str:
        """
        Convert symbol to Twelve Data format

        Args:
            symbol: Symbol in Yahoo Finance format

        Returns:
            Symbol in Twelve Data format (EUR/USD)
        """
        # Check if already in Twelve Data format
        if '/' in symbol:
            return symbol

        # Direct mapping
        if symbol in self.SYMBOL_MAP:
            return self.SYMBOL_MAP[symbol]

        # Try to parse if it's a standard pair
        # Remove =X suffix if present
        clean_symbol = symbol.replace('=X', '').replace('=F', '')

        # Handle special cases
        if clean_symbol in ['XAUUSD', 'XAU_USD']:
            return 'XAU/USD'
        if clean_symbol in ['XAGUSD', 'XAG_USD']:
            return 'XAG/USD'

        # Standard forex pair (6 characters)
        if len(clean_symbol) == 6:
            base = clean_symbol[:3]
            quote = clean_symbol[3:]
            return f'{base}/{quote}'

        # If we can't convert, return as-is and let API handle it
        logger.warning(f"Could not convert symbol {symbol}, using as-is")
        return symbol

    def _get_timeframe_interval(self, timeframe: str) -> str:
        """
        Convert timeframe to Twelve Data interval

        Args:
            timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)

        Returns:
            Twelve Data interval string
        """
        return self.TIMEFRAME_MAP.get(timeframe, '1day')

    def fetch_candles(
        self,
        symbol: str,
        timeframe: str = '1d',
        limit: int = 200
    ) -> pd.DataFrame:
        """
        Fetch OHLC candlestick data from Twelve Data

        Args:
            symbol: Currency pair symbol
            timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
            limit: Number of candles to fetch (max 5000)

        Returns:
            DataFrame with OHLC data
        """
        try:
            # Convert symbol and timeframe
            td_symbol = self._convert_symbol(symbol)
            interval = self._get_timeframe_interval(timeframe)

            # API endpoint
            url = f"{self.BASE_URL}/time_series"
            params = {
                'symbol': td_symbol,
                'interval': interval,
                'outputsize': min(limit, 5000),  # Max 5000
                'apikey': self.api_key
            }

            logger.info(f"Fetching {symbol} ({td_symbol}) {timeframe} from Twelve Data")

            # Rate limit before making request
            self._rate_limit()

            # Make request
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()

            # Check for errors
            if 'status' in data and data['status'] == 'error':
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"Twelve Data API error: {error_msg}")
                return pd.DataFrame()

            if 'code' in data:
                # API returned an error code
                logger.error(f"Twelve Data error {data['code']}: {data.get('message', '')}")
                return pd.DataFrame()

            if 'values' not in data or len(data['values']) == 0:
                logger.warning(f"No data available for {symbol} {timeframe}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(data['values'])

            # Convert columns to proper types
            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df.get('volume', 0))

            # Rename columns to match our format
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume',
                'datetime': 'timestamp'
            }, inplace=True)

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)

            logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")

            return df

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("Twelve Data API rate limit exceeded (8 calls/min on free tier)")
            elif e.response.status_code == 401:
                logger.error("Twelve Data API key is invalid or expired")
            else:
                logger.error(f"HTTP error fetching {symbol}: {e}")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error fetching {symbol} from Twelve Data: {e}")
            return pd.DataFrame()

    def get_quote(self, symbol: str) -> dict:
        """
        Get current quote for a symbol

        Args:
            symbol: Currency pair symbol

        Returns:
            Dictionary with current price data
        """
        try:
            td_symbol = self._convert_symbol(symbol)

            url = f"{self.BASE_URL}/quote"
            params = {
                'symbol': td_symbol,
                'apikey': self.api_key
            }

            # Rate limit before making request
            self._rate_limit()

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'code' in data:
                logger.error(f"Error getting quote: {data.get('message', '')}")
                return {}

            return {
                'symbol': symbol,
                'current': float(data.get('close', 0)),
                'high': float(data.get('high', 0)),
                'low': float(data.get('low', 0)),
                'open': float(data.get('open', 0)),
                'previous_close': float(data.get('previous_close', 0)),
                'change': float(data.get('change', 0)),
                'percent_change': float(data.get('percent_change', 0)),
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return {}

    def check_api_status(self) -> bool:
        """
        Check if API key is valid and service is accessible

        Returns:
            True if API is working, False otherwise
        """
        try:
            # Try to fetch a quote
            result = self.get_quote('EURUSD=X')
            return bool(result and result.get('current', 0) > 0)

        except Exception as e:
            logger.error(f"API status check failed: {e}")
            return False
