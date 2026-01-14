"""
Multi-Timeframe Analysis Module
Analyzes forex signals across multiple timeframes
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

from ..indicators.technical_indicators import TechnicalIndicators, SignalGenerator
from ..indicators.support_resistance import SupportResistance
from .enhanced_recommendations import EnhancedRecommendations
from .trend_momentum import TrendMomentumAnalyzer

logger = logging.getLogger(__name__)


class MultiTimeframeAnalyzer:
    """Analyze forex signals across multiple timeframes"""

    def __init__(self, config: Dict):
        """
        Initialize multi-timeframe analyzer

        Args:
            config: Configuration dictionary with indicator settings
        """
        self.config = config
        self.indicator_config = config.get('indicators', {})

    def analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """
        Analyze a single timeframe

        Args:
            df: DataFrame with OHLCV data
            timeframe: Timeframe identifier (e.g., '1d', '4h')

        Returns:
            Dictionary with analysis results
        """
        if df is None or len(df) < 50:
            logger.warning(f"Insufficient data for {timeframe}")
            return None

        try:
            # Add all technical indicators
            df = TechnicalIndicators.add_all_indicators(df, self.indicator_config)

            # Add support/resistance
            df = SupportResistance.add_sr_indicators(df)

            # Generate signals
            signals = SignalGenerator.generate_all_signals(df, self.indicator_config)

            # Add S/R signal
            signals['support_resistance'] = SupportResistance.get_sr_signal(df)

            # Calculate trend strength
            trend_strength = self._calculate_trend_strength(df)

            # Calculate momentum
            momentum = self._calculate_momentum(df)

            # Get current values
            current_data = {
                'price': df['Close'].iloc[-1],
                'rsi': df['RSI'].iloc[-1] if 'RSI' in df.columns else None,
                'macd': df['MACD'].iloc[-1] if 'MACD' in df.columns else None,
                'atr': df['ATR'].iloc[-1] if 'ATR' in df.columns else None,
                'volume': df['Volume'].iloc[-1],
            }

            # Get support/resistance levels
            sr_levels = SupportResistance.get_key_levels(df)

            # Generate enhanced recommendations (ForexApp_V2 style)
            enhanced_rec = EnhancedRecommendations.generate_enhanced_recommendation(
                df, signals, timeframe
            )

            # NEW: Calculate trend momentum from historical candles
            trend_momentum = TrendMomentumAnalyzer.calculate_trend_momentum(df, lookback=20)

            # NEW: Detect potential reversals
            reversal_detection = TrendMomentumAnalyzer.detect_reversal(
                df, recent_lookback=5, historical_lookback=20
            )

            # Get current consensus signal from indicators
            tf_signals = list(signals.values())
            tf_buy = tf_signals.count('BUY')
            tf_sell = tf_signals.count('SELL')

            if tf_buy > tf_sell:
                current_consensus = 'BUY'
            elif tf_sell > tf_buy:
                current_consensus = 'SELL'
            else:
                current_consensus = 'HOLD'

            # NEW: Get enhanced signal with momentum and reversal consideration
            enhanced_signal_analysis = TrendMomentumAnalyzer.get_enhanced_analysis(
                df, current_consensus
            )

            return {
                'timeframe': timeframe,
                'signals': signals,
                'current_consensus': current_consensus,  # Original consensus
                'enhanced_signal': enhanced_signal_analysis['final_signal'],  # NEW: Enhanced signal
                'signal_confidence': enhanced_signal_analysis['confidence'],  # NEW: Confidence level
                'signal_reasoning': enhanced_signal_analysis['reasoning'],  # NEW: Why this signal
                'trend_strength': trend_strength,
                'momentum': momentum,
                'trend_momentum': trend_momentum,  # NEW: Historical momentum analysis
                'reversal_detection': reversal_detection,  # NEW: Reversal detection
                'current_data': current_data,
                'support_levels': sr_levels['support'],
                'resistance_levels': sr_levels['resistance'],
                'dataframe': df,
                'enhanced_recommendation': enhanced_rec,
                'signal_changed': enhanced_signal_analysis['signal_changed']  # NEW: Did signal change?
            }

        except Exception as e:
            logger.error(f"Error analyzing {timeframe}: {e}")
            return None

    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """
        Calculate trend strength from 0 (no trend) to 1 (strong trend)

        Args:
            df: DataFrame with indicators

        Returns:
            Trend strength score
        """
        scores = []

        # MA alignment
        if all(col in df.columns for col in ['MA_20', 'MA_50', 'MA_200']):
            ma20 = df['MA_20'].iloc[-1]
            ma50 = df['MA_50'].iloc[-1]
            ma200 = df['MA_200'].iloc[-1]

            # Bullish alignment
            if ma20 > ma50 > ma200:
                scores.append(1.0)
            # Bearish alignment
            elif ma20 < ma50 < ma200:
                scores.append(1.0)
            else:
                scores.append(0.3)

        # ADX would be ideal here, but we'll use price momentum
        if len(df) >= 20:
            price_change = (df['Close'].iloc[-1] - df['Close'].iloc[-20]) / df['Close'].iloc[-20]
            momentum_score = min(abs(price_change) * 10, 1.0)  # Scale to 0-1
            scores.append(momentum_score)

        return np.mean(scores) if scores else 0.5

    def _calculate_momentum(self, df: pd.DataFrame) -> str:
        """
        Calculate overall momentum direction

        Args:
            df: DataFrame with indicators

        Returns:
            'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        bullish_count = 0
        bearish_count = 0

        # Check RSI
        if 'RSI' in df.columns:
            rsi = df['RSI'].iloc[-1]
            if rsi > 50:
                bullish_count += 1
            elif rsi < 50:
                bearish_count += 1

        # Check MACD
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1]:
                bullish_count += 1
            else:
                bearish_count += 1

        # Check price vs MA
        if 'MA_50' in df.columns:
            if df['Close'].iloc[-1] > df['MA_50'].iloc[-1]:
                bullish_count += 1
            else:
                bearish_count += 1

        if bullish_count > bearish_count:
            return 'BULLISH'
        elif bearish_count > bullish_count:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def analyze_multiple_timeframes(
        self,
        data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, Dict]:
        """
        Analyze multiple timeframes

        Args:
            data_dict: Dictionary mapping timeframe to DataFrame

        Returns:
            Dictionary mapping timeframe to analysis results
        """
        results = {}

        for timeframe, df in data_dict.items():
            logger.info(f"Analyzing {timeframe}")
            analysis = self.analyze_timeframe(df, timeframe)
            if analysis:
                results[timeframe] = analysis

        return results

    def _apply_signal_controls(self, analyses: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Apply enhanced signal controls to filter and adjust signals

        Args:
            analyses: Dictionary of timeframe analyses

        Returns:
            Filtered and adjusted analyses
        """
        signal_control = self.config.get('signal_control', {})

        # Get control settings
        min_conf_by_tf = signal_control.get('min_confidence_by_timeframe', {})
        require_higher_tf = signal_control.get('require_higher_tf_confirmation', True)
        confirmation_rules = signal_control.get('confirmation_rules', {})
        momentum_settings = signal_control.get('momentum', {})
        reversal_settings = signal_control.get('reversal', {})
        strength_settings = signal_control.get('strength', {})

        filtered_analyses = {}

        for tf, analysis in analyses.items():
            if not analysis:
                continue

            # Make a copy to modify
            filtered_analysis = analysis.copy()

            # 1. Check minimum confidence threshold for this timeframe
            min_confidence = min_conf_by_tf.get(tf, 0.5)
            current_confidence = analysis.get('signal_confidence', 0.5)

            if current_confidence < min_confidence:
                logger.info(f"{tf}: Signal confidence {current_confidence:.2f} below threshold {min_confidence:.2f}, setting to HOLD")
                filtered_analysis['enhanced_signal'] = 'HOLD'
                filtered_analysis['signal_confidence'] = current_confidence
                filtered_analysis['filtered_reason'] = f'Below {tf} confidence threshold'

            # 2. Check minimum indicators agreement
            min_indicators = strength_settings.get('min_indicators_agree', 3)
            signals = analysis.get('signals', {})
            signal_counts = {
                'BUY': sum(1 for s in signals.values() if s == 'BUY'),
                'SELL': sum(1 for s in signals.values() if s == 'SELL'),
                'HOLD': sum(1 for s in signals.values() if s == 'HOLD')
            }

            current_signal = filtered_analysis.get('enhanced_signal', 'HOLD')
            if current_signal != 'HOLD' and signal_counts.get(current_signal, 0) < min_indicators:
                logger.info(f"{tf}: Only {signal_counts.get(current_signal, 0)} indicators agree, need {min_indicators}, setting to HOLD")
                filtered_analysis['enhanced_signal'] = 'HOLD'
                filtered_analysis['filtered_reason'] = f'Insufficient indicator agreement'

            # 3. Check momentum filter
            if momentum_settings.get('enable_momentum_filter', True):
                min_momentum = momentum_settings.get('min_momentum_strength', 0.5)
                trend_momentum = analysis.get('trend_momentum', {})
                momentum_score = trend_momentum.get('momentum_score', 0.5)

                if momentum_score < min_momentum and current_signal != 'HOLD':
                    logger.info(f"{tf}: Momentum {momentum_score:.2f} below threshold {min_momentum:.2f}")
                    filtered_analysis['signal_confidence'] *= 0.7  # Reduce confidence

            # 4. Apply reversal detection downgrade/block
            if reversal_settings.get('enable_reversal_detection', True):
                reversal_action = reversal_settings.get('reversal_warning_action', 'downgrade')
                reversal = analysis.get('reversal_detection', {})

                if reversal.get('is_reversal', False):
                    if reversal_action == 'block':
                        logger.info(f"{tf}: Reversal detected, blocking signal")
                        filtered_analysis['enhanced_signal'] = 'HOLD'
                        filtered_analysis['filtered_reason'] = 'Reversal detected'
                    elif reversal_action == 'downgrade':
                        downgrade_factor = reversal_settings.get('downgrade_factor', 0.5)
                        filtered_analysis['signal_confidence'] *= downgrade_factor
                        logger.info(f"{tf}: Reversal detected, confidence downgraded by {downgrade_factor}")

            filtered_analyses[tf] = filtered_analysis

        # 5. Apply higher timeframe confirmation requirements
        if require_higher_tf:
            for tf, analysis in list(filtered_analyses.items()):
                rule_key = f'{tf}_requires'
                required_tfs = confirmation_rules.get(rule_key, [])

                if not required_tfs:
                    continue  # No confirmation needed

                current_signal = analysis.get('enhanced_signal', 'HOLD')
                if current_signal == 'HOLD':
                    continue  # No need to check if already HOLD

                # Check if at least one required timeframe confirms
                confirmed = False
                for req_tf in required_tfs:
                    if req_tf in filtered_analyses:
                        req_signal = filtered_analyses[req_tf].get('enhanced_signal', 'HOLD')
                        # Consider both exact match or at least not opposite
                        if req_signal == current_signal:
                            confirmed = True
                            break
                        elif req_signal == 'HOLD':
                            # HOLD is neutral, can be partial confirmation
                            confirmed = True  # Allow if not opposite
                            break

                if not confirmed:
                    logger.info(f"{tf}: {current_signal} signal not confirmed by required timeframes {required_tfs}, setting to HOLD")
                    filtered_analyses[tf]['enhanced_signal'] = 'HOLD'
                    filtered_analyses[tf]['filtered_reason'] = f'No confirmation from {required_tfs}'

        return filtered_analyses

    def get_timeframe_consensus(self, analyses: Dict[str, Dict]) -> Dict:
        """
        Get consensus across all timeframes with enhanced controls

        Args:
            analyses: Dictionary of timeframe analyses

        Returns:
            Dictionary with consensus information
        """
        if not analyses:
            return {
                'consensus': 'HOLD',
                'agreement_count': 0,
                'total_timeframes': 0,
                'confidence': 0.0
            }

        # Apply enhanced signal controls
        filtered_analyses = self._apply_signal_controls(analyses)

        # Count signals across all timeframes
        buy_count = 0
        sell_count = 0
        hold_count = 0

        # Weight signals by timeframe importance
        timeframe_weights = self.config.get('timeframe_weights', {
            '1d': 0.4,
            '4h': 0.3,
            '1h': 0.2,
            '15m': 0.1
        })

        weighted_buy = 0.0
        weighted_sell = 0.0

        # Track timeframes with reversals for additional context
        reversals_detected = []
        filtered_reasons = {}

        for tf, analysis in filtered_analyses.items():
            weight = timeframe_weights.get(tf, 0.1)

            # Use enhanced signal with applied controls
            enhanced_signal = analysis.get('enhanced_signal', 'HOLD')
            signal_confidence = analysis.get('signal_confidence', 0.5)

            # Track filtering reasons
            if 'filtered_reason' in analysis:
                filtered_reasons[tf] = analysis['filtered_reason']

            # Apply confidence weighting (stronger signals get more weight)
            confidence_weight = weight * signal_confidence

            # Check for reversal warnings
            if analysis.get('reversal_detection', {}).get('is_reversal', False):
                reversals_detected.append({
                    'timeframe': tf,
                    'type': analysis['reversal_detection']['reversal_type'],
                    'strength': analysis['reversal_detection']['reversal_strength'],
                    'warning_level': analysis['reversal_detection']['warning_level']
                })

            if enhanced_signal == 'BUY':
                buy_count += 1
                weighted_buy += confidence_weight
            elif enhanced_signal == 'SELL':
                sell_count += 1
                weighted_sell += confidence_weight
            else:
                hold_count += 1

        # Determine consensus with conflict resolution
        total_timeframes = len(filtered_analyses)
        signal_control = self.config.get('signal_control', {})
        conflict_mode = signal_control.get('conflict_resolution', {}).get('mode', 'weighted_priority')
        min_timeframes_agree = self.config.get('confluence', {}).get('min_timeframes_agree', 2)
        min_confidence = self.config.get('confluence', {}).get('min_confidence', 0.5)

        if conflict_mode == 'conservative':
            # Conservative: require clear majority
            if buy_count > sell_count + 1 and buy_count >= min_timeframes_agree and weighted_buy >= min_confidence:
                consensus = 'BUY'
                agreement_count = buy_count
                confidence = weighted_buy
            elif sell_count > buy_count + 1 and sell_count >= min_timeframes_agree and weighted_sell >= min_confidence:
                consensus = 'SELL'
                agreement_count = sell_count
                confidence = weighted_sell
            else:
                consensus = 'HOLD'
                agreement_count = hold_count
                confidence = 0.5

        elif conflict_mode == 'higher_tf_wins':
            # Higher timeframe wins: check 1d first, then 4h, then 1h, then 15m
            consensus = 'HOLD'
            confidence = 0.5
            agreement_count = hold_count
            for tf in ['1d', '4h', '1h', '15m']:
                if tf in filtered_analyses:
                    signal = filtered_analyses[tf].get('enhanced_signal', 'HOLD')
                    if signal != 'HOLD':
                        consensus = signal
                        confidence = filtered_analyses[tf].get('signal_confidence', 0.5)
                        agreement_count = buy_count if signal == 'BUY' else sell_count
                        break

        else:  # weighted_priority (default)
            if weighted_buy > weighted_sell and buy_count >= min_timeframes_agree and weighted_buy >= min_confidence:
                consensus = 'BUY'
                agreement_count = buy_count
                confidence = weighted_buy
            elif weighted_sell > weighted_buy and sell_count >= min_timeframes_agree and weighted_sell >= min_confidence:
                consensus = 'SELL'
                agreement_count = sell_count
                confidence = weighted_sell
            else:
                consensus = 'HOLD'
                agreement_count = hold_count
                confidence = 0.5

        return {
            'consensus': consensus,
            'agreement_count': agreement_count,
            'total_timeframes': total_timeframes,
            'confidence': confidence,
            'buy_timeframes': buy_count,
            'sell_timeframes': sell_count,
            'hold_timeframes': hold_count,
            'reversals_detected': reversals_detected,
            'has_reversal_warning': len(reversals_detected) > 0,
            'filtered_reasons': filtered_reasons,  # NEW: Why signals were filtered
            'conflict_mode': conflict_mode  # NEW: Which mode was used
        }

    def get_detailed_report(self, analyses: Dict[str, Dict]) -> str:
        """
        Generate a detailed text report of the analysis

        Args:
            analyses: Dictionary of timeframe analyses

        Returns:
            Formatted report string
        """
        if not analyses:
            return "No analysis data available"

        report = []
        report.append("=" * 60)
        report.append("MULTI-TIMEFRAME FOREX ANALYSIS REPORT")
        report.append("=" * 60)

        # Overall consensus
        consensus = self.get_timeframe_consensus(analyses)
        report.append(f"\nOVERALL CONSENSUS: {consensus['consensus']}")
        report.append(f"Confidence: {consensus['confidence']:.2%}")
        report.append(f"Agreement: {consensus['agreement_count']}/{consensus['total_timeframes']} timeframes")

        # Individual timeframe details
        report.append("\n" + "-" * 60)
        report.append("TIMEFRAME BREAKDOWN")
        report.append("-" * 60)

        for tf in ['1d', '4h', '1h', '15m']:
            if tf not in analyses:
                continue

            analysis = analyses[tf]
            report.append(f"\n[{tf.upper()}] Timeframe:")
            report.append(f"  Price: {analysis['current_data']['price']:.5f}")
            report.append(f"  Trend Strength: {analysis['trend_strength']:.2%}")
            report.append(f"  Momentum: {analysis['momentum']}")

            # Signals
            signals = analysis['signals']
            buy_signals = sum(1 for s in signals.values() if s == 'BUY')
            sell_signals = sum(1 for s in signals.values() if s == 'SELL')

            report.append(f"  Signals: {buy_signals} BUY, {sell_signals} SELL")
            report.append(f"    - MA Cross: {signals.get('ma_cross', 'N/A')}")
            report.append(f"    - RSI: {signals.get('rsi', 'N/A')}")
            report.append(f"    - MACD: {signals.get('macd', 'N/A')}")
            report.append(f"    - Stochastic: {signals.get('stochastic', 'N/A')}")
            report.append(f"    - S/R: {signals.get('support_resistance', 'N/A')}")

            # Key levels
            if analysis['support_levels']:
                report.append(f"  Support: {', '.join([f'{s:.5f}' for s in analysis['support_levels'][:3]])}")
            if analysis['resistance_levels']:
                report.append(f"  Resistance: {', '.join([f'{r:.5f}' for r in analysis['resistance_levels'][:3]])}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)
