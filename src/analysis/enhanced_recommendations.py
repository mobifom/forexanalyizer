"""
Enhanced Recommendations Module
Implements ForexApp_V2 style recommendations with multiple entry points, stop losses, and take profit targets
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class EnhancedRecommendations:
    """Generate detailed trading recommendations similar to ForexApp_V2"""

    @staticmethod
    def calculate_signal_score(df: pd.DataFrame, signals: Dict[str, str]) -> Tuple[int, str]:
        """
        Calculate signal score and recommendation

        Args:
            df: DataFrame with indicators
            signals: Dictionary of signal types

        Returns:
            Tuple of (score, recommendation)
        """
        latest = df.iloc[-1]
        score_parts = {'trend': 0, 'momentum': 0, 'strength': 0, 'volatility': 0}

        # Trend Analysis (from moving averages)
        if 'MA_20' in df.columns and 'MA_50' in df.columns:
            if not pd.isna(latest['MA_20']) and not pd.isna(latest['MA_50']):
                if latest['MA_20'] > latest['MA_50']:
                    score_parts['trend'] += 1
                else:
                    score_parts['trend'] -= 1

                if latest['Close'] > latest['MA_20']:
                    score_parts['trend'] += 1
                else:
                    score_parts['trend'] -= 1

        # MACD Signal
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            if not pd.isna(latest['MACD']) and not pd.isna(latest['MACD_Signal']):
                if latest['MACD'] > latest['MACD_Signal']:
                    score_parts['momentum'] += 1
                else:
                    score_parts['momentum'] -= 1

                if 'MACD_Hist' in df.columns and not pd.isna(latest['MACD_Hist']):
                    if latest['MACD_Hist'] > 0:
                        score_parts['momentum'] += 0.5
                    else:
                        score_parts['momentum'] -= 0.5

        # RSI Analysis
        if 'RSI' in df.columns and not pd.isna(latest['RSI']):
            if latest['RSI'] < 30:
                score_parts['strength'] += 2  # Oversold - strong buy
            elif latest['RSI'] < 40:
                score_parts['strength'] += 1  # Slightly oversold
            elif latest['RSI'] > 70:
                score_parts['strength'] -= 2  # Overbought - strong sell
            elif latest['RSI'] > 60:
                score_parts['strength'] -= 1  # Slightly overbought

        # Bollinger Bands
        if 'BB_Lower' in df.columns and 'BB_Upper' in df.columns:
            if not pd.isna(latest['BB_Lower']) and not pd.isna(latest['BB_Upper']):
                if latest['Close'] < latest['BB_Lower']:
                    score_parts['volatility'] += 1  # Below lower band - buy signal
                elif latest['Close'] > latest['BB_Upper']:
                    score_parts['volatility'] -= 1  # Above upper band - sell signal

        # Stochastic
        if 'Stoch_K' in df.columns and 'Stoch_D' in df.columns:
            if not pd.isna(latest['Stoch_K']) and not pd.isna(latest['Stoch_D']):
                if latest['Stoch_K'] < 20 and latest['Stoch_K'] > latest['Stoch_D']:
                    score_parts['momentum'] += 1  # Oversold and turning up
                elif latest['Stoch_K'] > 80 and latest['Stoch_K'] < latest['Stoch_D']:
                    score_parts['momentum'] -= 1  # Overbought and turning down

        # Calculate total score
        total_score = sum(score_parts.values())

        # Determine recommendation
        if total_score >= 3:
            recommendation = "STRONG BUY"
        elif total_score >= 1:
            recommendation = "BUY"
        elif total_score <= -3:
            recommendation = "STRONG SELL"
        elif total_score <= -1:
            recommendation = "SELL"
        else:
            recommendation = "HOLD"

        return total_score, recommendation

    @staticmethod
    def calculate_price_levels(df: pd.DataFrame, recommendation: str) -> Dict:
        """
        Calculate entry points, stop losses, and take profit targets

        Args:
            df: DataFrame with indicators
            recommendation: Trading recommendation

        Returns:
            Dictionary with all price levels
        """
        latest = df.iloc[-1]
        current_price = latest['Close']

        # Get ATR for calculations
        atr = latest.get('ATR', current_price * 0.02)  # Fallback to 2% if no ATR

        # Buy price ranges (support levels)
        buy_range = {
            'strong_buy': round(latest.get('BB_Lower', current_price * 0.98), 5),
            'buy_zone_low': round(current_price - (1.5 * atr), 5),
            'buy_zone_high': round(current_price - (0.5 * atr), 5)
        }

        # Sell price ranges (resistance levels)
        sell_range = {
            'sell_zone_low': round(current_price + (0.5 * atr), 5),
            'sell_zone_high': round(current_price + (1.5 * atr), 5),
            'strong_sell': round(latest.get('BB_Upper', current_price * 1.02), 5)
        }

        # Multiple entry points
        if recommendation in ["BUY", "STRONG BUY"]:
            entry_points = {
                'entry_1_now': {
                    'price': round(current_price, 5),
                    'description': 'Current price - Immediate entry',
                    'urgency': 'NOW'
                },
                'entry_2_pullback': {
                    'price': round(buy_range['buy_zone_high'], 5),
                    'description': 'Better entry on pullback',
                    'urgency': 'LIMIT ORDER'
                },
                'entry_3_best': {
                    'price': round(buy_range['buy_zone_low'], 5),
                    'description': 'Best entry in support zone',
                    'urgency': 'LIMIT ORDER'
                }
            }
        elif recommendation in ["SELL", "STRONG SELL"]:
            entry_points = {
                'entry_1_now': {
                    'price': round(current_price, 5),
                    'description': 'Current price - Immediate entry',
                    'urgency': 'NOW'
                },
                'entry_2_pullback': {
                    'price': round(sell_range['sell_zone_low'], 5),
                    'description': 'Better entry on pullback',
                    'urgency': 'LIMIT ORDER'
                },
                'entry_3_best': {
                    'price': round(sell_range['sell_zone_high'], 5),
                    'description': 'Best entry in resistance zone',
                    'urgency': 'LIMIT ORDER'
                }
            }
        else:
            entry_points = {
                'entry_1_now': {
                    'price': round(current_price, 5),
                    'description': 'No clear entry - HOLD',
                    'urgency': 'WAIT'
                }
            }

        # Multiple stop loss levels
        if recommendation in ["BUY", "STRONG BUY"]:
            stop_losses = {
                'tight_1atr': {
                    'price': round(current_price - (1 * atr), 5),
                    'description': 'Tight stop - Quick exit, less risk',
                    'risk_pct': round(((current_price - (current_price - (1 * atr))) / current_price) * 100, 2)
                },
                'standard_2atr': {
                    'price': round(current_price - (2 * atr), 5),
                    'description': 'Standard stop - Recommended',
                    'risk_pct': round(((current_price - (current_price - (2 * atr))) / current_price) * 100, 2)
                },
                'wide_3atr': {
                    'price': round(current_price - (3 * atr), 5),
                    'description': 'Wide stop - More room, more risk',
                    'risk_pct': round(((current_price - (current_price - (3 * atr))) / current_price) * 100, 2)
                },
                'percentage_2pct': {
                    'price': round(current_price * 0.98, 5),
                    'description': '2% fixed stop loss',
                    'risk_pct': 2.0
                },
                'percentage_3pct': {
                    'price': round(current_price * 0.97, 5),
                    'description': '3% fixed stop loss',
                    'risk_pct': 3.0
                },
                'percentage_5pct': {
                    'price': round(current_price * 0.95, 5),
                    'description': '5% fixed stop loss',
                    'risk_pct': 5.0
                }
            }

            # Multiple take profit targets
            take_profits = {
                'tp1_scalp': {
                    'price': round(current_price + (1 * atr), 5),
                    'description': 'Scalp/Quick profit (25% position)',
                    'gain_pct': round((((current_price + (1 * atr)) - current_price) / current_price) * 100, 2),
                    'atr_multiple': 1
                },
                'tp2_conservative': {
                    'price': round(current_price + (2 * atr), 5),
                    'description': 'Conservative target (25% position)',
                    'gain_pct': round((((current_price + (2 * atr)) - current_price) / current_price) * 100, 2),
                    'atr_multiple': 2
                },
                'tp3_moderate': {
                    'price': round(current_price + (3 * atr), 5),
                    'description': 'Moderate target (25% position)',
                    'gain_pct': round((((current_price + (3 * atr)) - current_price) / current_price) * 100, 2),
                    'atr_multiple': 3
                },
                'tp4_aggressive': {
                    'price': round(current_price + (5 * atr), 5),
                    'description': 'Aggressive target (25% - let it run!)',
                    'gain_pct': round((((current_price + (5 * atr)) - current_price) / current_price) * 100, 2),
                    'atr_multiple': 5
                }
            }

        elif recommendation in ["SELL", "STRONG SELL"]:
            stop_losses = {
                'tight_1atr': {
                    'price': round(current_price + (1 * atr), 5),
                    'description': 'Tight stop - Quick exit, less risk',
                    'risk_pct': round((((current_price + (1 * atr)) - current_price) / current_price) * 100, 2)
                },
                'standard_2atr': {
                    'price': round(current_price + (2 * atr), 5),
                    'description': 'Standard stop - Recommended',
                    'risk_pct': round((((current_price + (2 * atr)) - current_price) / current_price) * 100, 2)
                },
                'wide_3atr': {
                    'price': round(current_price + (3 * atr), 5),
                    'description': 'Wide stop - More room, more risk',
                    'risk_pct': round((((current_price + (3 * atr)) - current_price) / current_price) * 100, 2)
                },
                'percentage_2pct': {
                    'price': round(current_price * 1.02, 5),
                    'description': '2% fixed stop loss',
                    'risk_pct': 2.0
                },
                'percentage_3pct': {
                    'price': round(current_price * 1.03, 5),
                    'description': '3% fixed stop loss',
                    'risk_pct': 3.0
                },
                'percentage_5pct': {
                    'price': round(current_price * 1.05, 5),
                    'description': '5% fixed stop loss',
                    'risk_pct': 5.0
                }
            }

            take_profits = {
                'tp1_scalp': {
                    'price': round(current_price - (1 * atr), 5),
                    'description': 'Scalp/Quick profit (25% position)',
                    'gain_pct': round(((current_price - (current_price - (1 * atr))) / current_price) * 100, 2),
                    'atr_multiple': 1
                },
                'tp2_conservative': {
                    'price': round(current_price - (2 * atr), 5),
                    'description': 'Conservative target (25% position)',
                    'gain_pct': round(((current_price - (current_price - (2 * atr))) / current_price) * 100, 2),
                    'atr_multiple': 2
                },
                'tp3_moderate': {
                    'price': round(current_price - (3 * atr), 5),
                    'description': 'Moderate target (25% position)',
                    'gain_pct': round(((current_price - (current_price - (3 * atr))) / current_price) * 100, 2),
                    'atr_multiple': 3
                },
                'tp4_aggressive': {
                    'price': round(current_price - (5 * atr), 5),
                    'description': 'Aggressive target (25% - let it run!)',
                    'gain_pct': round(((current_price - (current_price - (5 * atr))) / current_price) * 100, 2),
                    'atr_multiple': 5
                }
            }
        else:
            # HOLD recommendation
            stop_losses = {
                'standard_2atr': {
                    'price': round(current_price - (2 * atr), 5),
                    'description': 'Protective stop if entering',
                    'risk_pct': round(((current_price - (current_price - (2 * atr))) / current_price) * 100, 2)
                }
            }
            take_profits = {}

        # Calculate risk/reward ratios
        risk_reward_ratios = {}
        if take_profits and stop_losses.get('standard_2atr'):
            standard_sl = stop_losses['standard_2atr']['price']
            potential_loss = abs(current_price - standard_sl)

            if potential_loss > 0:
                for tp_name, tp_data in take_profits.items():
                    potential_gain = abs(tp_data['price'] - current_price)
                    risk_reward_ratios[tp_name] = round(potential_gain / potential_loss, 2)

        return {
            'buy_range': buy_range,
            'sell_range': sell_range,
            'entry_points': entry_points,
            'stop_losses': stop_losses,
            'take_profits': take_profits,
            'risk_reward_ratios': risk_reward_ratios
        }

    @staticmethod
    def generate_enhanced_recommendation(df: pd.DataFrame, signals: Dict[str, str],
                                        timeframe: str) -> Dict:
        """
        Generate enhanced recommendation with all details

        Args:
            df: DataFrame with indicators
            signals: Dictionary of signal types
            timeframe: Timeframe being analyzed

        Returns:
            Complete recommendation dictionary
        """
        # Calculate score and recommendation
        score, recommendation = EnhancedRecommendations.calculate_signal_score(df, signals)

        # Calculate all price levels
        price_levels = EnhancedRecommendations.calculate_price_levels(df, recommendation)

        # Get latest price data
        latest = df.iloc[-1]

        return {
            'timeframe': timeframe,
            'recommendation': recommendation,
            'score': score,
            'current_price': round(latest['Close'], 5),
            'ohlc': {
                'open': round(latest['Open'], 5),
                'high': round(latest['High'], 5),
                'low': round(latest['Low'], 5),
                'close': round(latest['Close'], 5)
            },
            **price_levels,
            'indicators': {
                'RSI': round(latest.get('RSI', 0), 2) if not pd.isna(latest.get('RSI')) else None,
                'MACD': round(latest.get('MACD', 0), 5) if not pd.isna(latest.get('MACD')) else None,
                'MACD_Signal': round(latest.get('MACD_Signal', 0), 5) if not pd.isna(latest.get('MACD_Signal')) else None,
                'Stoch_K': round(latest.get('Stoch_K', 0), 2) if not pd.isna(latest.get('Stoch_K')) else None,
                'Stoch_D': round(latest.get('Stoch_D', 0), 2) if not pd.isna(latest.get('Stoch_D')) else None,
                'ATR': round(latest.get('ATR', 0), 5) if not pd.isna(latest.get('ATR')) else None,
                'MA_20': round(latest.get('MA_20', 0), 5) if not pd.isna(latest.get('MA_20')) else None,
                'MA_50': round(latest.get('MA_50', 0), 5) if not pd.isna(latest.get('MA_50')) else None
            },
            'timestamp': latest.name if hasattr(latest.name, 'strftime') else latest.get('timestamp', 'N/A')
        }
