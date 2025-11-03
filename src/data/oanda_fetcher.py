"""
Oanda Data Fetcher Module
Handles downloading forex data from Oanda API
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

try:
    from oandapyV20 import API
    from oandapyV20.endpoints.instruments import InstrumentsCandles
    from oandapyV20.exceptions import V20Error
    OANDA_AVAILABLE = True
except ImportError:
    OANDA_AVAILABLE = False
    logging.warning("oandapyV20 not installed. Install with: pip install oandapyV20")

logger = logging.getLogger(__name__)


class OandaDataFetcher:
    """Fetches forex data from Oanda API"""

    def __init__(self, api_key: str = None, account_type: str = 'practice'):
        """
        Initialize Oanda data fetcher

        Args:
            api_key: Oanda API key (from Oanda account)
            account_type: 'practice' for demo account or 'live' for real account
        """
        if not OANDA_AVAILABLE:
            raise ImportError("oandapyV20 not installed. Install with: pip install oandapyV20")

        self.api_key = api_key
        self.account_type = account_type

        # Initialize API client
        if api_key:
            self.client = API(access_token=api_key, environment=account_type)
            self.initialized = True
            logger.info(f"Oanda API initialized in {account_type} mode")
        else:
            self.client = None
            self.initialized = False
            logger.warning("No Oanda API key provided. Set OANDA_API_KEY in config.")

    def _convert_symbol(self, symbol: str) -> str:
        """
        Convert yfinance/MT5 symbol format to Oanda format

        Args:
            symbol: Symbol like 'EURUSD=X', 'EURUSD', 'GC=F'

        Returns:
            Oanda format like 'EUR_USD', 'XAU_USD'
        """
        # Remove =X suffix if present
        symbol = symbol.replace('=X', '').replace('=F', '')

        # Handle forex pairs
        if len(symbol) == 6 and symbol.isalpha():
            # Standard forex pair like EURUSD
            return f"{symbol[:3]}_{symbol[3:]}"

        # Handle gold/silver
        symbol_map = {
            'GC': 'XAU_USD',       # Gold futures
            'XAUUSD': 'XAU_USD',   # Gold without underscore
            'XAU_USD': 'XAU_USD',  # Gold with underscore (already correct)
            'GOLD': 'XAU_USD',
            'SI': 'XAG_USD',       # Silver futures
            'XAGUSD': 'XAG_USD',   # Silver without underscore
            'XAG_USD': 'XAG_USD',  # Silver with underscore (already correct)
            'SILVER': 'XAG_USD',
        }

        return symbol_map.get(symbol.upper(), symbol)

    def _convert_timeframe(self, timeframe: str) -> str:
        """
        Convert timeframe to Oanda granularity format

        Args:
            timeframe: Timeframe like '1d', '4h', '1h', '15m'

        Returns:
            Oanda granularity like 'D', 'H4', 'H1', 'M15'
        """
        timeframe_map = {
            '1m': 'M1',
            '5m': 'M5',
            '15m': 'M15',
            '30m': 'M30',
            '1h': 'H1',
            '2h': 'H2',
            '3h': 'H3',
            '4h': 'H4',
            '8h': 'H8',
            '12h': 'H12',
            '1d': 'D',
            '1w': 'W',
            '1mo': 'M'
        }
        return timeframe_map.get(timeframe.lower(), 'D')

    def _get_candle_count(self, timeframe: str) -> int:
        """
        Get appropriate number of candles to fetch based on timeframe

        Args:
            timeframe: Timeframe string

        Returns:
            Number of candles to fetch
        """
        count_map = {
            '15m': 2000,  # ~20 days
            '1h': 2000,   # ~83 days
            '4h': 2000,   # ~333 days
            '1d': 2500    # ~7 years (Oanda max is 5000)
        }
        return count_map.get(timeframe.lower(), 1000)

    def fetch_data(
        self,
        symbol: str,
        timeframe: str = '1d',
        count: int = None
    ) -> Optional[pd.DataFrame]:
        """
        Fetch forex data from Oanda

        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD=X', 'EURUSD')
            timeframe: Time interval ('1d', '4h', '1h', '15m')
            count: Number of candles to fetch (default varies by timeframe)

        Returns:
            DataFrame with OHLCV data
        """
        if not self.initialized or not self.client:
            logger.error("Oanda API not initialized. Check API key configuration.")
            return None

        try:
            # Convert symbol and timeframe
            oanda_symbol = self._convert_symbol(symbol)
            granularity = self._convert_timeframe(timeframe)

            # Get candle count
            if count is None:
                count = self._get_candle_count(timeframe)

            logger.info(f"Fetching {oanda_symbol} {granularity} from Oanda (count={count})")

            # Prepare request parameters
            params = {
                "granularity": granularity,
                "count": count,
                "price": "MBA"  # Mid, Bid, Ask prices
            }

            # Make API request
            request = InstrumentsCandles(instrument=oanda_symbol, params=params)
            response = self.client.request(request)

            # Parse response
            candles = response.get('candles', [])

            if not candles:
                logger.error(f"No data received from Oanda for {oanda_symbol}")
                return None

            # Convert to DataFrame
            data = []
            for candle in candles:
                if candle['complete']:  # Only use complete candles
                    data.append({
                        'Date': pd.to_datetime(candle['time']),
                        'Open': float(candle['mid']['o']),
                        'High': float(candle['mid']['h']),
                        'Low': float(candle['mid']['l']),
                        'Close': float(candle['mid']['c']),
                        'Volume': int(candle['volume'])
                    })

            df = pd.DataFrame(data)
            df.set_index('Date', inplace=True)
            df = df.dropna()

            logger.info(f"Fetched {len(df)} rows from Oanda for {oanda_symbol} {granularity}")
            return df

        except V20Error as e:
            logger.error(f"Oanda API error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Oanda data for {symbol}: {e}")
            return None

    def get_account_info(self) -> Optional[Dict]:
        """
        Get Oanda account information

        Returns:
            Dictionary with account details or None
        """
        if not self.initialized or not self.client:
            logger.error("Oanda API not initialized")
            return None

        try:
            from oandapyV20.endpoints.accounts import AccountList

            request = AccountList()
            response = self.client.request(request)
            return response
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            return None

    def get_instruments(self) -> Optional[list]:
        """
        Get list of available instruments from Oanda

        Returns:
            List of instrument names
        """
        if not self.initialized or not self.client:
            logger.error("Oanda API not initialized")
            return None

        try:
            from oandapyV20.endpoints.accounts import AccountInstruments

            # Get first account ID
            account_info = self.get_account_info()
            if not account_info or 'accounts' not in account_info:
                return None

            account_id = account_info['accounts'][0]['id']

            request = AccountInstruments(accountID=account_id)
            response = self.client.request(request)

            instruments = [inst['name'] for inst in response.get('instruments', [])]
            logger.info(f"Found {len(instruments)} instruments")
            return instruments

        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test Oanda API connection

        Returns:
            True if connection successful, False otherwise
        """
        if not self.initialized or not self.client:
            logger.error("Oanda API not initialized")
            return False

        try:
            # Try to fetch account info
            account_info = self.get_account_info()
            if account_info and 'accounts' in account_info:
                logger.info("✅ Oanda API connection successful")
                logger.info(f"Found {len(account_info['accounts'])} account(s)")
                return True
            else:
                logger.error("❌ Oanda API connection failed")
                return False

        except Exception as e:
            logger.error(f"❌ Oanda connection test failed: {e}")
            return False
