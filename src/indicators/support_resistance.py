"""
Support and Resistance Level Detection
Uses pivot points and price action to identify key levels
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class SupportResistance:
    """Detect support and resistance levels"""

    @staticmethod
    def find_pivot_points(df: pd.DataFrame, window: int = 5) -> Tuple[List[float], List[float]]:
        """
        Find pivot highs and lows

        Args:
            df: DataFrame with OHLCV data
            window: Window size for pivot detection

        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        support_levels = []
        resistance_levels = []

        for i in range(window, len(df) - window):
            # Check for pivot high (resistance)
            if df['High'].iloc[i] == df['High'].iloc[i - window:i + window + 1].max():
                resistance_levels.append(df['High'].iloc[i])

            # Check for pivot low (support)
            if df['Low'].iloc[i] == df['Low'].iloc[i - window:i + window + 1].min():
                support_levels.append(df['Low'].iloc[i])

        return support_levels, resistance_levels

    @staticmethod
    def cluster_levels(levels: List[float], tolerance: float = 0.001) -> List[float]:
        """
        Cluster nearby levels together

        Args:
            levels: List of price levels
            tolerance: Percentage tolerance for clustering (0.001 = 0.1%)

        Returns:
            List of clustered levels
        """
        if not levels:
            return []

        sorted_levels = sorted(levels)
        clusters = []
        current_cluster = [sorted_levels[0]]

        for level in sorted_levels[1:]:
            # If level is within tolerance of cluster, add to cluster
            if abs(level - np.mean(current_cluster)) / np.mean(current_cluster) <= tolerance:
                current_cluster.append(level)
            else:
                # Start new cluster
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]

        # Add last cluster
        clusters.append(np.mean(current_cluster))

        return clusters

    @staticmethod
    def get_key_levels(
        df: pd.DataFrame,
        num_levels: int = 3,
        window: int = 5,
        tolerance: float = 0.001
    ) -> Dict[str, List[float]]:
        """
        Get the most important support and resistance levels

        Args:
            df: DataFrame with OHLCV data
            num_levels: Number of key levels to return
            window: Window for pivot detection
            tolerance: Clustering tolerance

        Returns:
            Dictionary with 'support' and 'resistance' lists
        """
        support, resistance = SupportResistance.find_pivot_points(df, window)

        # Cluster the levels
        support_clustered = SupportResistance.cluster_levels(support, tolerance)
        resistance_clustered = SupportResistance.cluster_levels(resistance, tolerance)

        # Get current price
        current_price = df['Close'].iloc[-1]

        # Filter and sort levels
        # Support levels below current price
        support_below = [s for s in support_clustered if s < current_price]
        support_below = sorted(support_below, reverse=True)[:num_levels]

        # Resistance levels above current price
        resistance_above = [r for r in resistance_clustered if r > current_price]
        resistance_above = sorted(resistance_above)[:num_levels]

        return {
            'support': support_below,
            'resistance': resistance_above
        }

    @staticmethod
    def check_level_proximity(
        price: float,
        levels: List[float],
        tolerance: float = 0.002
    ) -> Tuple[bool, str, float]:
        """
        Check if price is near a support or resistance level

        Args:
            price: Current price
            levels: List of S/R levels
            tolerance: How close to consider "near" (0.002 = 0.2%)

        Returns:
            Tuple of (is_near, level_type, nearest_level)
        """
        if not levels:
            return False, None, None

        for level in levels:
            if abs(price - level) / level <= tolerance:
                level_type = 'support' if price > level else 'resistance'
                return True, level_type, level

        return False, None, None

    @staticmethod
    def add_sr_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add support/resistance indicators to dataframe

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with S/R columns added
        """
        levels = SupportResistance.get_key_levels(df)

        # Add distance to nearest support and resistance
        current_price = df['Close'].iloc[-1]

        if levels['support']:
            df['Nearest_Support'] = levels['support'][0]
            df['Support_Distance'] = (current_price - levels['support'][0]) / current_price
        else:
            df['Nearest_Support'] = np.nan
            df['Support_Distance'] = np.nan

        if levels['resistance']:
            df['Nearest_Resistance'] = levels['resistance'][0]
            df['Resistance_Distance'] = (levels['resistance'][0] - current_price) / current_price
        else:
            df['Nearest_Resistance'] = np.nan
            df['Resistance_Distance'] = np.nan

        return df

    @staticmethod
    def get_sr_signal(df: pd.DataFrame, tolerance: float = 0.002) -> str:
        """
        Generate signal based on support/resistance levels

        Args:
            df: DataFrame with OHLCV data
            tolerance: Proximity tolerance

        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        levels = SupportResistance.get_key_levels(df)
        current_price = df['Close'].iloc[-1]

        # Check if near support (potential buy)
        if levels['support']:
            for support in levels['support']:
                if abs(current_price - support) / support <= tolerance:
                    # Near support = potential bounce = BUY
                    return 'BUY'

        # Check if near resistance (potential sell)
        if levels['resistance']:
            for resistance in levels['resistance']:
                if abs(current_price - resistance) / resistance <= tolerance:
                    # Near resistance = potential rejection = SELL
                    return 'SELL'

        return 'HOLD'
