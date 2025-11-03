"""
Technical Indicators Module
Implements various technical indicators for forex analysis
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for forex trading"""

    @staticmethod
    def add_moving_averages(df: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
        """
        Add Simple Moving Averages

        Args:
            df: DataFrame with OHLCV data
            periods: List of MA periods

        Returns:
            DataFrame with MA columns added
        """
        for period in periods:
            df[f'MA_{period}'] = df['Close'].rolling(window=period).mean()

        return df

    @staticmethod
    def add_exponential_moving_averages(df: pd.DataFrame, periods: list = [12, 26, 50]) -> pd.DataFrame:
        """
        Add Exponential Moving Averages

        Args:
            df: DataFrame with OHLCV data
            periods: List of EMA periods

        Returns:
            DataFrame with EMA columns added
        """
        for period in periods:
            df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()

        return df

    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Relative Strength Index

        Args:
            df: DataFrame with OHLCV data
            period: RSI period

        Returns:
            DataFrame with RSI column added
        """
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    @staticmethod
    def add_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """
        Add MACD (Moving Average Convergence Divergence)

        Args:
            df: DataFrame with OHLCV data
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            DataFrame with MACD columns added
        """
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()

        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        return df

    @staticmethod
    def add_stochastic(
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> pd.DataFrame:
        """
        Add Stochastic Oscillator

        Args:
            df: DataFrame with OHLCV data
            k_period: %K period
            d_period: %D period

        Returns:
            DataFrame with Stochastic columns added
        """
        low_min = df['Low'].rolling(window=k_period).min()
        high_max = df['High'].rolling(window=k_period).max()

        df['Stoch_K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
        df['Stoch_D'] = df['Stoch_K'].rolling(window=d_period).mean()

        return df

    @staticmethod
    def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Add Average True Range

        Args:
            df: DataFrame with OHLCV data
            period: ATR period

        Returns:
            DataFrame with ATR column added
        """
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = true_range.rolling(window=period).mean()

        return df

    @staticmethod
    def add_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> pd.DataFrame:
        """
        Add Bollinger Bands

        Args:
            df: DataFrame with OHLCV data
            period: Moving average period
            std_dev: Number of standard deviations

        Returns:
            DataFrame with Bollinger Band columns added
        """
        df['BB_Middle'] = df['Close'].rolling(window=period).mean()
        std = df['Close'].rolling(window=period).std()

        df['BB_Upper'] = df['BB_Middle'] + (std * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (std * std_dev)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']

        return df

    @staticmethod
    def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add volume-based indicators

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with volume indicators added
        """
        # Volume Moving Average
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()

        # On-Balance Volume (OBV)
        obv = [0]
        for i in range(1, len(df)):
            if df['Close'].iloc[i] > df['Close'].iloc[i - 1]:
                obv.append(obv[-1] + df['Volume'].iloc[i])
            elif df['Close'].iloc[i] < df['Close'].iloc[i - 1]:
                obv.append(obv[-1] - df['Volume'].iloc[i])
            else:
                obv.append(obv[-1])

        df['OBV'] = obv

        return df

    @staticmethod
    def add_all_indicators(
        df: pd.DataFrame,
        config: Dict = None
    ) -> pd.DataFrame:
        """
        Add all technical indicators to the dataframe

        Args:
            df: DataFrame with OHLCV data
            config: Configuration dictionary with indicator parameters

        Returns:
            DataFrame with all indicators added
        """
        if config is None:
            config = {
                'ma_periods': [20, 50, 200],
                'ema_periods': [12, 26, 50],
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'stochastic_k': 14,
                'stochastic_d': 3,
                'atr_period': 14,
                'bollinger_period': 20,
                'bollinger_std': 2
            }

        df = TechnicalIndicators.add_moving_averages(df, config['ma_periods'])
        df = TechnicalIndicators.add_exponential_moving_averages(df, config['ema_periods'])
        df = TechnicalIndicators.add_rsi(df, config['rsi_period'])
        df = TechnicalIndicators.add_macd(
            df,
            config['macd_fast'],
            config['macd_slow'],
            config['macd_signal']
        )
        df = TechnicalIndicators.add_stochastic(
            df,
            config['stochastic_k'],
            config['stochastic_d']
        )
        df = TechnicalIndicators.add_atr(df, config['atr_period'])
        df = TechnicalIndicators.add_bollinger_bands(
            df,
            config['bollinger_period'],
            config['bollinger_std']
        )
        df = TechnicalIndicators.add_volume_indicators(df)

        return df


class SignalGenerator:
    """Generate trading signals from technical indicators"""

    @staticmethod
    def ma_crossover_signal(df: pd.DataFrame, fast_period: int = 20, slow_period: int = 50) -> str:
        """
        Generate signal based on MA crossover AND current position

        Args:
            df: DataFrame with MA indicators
            fast_period: Fast MA period
            slow_period: Slow MA period

        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if len(df) < 2:
            return 'HOLD'

        fast_col = f'MA_{fast_period}'
        slow_col = f'MA_{slow_period}'

        if fast_col not in df.columns or slow_col not in df.columns:
            return 'HOLD'

        # Current and previous values
        fast_current = df[fast_col].iloc[-1]
        fast_prev = df[fast_col].iloc[-2]
        slow_current = df[slow_col].iloc[-1]
        slow_prev = df[slow_col].iloc[-2]
        price_current = df['Close'].iloc[-1]

        # Check for crossover (strong signal)
        if fast_prev <= slow_prev and fast_current > slow_current:
            return 'BUY'
        elif fast_prev >= slow_prev and fast_current < slow_current:
            return 'SELL'

        # Check current position (weaker signal)
        if fast_current > slow_current and price_current > fast_current:
            # Fast MA above slow MA and price above fast MA = bullish trend
            return 'BUY'
        elif fast_current < slow_current and price_current < fast_current:
            # Fast MA below slow MA and price below fast MA = bearish trend
            return 'SELL'

        return 'HOLD'

    @staticmethod
    def ema_crossover_signal(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26) -> str:
        """
        Generate signal based on EMA crossover AND current position

        Args:
            df: DataFrame with EMA indicators
            fast_period: Fast EMA period
            slow_period: Slow EMA period

        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if len(df) < 2:
            return 'HOLD'

        fast_col = f'EMA_{fast_period}'
        slow_col = f'EMA_{slow_period}'

        if fast_col not in df.columns or slow_col not in df.columns:
            return 'HOLD'

        # Current and previous values
        fast_current = df[fast_col].iloc[-1]
        fast_prev = df[fast_col].iloc[-2]
        slow_current = df[slow_col].iloc[-1]
        slow_prev = df[slow_col].iloc[-2]
        price_current = df['Close'].iloc[-1]

        # Check for crossover (strong signal)
        if fast_prev <= slow_prev and fast_current > slow_current:
            return 'BUY'
        elif fast_prev >= slow_prev and fast_current < slow_current:
            return 'SELL'

        # Check current position (weaker signal)
        if fast_current > slow_current and price_current > fast_current:
            # Fast EMA above slow EMA and price above fast EMA = bullish trend
            return 'BUY'
        elif fast_current < slow_current and price_current < fast_current:
            # Fast EMA below slow EMA and price below fast EMA = bearish trend
            return 'SELL'

        return 'HOLD'

    @staticmethod
    def rsi_signal(df: pd.DataFrame, overbought: int = 70, oversold: int = 30) -> str:
        """
        Generate signal based on RSI

        Args:
            df: DataFrame with RSI
            overbought: Overbought threshold
            oversold: Oversold threshold

        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if 'RSI' not in df.columns or len(df) < 2:
            return 'HOLD'

        rsi_current = df['RSI'].iloc[-1]
        rsi_prev = df['RSI'].iloc[-2]

        # Strong signals: crossing thresholds
        # Oversold to normal (bullish)
        if rsi_prev < oversold and rsi_current >= oversold:
            return 'BUY'
        # Overbought to normal (bearish)
        elif rsi_prev > overbought and rsi_current <= overbought:
            return 'SELL'

        # Moderate signals: current position with momentum
        # In oversold zone and rising
        if rsi_current < oversold and rsi_current > rsi_prev:
            return 'BUY'
        # In overbought zone and falling
        elif rsi_current > overbought and rsi_current < rsi_prev:
            return 'SELL'

        # Weaker signals: neutral zone with strong momentum
        # RSI rising in lower half (potential uptrend)
        elif rsi_current < 50 and rsi_current > rsi_prev + 2:
            return 'BUY'
        # RSI falling in upper half (potential downtrend)
        elif rsi_current > 50 and rsi_current < rsi_prev - 2:
            return 'SELL'

        return 'HOLD'

    @staticmethod
    def macd_signal(df: pd.DataFrame) -> str:
        """
        Generate signal based on MACD crossover

        Args:
            df: DataFrame with MACD indicators

        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if 'MACD' not in df.columns or len(df) < 2:
            return 'HOLD'

        macd_current = df['MACD'].iloc[-1]
        macd_prev = df['MACD'].iloc[-2]
        signal_current = df['MACD_Signal'].iloc[-1]
        signal_prev = df['MACD_Signal'].iloc[-2]
        hist_current = df['MACD_Hist'].iloc[-1]
        hist_prev = df['MACD_Hist'].iloc[-2]

        # Strong signals: crossovers
        # Bullish crossover
        if macd_prev <= signal_prev and macd_current > signal_current:
            return 'BUY'
        # Bearish crossover
        elif macd_prev >= signal_prev and macd_current < signal_current:
            return 'SELL'

        # Moderate signals: current position with strengthening histogram
        # MACD above signal and histogram increasing
        if macd_current > signal_current and hist_current > hist_prev:
            return 'BUY'
        # MACD below signal and histogram decreasing (more negative)
        elif macd_current < signal_current and hist_current < hist_prev:
            return 'SELL'

        return 'HOLD'

    @staticmethod
    def stochastic_signal(df: pd.DataFrame, overbought: int = 80, oversold: int = 20) -> str:
        """
        Generate signal based on Stochastic Oscillator

        Args:
            df: DataFrame with Stochastic indicators
            overbought: Overbought threshold
            oversold: Oversold threshold

        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if 'Stoch_K' not in df.columns or len(df) < 2:
            return 'HOLD'

        k_current = df['Stoch_K'].iloc[-1]
        d_current = df['Stoch_D'].iloc[-1]
        k_prev = df['Stoch_K'].iloc[-2]
        d_prev = df['Stoch_D'].iloc[-2]

        # Strong signals: K crosses D in extreme zones
        # Bullish: K crosses above D in oversold zone
        if k_prev <= d_prev and k_current > d_current and k_current < oversold:
            return 'BUY'
        # Bearish: K crosses below D in overbought zone
        elif k_prev >= d_prev and k_current < d_current and k_current > overbought:
            return 'SELL'

        # Moderate signals: In extreme zones
        # In oversold zone and K above D (bullish setup)
        if k_current < oversold and k_current > d_current:
            return 'BUY'
        # In overbought zone and K below D (bearish setup)
        elif k_current > overbought and k_current < d_current:
            return 'SELL'

        # Weaker signals: General position
        # K above D and both rising from lower levels
        if k_current > d_current and k_current > k_prev and k_current < 50:
            return 'BUY'
        # K below D and both falling from upper levels
        elif k_current < d_current and k_current < k_prev and k_current > 50:
            return 'SELL'

        return 'HOLD'

    @staticmethod
    def generate_all_signals(df: pd.DataFrame, config: Dict = None) -> Dict[str, str]:
        """
        Generate all technical indicator signals

        Args:
            df: DataFrame with all indicators
            config: Configuration dictionary

        Returns:
            Dictionary of signal types and their values
        """
        if config is None:
            config = {
                'rsi_overbought': 70,
                'rsi_oversold': 30
            }

        signals = {
            'ma_cross': SignalGenerator.ma_crossover_signal(df, 20, 50),
            'ema_cross': SignalGenerator.ema_crossover_signal(df, 12, 26),
            'rsi': SignalGenerator.rsi_signal(df, config['rsi_overbought'], config['rsi_oversold']),
            'macd': SignalGenerator.macd_signal(df),
            'stochastic': SignalGenerator.stochastic_signal(df)
        }

        return signals
