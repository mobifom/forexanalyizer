"""
Finnhub Real-Time Data Fetcher
Provides real-time forex OHLC data using Finnhub API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)


class FinnhubDataFetcher:
    """Fetch real-time forex data from Finnhub API"""

    BASE_URL = "https://finnhub.io/api/v1"

    # Timeframe mapping
    TIMEFRAME_MAP = {
        '1m': '1',
        '5m': '5',
        '15m': '15',
        '30m': '30',
        '1h': '60',
        '4h': '240',
        '1d': 'D',
        '1w': 'W',
        '1M': 'M'
    }

    # Symbol mapping (Yahoo Finance to Finnhub format)
    SYMBOL_MAP = {
        'EURUSD=X': 'OANDA:EUR_USD',
        'GBPUSD=X': 'OANDA:GBP_USD',
        'USDJPY=X': 'OANDA:USD_JPY',
        'AUDUSD=X': 'OANDA:AUD_USD',
        'USDCHF=X': 'OANDA:USD_CHF',
        'NZDUSD=X': 'OANDA:NZD_USD',
        'USDCAD=X': 'OANDA:USD_CAD',
        'EURJPY=X': 'OANDA:EUR_JPY',
        'GBPJPY=X': 'OANDA:GBP_JPY',
        'EURGBP=X': 'OANDA:EUR_GBP',
        # Add gold/silver (use forex pairs)
        'XAUUSD=X': 'OANDA:XAU_USD',
        'XAGUSD=X': 'OANDA:XAG_USD',
        'GC=F': 'OANDA:XAU_USD',  # Gold futures
        'SI=F': 'OANDA:XAG_USD',  # Silver futures
    }

    def __init__(self, api_key: str):
        """
        Initialize Finnhub data fetcher

        Args:
            api_key: Finnhub API key (get from https://finnhub.io)
        """
        self.api_key = api_key
        self.session = requests.Session()

    def _convert_symbol(self, symbol: str) -> str:
        """
        Convert symbol to Finnhub format

        Args:
            symbol: Symbol in Yahoo Finance format

        Returns:
            Symbol in Finnhub format (OANDA:EUR_USD)
        """
        # Check if already in Finnhub format
        if ':' in symbol and '_' in symbol:
            return symbol

        # Direct mapping
        if symbol in self.SYMBOL_MAP:
            return self.SYMBOL_MAP[symbol]

        # Try to parse if it's a standard pair
        # Remove =X suffix if present
        clean_symbol = symbol.replace('=X', '').replace('=F', '')

        # Handle special cases
        if clean_symbol == 'XAU_USD' or clean_symbol == 'XAUUSD':
            return 'OANDA:XAU_USD'
        if clean_symbol == 'XAG_USD' or clean_symbol == 'XAGUSD':
            return 'OANDA:XAG_USD'

        # Standard forex pair (6 characters)
        if len(clean_symbol) == 6:
            base = clean_symbol[:3]
            quote = clean_symbol[3:]
            return f'OANDA:{base}_{quote}'

        # If we can't convert, return as-is and let API handle it
        logger.warning(f"Could not convert symbol {symbol}, using as-is")
        return symbol

    def _get_timeframe_resolution(self, timeframe: str) -> str:
        """
        Convert timeframe to Finnhub resolution

        Args:
            timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)

        Returns:
            Finnhub resolution string
        """
        return self.TIMEFRAME_MAP.get(timeframe, 'D')

    def fetch_candles(
        self,
        symbol: str,
        timeframe: str = '1d',
        limit: int = 200,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> pd.DataFrame:
        """
        Fetch OHLC candlestick data from Finnhub

        Args:
            symbol: Currency pair symbol
            timeframe: Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
            limit: Number of candles to fetch
            start_date: Start date (optional)
            end_date: End date (optional)

        Returns:
            DataFrame with OHLC data
        """
        try:
            # Convert symbol
            finnhub_symbol = self._convert_symbol(symbol)
            resolution = self._get_timeframe_resolution(timeframe)

            # Calculate date range if not provided
            if end_date is None:
                end_date = datetime.now()

            if start_date is None:
                # Calculate based on timeframe and limit
                if timeframe in ['1m', '5m', '15m', '30m']:
                    days_back = (limit * int(timeframe.replace('m', ''))) / (60 * 24)
                elif timeframe == '1h':
                    days_back = limit / 24
                elif timeframe == '4h':
                    days_back = (limit * 4) / 24
                elif timeframe == '1d':
                    days_back = limit
                elif timeframe == '1w':
                    days_back = limit * 7
                else:
                    days_back = limit

                start_date = end_date - timedelta(days=max(days_back, 30))

            # Convert to Unix timestamps
            from_ts = int(start_date.timestamp())
            to_ts = int(end_date.timestamp())

            # API endpoint
            url = f"{self.BASE_URL}/forex/candle"
            params = {
                'symbol': finnhub_symbol,
                'resolution': resolution,
                'from': from_ts,
                'to': to_ts,
                'token': self.api_key
            }

            logger.info(f"Fetching {symbol} ({finnhub_symbol}) {timeframe} from Finnhub")

            # Make request
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check for errors
            if data.get('s') == 'no_data':
                logger.warning(f"No data available for {symbol} {timeframe}")
                return pd.DataFrame()

            if 'c' not in data or len(data['c']) == 0:
                logger.warning(f"Empty response for {symbol} {timeframe}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame({
                'Open': data['o'],
                'High': data['h'],
                'Low': data['l'],
                'Close': data['c'],
                'Volume': data.get('v', [0] * len(data['c'])),
                'timestamp': data['t']
            })

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)

            # Limit to requested number of candles
            if len(df) > limit:
                df = df.tail(limit)

            logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")

            return df

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error("Finnhub API rate limit exceeded")
            else:
                logger.error(f"HTTP error fetching {symbol}: {e}")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error fetching {symbol} from Finnhub: {e}")
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
            finnhub_symbol = self._convert_symbol(symbol)

            url = f"{self.BASE_URL}/quote"
            params = {
                'symbol': finnhub_symbol,
                'token': self.api_key
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            return {
                'symbol': symbol,
                'current': data.get('c', 0),  # Current price
                'high': data.get('h', 0),     # High of the day
                'low': data.get('l', 0),      # Low of the day
                'open': data.get('o', 0),     # Open price
                'previous_close': data.get('pc', 0),  # Previous close
                'timestamp': datetime.fromtimestamp(data.get('t', time.time()))
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
