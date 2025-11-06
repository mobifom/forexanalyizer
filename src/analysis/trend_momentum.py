"""
Trend Momentum and Reversal Detection Module
Analyzes historical candles to detect trend strength and potential reversals
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class TrendMomentumAnalyzer:
    """
    Analyzes trend momentum by considering historical candles
    Detects strong trends and sudden reversals
    """

    @staticmethod
    def calculate_trend_momentum(df: pd.DataFrame, lookback: int = 20) -> Dict:
        """
        Calculate trend momentum over historical candles

        Args:
            df: DataFrame with OHLCV data
            lookback: Number of candles to analyze

        Returns:
            Dictionary with momentum metrics
        """
        if len(df) < lookback:
            return {
                'direction': 'NEUTRAL',
                'strength': 0.0,
                'consistency': 0.0,
                'momentum_score': 0.0
            }

        # Get recent candles
        recent_df = df.iloc[-lookback:]

        # 1. Calculate directional movement
        bullish_candles = (recent_df['Close'] > recent_df['Open']).sum()
        bearish_candles = (recent_df['Close'] < recent_df['Open']).sum()

        # 2. Calculate price momentum
        price_change = (recent_df['Close'].iloc[-1] - recent_df['Close'].iloc[0]) / recent_df['Close'].iloc[0]
        price_momentum = price_change * 100  # As percentage

        # 3. Calculate momentum consistency (are candles mostly in same direction?)
        total_candles = len(recent_df)
        consistency = max(bullish_candles, bearish_candles) / total_candles

        # 4. Calculate higher highs / lower lows pattern
        highs = recent_df['High'].values
        lows = recent_df['Low'].values

        higher_highs = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
        lower_lows = sum(1 for i in range(1, len(lows)) if lows[i] < lows[i-1])

        # 5. Calculate volume-weighted momentum (if volume available)
        if 'Volume' in recent_df.columns:
            volume_trend = recent_df['Volume'].iloc[-5:].mean() / recent_df['Volume'].iloc[:5].mean()
        else:
            volume_trend = 1.0

        # Determine direction and strength
        if bullish_candles > bearish_candles * 1.5:  # Strong bullish bias
            direction = 'BULLISH'
            strength = (bullish_candles / total_candles)
        elif bearish_candles > bullish_candles * 1.5:  # Strong bearish bias
            direction = 'BEARISH'
            strength = (bearish_candles / total_candles)
        else:
            direction = 'NEUTRAL'
            strength = 0.5

        # Calculate overall momentum score (0-1)
        momentum_score = (
            consistency * 0.3 +  # 30% weight on consistency
            abs(price_momentum) / 10 * 0.3 +  # 30% weight on price change
            strength * 0.2 +  # 20% weight on candle direction
            (higher_highs if direction == 'BULLISH' else lower_lows) / (total_candles - 1) * 0.2  # 20% on pattern
        )
        momentum_score = min(momentum_score, 1.0)  # Cap at 1.0

        return {
            'direction': direction,
            'strength': strength,
            'consistency': consistency,
            'momentum_score': momentum_score,
            'price_change_pct': price_momentum,
            'bullish_candles': bullish_candles,
            'bearish_candles': bearish_candles,
            'higher_highs': higher_highs,
            'lower_lows': lower_lows,
            'volume_trend': volume_trend
        }

    @staticmethod
    def detect_reversal(df: pd.DataFrame, recent_lookback: int = 5, historical_lookback: int = 20) -> Dict:
        """
        Detect if there's a potential reversal from a strong trend

        Args:
            df: DataFrame with OHLCV data
            recent_lookback: Recent candles to check for reversal (default 5)
            historical_lookback: Historical candles to establish trend (default 20)

        Returns:
            Dictionary with reversal detection info
        """
        if len(df) < historical_lookback + recent_lookback:
            return {
                'is_reversal': False,
                'reversal_strength': 0.0,
                'reversal_type': 'NONE',
                'previous_trend': 'NEUTRAL',
                'warning_level': 'LOW'
            }

        # Analyze historical trend (excluding recent candles)
        historical_df = df.iloc[-(historical_lookback + recent_lookback):-recent_lookback]
        historical_momentum = TrendMomentumAnalyzer.calculate_trend_momentum(historical_df, historical_lookback)

        # Analyze recent candles
        recent_df = df.iloc[-recent_lookback:]
        recent_momentum = TrendMomentumAnalyzer.calculate_trend_momentum(recent_df, recent_lookback)

        # Detect reversal: strong historical trend + opposite recent movement
        is_reversal = False
        reversal_strength = 0.0
        reversal_type = 'NONE'
        warning_level = 'LOW'

        # Check if historical trend was strong
        if historical_momentum['momentum_score'] > 0.6:  # Strong trend threshold

            # Check if recent candles show opposite direction
            if historical_momentum['direction'] == 'BULLISH' and recent_momentum['direction'] == 'BEARISH':
                # Bullish to Bearish reversal
                is_reversal = True
                reversal_type = 'BULLISH_TO_BEARISH'
                reversal_strength = recent_momentum['consistency']

                # Warning level based on how sudden the reversal is
                if recent_momentum['consistency'] > 0.7:
                    warning_level = 'HIGH'  # Very sudden reversal
                elif recent_momentum['consistency'] > 0.5:
                    warning_level = 'MEDIUM'
                else:
                    warning_level = 'LOW'

            elif historical_momentum['direction'] == 'BEARISH' and recent_momentum['direction'] == 'BULLISH':
                # Bearish to Bullish reversal
                is_reversal = True
                reversal_type = 'BEARISH_TO_BULLISH'
                reversal_strength = recent_momentum['consistency']

                if recent_momentum['consistency'] > 0.7:
                    warning_level = 'HIGH'
                elif recent_momentum['consistency'] > 0.5:
                    warning_level = 'MEDIUM'
                else:
                    warning_level = 'LOW'

        return {
            'is_reversal': is_reversal,
            'reversal_strength': reversal_strength,
            'reversal_type': reversal_type,
            'previous_trend': historical_momentum['direction'],
            'previous_trend_strength': historical_momentum['momentum_score'],
            'recent_trend': recent_momentum['direction'],
            'recent_trend_strength': recent_momentum['momentum_score'],
            'warning_level': warning_level,
            'historical_momentum': historical_momentum,
            'recent_momentum': recent_momentum
        }

    @staticmethod
    def calculate_weighted_signal(
        current_signal: str,
        momentum: Dict,
        reversal: Dict,
        current_weight: float = 0.4,
        momentum_weight: float = 0.4,
        reversal_weight: float = 0.2
    ) -> Tuple[str, float, str]:
        """
        Calculate weighted signal considering:
        - Current candle signal (latest indicators)
        - Historical momentum
        - Reversal detection

        Args:
            current_signal: Signal from current candle ('BUY', 'SELL', 'HOLD')
            momentum: Momentum analysis dict
            reversal: Reversal detection dict
            current_weight: Weight for current signal (default 0.4)
            momentum_weight: Weight for momentum (default 0.4)
            reversal_weight: Weight for reversal detection (default 0.2)

        Returns:
            Tuple of (final_signal, confidence, reasoning)
        """
        # Convert signals to numeric scores (-1 to +1)
        signal_scores = {'BUY': 1.0, 'SELL': -1.0, 'HOLD': 0.0}

        # 1. Current signal score
        current_score = signal_scores.get(current_signal, 0.0)

        # 2. Momentum score
        momentum_direction = momentum.get('direction', 'NEUTRAL')
        momentum_strength = momentum.get('momentum_score', 0.5)

        if momentum_direction == 'BULLISH':
            momentum_score = momentum_strength
        elif momentum_direction == 'BEARISH':
            momentum_score = -momentum_strength
        else:
            momentum_score = 0.0

        # 3. Reversal adjustment
        reversal_score = 0.0
        reversal_reasoning = ""

        if reversal.get('is_reversal', False):
            reversal_type = reversal.get('reversal_type')
            reversal_strength = reversal.get('reversal_strength', 0.0)
            warning_level = reversal.get('warning_level', 'LOW')

            if reversal_type == 'BULLISH_TO_BEARISH':
                # Was bullish, now turning bearish
                reversal_score = -reversal_strength
                reversal_reasoning = f"⚠️ REVERSAL DETECTED: Strong bullish trend reversing to bearish ({warning_level} confidence)"

            elif reversal_type == 'BEARISH_TO_BULLISH':
                # Was bearish, now turning bullish
                reversal_score = reversal_strength
                reversal_reasoning = f"⚠️ REVERSAL DETECTED: Strong bearish trend reversing to bullish ({warning_level} confidence)"

        # Calculate weighted final score
        final_score = (
            current_score * current_weight +
            momentum_score * momentum_weight +
            reversal_score * reversal_weight
        )

        # Determine final signal
        if final_score > 0.3:
            final_signal = 'BUY'
        elif final_score < -0.3:
            final_signal = 'SELL'
        else:
            final_signal = 'HOLD'

        # Calculate confidence (0-1)
        confidence = min(abs(final_score), 1.0)

        # Build reasoning
        reasoning_parts = []

        if current_signal != 'HOLD':
            reasoning_parts.append(f"Current indicators suggest {current_signal}")

        if momentum_direction != 'NEUTRAL':
            reasoning_parts.append(
                f"Historical momentum is {momentum_direction} (strength: {momentum_strength:.1%})"
            )

        if reversal_reasoning:
            reasoning_parts.append(reversal_reasoning)

        if not reasoning_parts:
            reasoning_parts.append("No clear signal - market is neutral")

        reasoning = " | ".join(reasoning_parts)

        return final_signal, confidence, reasoning

    @staticmethod
    def get_enhanced_analysis(df: pd.DataFrame, current_signal: str) -> Dict:
        """
        Get complete enhanced analysis with momentum and reversal detection

        Args:
            df: DataFrame with OHLCV data
            current_signal: Current signal from indicators

        Returns:
            Dictionary with complete analysis
        """
        # Calculate momentum
        momentum = TrendMomentumAnalyzer.calculate_trend_momentum(df, lookback=20)

        # Detect reversals
        reversal = TrendMomentumAnalyzer.detect_reversal(df, recent_lookback=5, historical_lookback=20)

        # Calculate weighted signal
        final_signal, confidence, reasoning = TrendMomentumAnalyzer.calculate_weighted_signal(
            current_signal, momentum, reversal
        )

        return {
            'original_signal': current_signal,
            'final_signal': final_signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'momentum': momentum,
            'reversal': reversal,
            'signal_changed': current_signal != final_signal
        }
