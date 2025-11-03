"""
Risk Management Module
Handles position sizing, stop loss, take profit, and risk management
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RiskManager:
    """Manage trading risk and position sizing"""

    def __init__(self, config: Dict):
        """
        Initialize risk manager

        Args:
            config: Configuration dictionary with risk settings
        """
        self.config = config
        self.risk_config = config.get('risk_management', {})
        self.confluence_config = config.get('confluence', {})
        self.trades = []
        self.current_drawdown = 0.0

    def calculate_position_size(
        self,
        account_balance: float,
        entry_price: float,
        stop_loss_price: float,
        risk_per_trade: Optional[float] = None
    ) -> Dict:
        """
        Calculate position size based on risk management rules

        Args:
            account_balance: Total account balance
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price
            risk_per_trade: Percentage of account to risk (overrides config)

        Returns:
            Dictionary with position sizing details
        """
        if risk_per_trade is None:
            risk_per_trade = self.risk_config.get('risk_per_trade', 0.02)

        # Amount willing to risk
        risk_amount = account_balance * risk_per_trade

        # Price difference to stop loss
        price_diff = abs(entry_price - stop_loss_price)

        if price_diff == 0:
            logger.error("Stop loss price equals entry price")
            return {
                'position_size': 0,
                'risk_amount': 0,
                'error': 'Invalid stop loss'
            }

        # Calculate position size (in lots for forex)
        # For forex: 1 standard lot = 100,000 units
        # Position size = Risk Amount / (Stop Loss Distance in pips * Pip Value)

        # For simplicity, calculate position in units
        position_size = risk_amount / price_diff

        # Convert to lots (for standard forex trading)
        standard_lot = 100000
        lots = position_size / standard_lot

        return {
            'position_size_units': position_size,
            'position_size_lots': lots,
            'risk_amount': risk_amount,
            'risk_percentage': risk_per_trade * 100,
            'stop_loss_distance': price_diff,
            'stop_loss_pct': (price_diff / entry_price) * 100
        }

    def calculate_stop_loss(
        self,
        df: pd.DataFrame,
        entry_price: float,
        signal: str,
        atr_multiplier: Optional[float] = None
    ) -> float:
        """
        Calculate stop loss based on ATR

        Args:
            df: DataFrame with ATR indicator
            entry_price: Entry price
            signal: 'BUY' or 'SELL'
            atr_multiplier: Multiplier for ATR (overrides config)

        Returns:
            Stop loss price
        """
        if 'ATR' not in df.columns:
            logger.warning("ATR not available, using default 2% stop loss")
            if signal == 'BUY':
                return entry_price * 0.98
            else:
                return entry_price * 1.02

        if atr_multiplier is None:
            atr_multiplier = self.risk_config.get('atr_multiplier', 2.0)

        atr = df['ATR'].iloc[-1]
        stop_distance = atr * atr_multiplier

        if signal == 'BUY':
            stop_loss = entry_price - stop_distance
        else:  # SELL
            stop_loss = entry_price + stop_distance

        return stop_loss

    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss_price: float,
        signal: str,
        risk_reward_ratio: Optional[float] = None
    ) -> float:
        """
        Calculate take profit based on risk:reward ratio

        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            signal: 'BUY' or 'SELL'
            risk_reward_ratio: Target risk:reward (overrides config)

        Returns:
            Take profit price
        """
        if risk_reward_ratio is None:
            risk_reward_ratio = self.risk_config.get('min_risk_reward', 1.5)

        stop_distance = abs(entry_price - stop_loss_price)
        profit_distance = stop_distance * risk_reward_ratio

        if signal == 'BUY':
            take_profit = entry_price + profit_distance
        else:  # SELL
            take_profit = entry_price - profit_distance

        return take_profit

    def validate_trade(
        self,
        signal: str,
        confidence: float,
        account_balance: float
    ) -> Dict:
        """
        Validate if trade should be taken based on risk rules

        Args:
            signal: Trading signal
            confidence: Signal confidence
            account_balance: Current account balance

        Returns:
            Dictionary with validation result
        """
        reasons = []
        approved = True

        # Check if signal is actionable
        if signal == 'HOLD':
            return {
                'approved': False,
                'reasons': ['Signal is HOLD']
            }

        # Check confidence threshold
        min_confidence = self.confluence_config.get('min_confidence', 0.6)
        if confidence < min_confidence:
            approved = False
            reasons.append(f'Confidence {confidence:.2%} below minimum {min_confidence:.2%}')

        # Check drawdown limit
        max_drawdown = self.risk_config.get('max_drawdown', 0.15)
        if self.current_drawdown > max_drawdown:
            approved = False
            reasons.append(f'Drawdown {self.current_drawdown:.2%} exceeds limit {max_drawdown:.2%}')

        if approved:
            reasons.append('All risk checks passed')

        return {
            'approved': approved,
            'reasons': reasons
        }

    def create_trade_plan(
        self,
        signal: str,
        entry_price: float,
        confidence: float,
        account_balance: float,
        df: pd.DataFrame
    ) -> Dict:
        """
        Create a complete trade plan with entry, stop loss, take profit, and position sizing

        Args:
            signal: Trading signal ('BUY' or 'SELL')
            entry_price: Entry price
            confidence: Signal confidence
            account_balance: Current account balance
            df: DataFrame with indicators (including ATR)

        Returns:
            Complete trade plan dictionary
        """
        # Validate trade
        validation = self.validate_trade(signal, confidence, account_balance)

        if not validation['approved']:
            return {
                'approved': False,
                'signal': signal,
                'reasons': validation['reasons']
            }

        # Calculate stop loss
        stop_loss = self.calculate_stop_loss(df, entry_price, signal)

        # Calculate take profit
        take_profit = self.calculate_take_profit(entry_price, stop_loss, signal)

        # Calculate position size
        position_info = self.calculate_position_size(
            account_balance,
            entry_price,
            stop_loss
        )

        # Compile trade plan
        trade_plan = {
            'approved': True,
            'signal': signal,
            'confidence': confidence,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size_lots': position_info['position_size_lots'],
            'position_size_units': position_info['position_size_units'],
            'risk_amount': position_info['risk_amount'],
            'risk_percentage': position_info['risk_percentage'],
            'potential_profit': abs(take_profit - entry_price) * position_info['position_size_units'],
            'potential_loss': position_info['risk_amount'],
            'risk_reward_ratio': abs(take_profit - entry_price) / abs(stop_loss - entry_price),
            'timestamp': datetime.now().isoformat()
        }

        return trade_plan

    def create_multi_timeframe_trade_plans(
        self,
        signal: str,
        entry_price: float,
        confidence: float,
        account_balance: float,
        dataframes: Dict[str, pd.DataFrame],
        timeframes: Optional[List[str]] = None
    ) -> Dict:
        """
        Create trade plans for multiple timeframes with expected execution times

        Args:
            signal: Trading signal ('BUY' or 'SELL')
            entry_price: Entry price
            confidence: Signal confidence
            account_balance: Current account balance
            dataframes: Dictionary of DataFrames for each timeframe
            timeframes: List of timeframes to generate plans for

        Returns:
            Dictionary containing plans for each timeframe
        """
        if timeframes is None:
            timeframes = ['15m', '1h', '4h', '1d']

        # Validate trade once for all timeframes
        validation = self.validate_trade(signal, confidence, account_balance)

        if not validation['approved']:
            return {
                'approved': False,
                'signal': signal,
                'reasons': validation['reasons']
            }

        multi_tf_plans = {
            'approved': True,
            'signal': signal,
            'confidence': confidence,
            'entry_price': entry_price,
            'generated_at': datetime.now().isoformat(),
            'timeframe_plans': {}
        }

        # Expected execution timeframes
        timeframe_durations = {
            '15m': {'minutes': 15, 'description': '15 minutes', 'candles_to_target': 20},
            '1h': {'minutes': 60, 'description': '1 hour', 'candles_to_target': 24},
            '4h': {'minutes': 240, 'description': '4 hours', 'candles_to_target': 18},
            '1d': {'minutes': 1440, 'description': '1 day', 'candles_to_target': 10}
        }

        for tf in timeframes:
            if tf not in dataframes or dataframes[tf].empty:
                logger.warning(f"No data available for timeframe {tf}")
                continue

            df = dataframes[tf]

            # Calculate ATR for this timeframe
            atr = df['ATR'].iloc[-1] if 'ATR' in df.columns else entry_price * 0.02

            # Calculate multiple stop loss levels
            stop_losses = self._calculate_multiple_stop_losses(entry_price, signal, atr)

            # Calculate multiple take profit levels
            take_profits = self._calculate_multiple_take_profits(entry_price, signal, atr)

            # Calculate multiple entry points
            entry_points = self._calculate_multiple_entries(entry_price, signal, atr, df)

            # Calculate expected execution time
            tf_info = timeframe_durations.get(tf, {'minutes': 60, 'description': 'Unknown', 'candles_to_target': 15})

            # Estimate based on average target (TP2)
            candles_to_tp = tf_info['candles_to_target']
            expected_duration_minutes = candles_to_tp * tf_info['minutes']
            expected_completion = datetime.now() + timedelta(minutes=expected_duration_minutes)

            # Calculate position sizes for standard stop loss
            standard_sl = stop_losses['standard_2atr']['price']
            position_info = self.calculate_position_size(
                account_balance,
                entry_price,
                standard_sl
            )

            # Calculate risk/reward ratios for each TP level
            risk_reward_ratios = {}
            for tp_name, tp_data in take_profits.items():
                potential_gain = abs(tp_data['price'] - entry_price)
                potential_loss = abs(entry_price - standard_sl)
                if potential_loss > 0:
                    risk_reward_ratios[tp_name] = round(potential_gain / potential_loss, 2)

            # Build the timeframe plan
            tf_plan = {
                'timeframe': tf,
                'timeframe_description': tf_info['description'],
                'entry_points': entry_points,
                'stop_losses': stop_losses,
                'take_profits': take_profits,
                'position_sizing': {
                    'position_size_lots': position_info['position_size_lots'],
                    'position_size_units': position_info['position_size_units'],
                    'risk_amount': position_info['risk_amount'],
                    'risk_percentage': position_info['risk_percentage']
                },
                'risk_reward_ratios': risk_reward_ratios,
                'expected_execution': {
                    'duration_minutes': expected_duration_minutes,
                    'duration_readable': self._format_duration(expected_duration_minutes),
                    'estimated_completion': expected_completion.isoformat(),
                    'estimated_completion_readable': expected_completion.strftime('%Y-%m-%d %H:%M:%S'),
                    'candles_to_target': candles_to_tp
                },
                'trading_strategy': self._get_trading_strategy(tf),
                'current_indicators': self._extract_indicators(df)
            }

            multi_tf_plans['timeframe_plans'][tf] = tf_plan

        return multi_tf_plans

    def _calculate_multiple_stop_losses(self, entry_price: float, signal: str, atr: float) -> Dict:
        """Calculate multiple stop loss options"""
        if signal == 'BUY':
            return {
                'tight_1atr': {
                    'price': round(entry_price - (1 * atr), 5),
                    'description': 'Tight stop - Quick exit if wrong',
                    'risk_pct': round(((1 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 1
                },
                'standard_2atr': {
                    'price': round(entry_price - (2 * atr), 5),
                    'description': 'Standard stop - Recommended (allows normal volatility)',
                    'risk_pct': round(((2 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 2,
                    'recommended': True
                },
                'wide_3atr': {
                    'price': round(entry_price - (3 * atr), 5),
                    'description': 'Wide stop - More breathing room',
                    'risk_pct': round(((3 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 3
                },
                'percentage_2pct': {
                    'price': round(entry_price * 0.98, 5),
                    'description': '2% fixed stop loss',
                    'risk_pct': 2.0,
                    'type': 'percentage'
                },
                'percentage_3pct': {
                    'price': round(entry_price * 0.97, 5),
                    'description': '3% fixed stop loss',
                    'risk_pct': 3.0,
                    'type': 'percentage'
                }
            }
        else:  # SELL
            return {
                'tight_1atr': {
                    'price': round(entry_price + (1 * atr), 5),
                    'description': 'Tight stop - Quick exit if wrong',
                    'risk_pct': round(((1 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 1
                },
                'standard_2atr': {
                    'price': round(entry_price + (2 * atr), 5),
                    'description': 'Standard stop - Recommended (allows normal volatility)',
                    'risk_pct': round(((2 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 2,
                    'recommended': True
                },
                'wide_3atr': {
                    'price': round(entry_price + (3 * atr), 5),
                    'description': 'Wide stop - More breathing room',
                    'risk_pct': round(((3 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 3
                },
                'percentage_2pct': {
                    'price': round(entry_price * 1.02, 5),
                    'description': '2% fixed stop loss',
                    'risk_pct': 2.0,
                    'type': 'percentage'
                },
                'percentage_3pct': {
                    'price': round(entry_price * 1.03, 5),
                    'description': '3% fixed stop loss',
                    'risk_pct': 3.0,
                    'type': 'percentage'
                }
            }

    def _calculate_multiple_take_profits(self, entry_price: float, signal: str, atr: float) -> Dict:
        """Calculate multiple take profit targets"""
        if signal == 'BUY':
            return {
                'tp1_quick': {
                    'price': round(entry_price + (1 * atr), 5),
                    'description': 'Quick profit - Scalp (Close 25% position)',
                    'gain_pct': round(((1 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 1,
                    'position_close_pct': 25
                },
                'tp2_conservative': {
                    'price': round(entry_price + (2 * atr), 5),
                    'description': 'Conservative target (Close 25% position)',
                    'gain_pct': round(((2 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 2,
                    'position_close_pct': 25,
                    'recommended': True
                },
                'tp3_moderate': {
                    'price': round(entry_price + (3 * atr), 5),
                    'description': 'Moderate target (Close 25% position)',
                    'gain_pct': round(((3 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 3,
                    'position_close_pct': 25
                },
                'tp4_aggressive': {
                    'price': round(entry_price + (5 * atr), 5),
                    'description': 'Aggressive target (Close remaining 25%)',
                    'gain_pct': round(((5 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 5,
                    'position_close_pct': 25
                }
            }
        else:  # SELL
            return {
                'tp1_quick': {
                    'price': round(entry_price - (1 * atr), 5),
                    'description': 'Quick profit - Scalp (Close 25% position)',
                    'gain_pct': round(((1 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 1,
                    'position_close_pct': 25
                },
                'tp2_conservative': {
                    'price': round(entry_price - (2 * atr), 5),
                    'description': 'Conservative target (Close 25% position)',
                    'gain_pct': round(((2 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 2,
                    'position_close_pct': 25,
                    'recommended': True
                },
                'tp3_moderate': {
                    'price': round(entry_price - (3 * atr), 5),
                    'description': 'Moderate target (Close 25% position)',
                    'gain_pct': round(((3 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 3,
                    'position_close_pct': 25
                },
                'tp4_aggressive': {
                    'price': round(entry_price - (5 * atr), 5),
                    'description': 'Aggressive target (Close remaining 25%)',
                    'gain_pct': round(((5 * atr) / entry_price) * 100, 2),
                    'atr_multiple': 5,
                    'position_close_pct': 25
                }
            }

    def _calculate_multiple_entries(self, entry_price: float, signal: str, atr: float, df: pd.DataFrame) -> Dict:
        """Calculate multiple entry point options"""
        latest = df.iloc[-1]

        if signal == 'BUY':
            # Try to use Bollinger Bands if available
            bb_lower = latest.get('BB_Lower', entry_price - (1.5 * atr))
            bb_middle = latest.get('BB_Middle', entry_price)

            return {
                'entry_1_immediate': {
                    'price': round(entry_price, 5),
                    'description': 'Market entry - Enter now at current price',
                    'urgency': 'IMMEDIATE',
                    'type': 'MARKET ORDER'
                },
                'entry_2_pullback': {
                    'price': round(entry_price - (0.5 * atr), 5),
                    'description': 'Wait for minor pullback - Better entry',
                    'urgency': 'LIMIT ORDER',
                    'type': 'LIMIT ORDER'
                },
                'entry_3_best': {
                    'price': round(bb_lower if isinstance(bb_lower, (int, float)) else entry_price - (1.5 * atr), 5),
                    'description': 'Best entry near support/BB Lower - Most favorable',
                    'urgency': 'LIMIT ORDER',
                    'type': 'LIMIT ORDER'
                }
            }
        else:  # SELL
            bb_upper = latest.get('BB_Upper', entry_price + (1.5 * atr))
            bb_middle = latest.get('BB_Middle', entry_price)

            return {
                'entry_1_immediate': {
                    'price': round(entry_price, 5),
                    'description': 'Market entry - Enter now at current price',
                    'urgency': 'IMMEDIATE',
                    'type': 'MARKET ORDER'
                },
                'entry_2_pullback': {
                    'price': round(entry_price + (0.5 * atr), 5),
                    'description': 'Wait for minor pullback - Better entry',
                    'urgency': 'LIMIT ORDER',
                    'type': 'LIMIT ORDER'
                },
                'entry_3_best': {
                    'price': round(bb_upper if isinstance(bb_upper, (int, float)) else entry_price + (1.5 * atr), 5),
                    'description': 'Best entry near resistance/BB Upper - Most favorable',
                    'urgency': 'LIMIT ORDER',
                    'type': 'LIMIT ORDER'
                }
            }

    def _format_duration(self, minutes: int) -> str:
        """Format duration in a human-readable way"""
        if minutes < 60:
            return f"{minutes} minutes"
        elif minutes < 1440:
            hours = minutes // 60
            mins = minutes % 60
            if mins > 0:
                return f"{hours} hours {mins} minutes"
            return f"{hours} hours"
        else:
            days = minutes // 1440
            hours = (minutes % 1440) // 60
            if hours > 0:
                return f"{days} days {hours} hours"
            return f"{days} days"

    def _get_trading_strategy(self, timeframe: str) -> Dict:
        """Get recommended trading strategy for each timeframe"""
        strategies = {
            '15m': {
                'style': 'Scalping',
                'holding_period': '15 minutes to 2 hours',
                'description': 'Quick in and out trades, capture small moves',
                'monitoring': 'Requires active monitoring',
                'suitable_for': 'Day traders, active traders'
            },
            '1h': {
                'style': 'Intraday Trading',
                'holding_period': '1 hour to 8 hours',
                'description': 'Intraday swings, close before end of day',
                'monitoring': 'Check every 1-2 hours',
                'suitable_for': 'Day traders, part-time traders'
            },
            '4h': {
                'style': 'Swing Trading',
                'holding_period': '4 hours to 3 days',
                'description': 'Capture medium-term trends',
                'monitoring': 'Check 2-3 times per day',
                'suitable_for': 'Swing traders, working professionals'
            },
            '1d': {
                'style': 'Position Trading',
                'holding_period': '1 day to several weeks',
                'description': 'Long-term trends, larger profit targets',
                'monitoring': 'Check once per day',
                'suitable_for': 'Position traders, long-term investors'
            }
        }
        return strategies.get(timeframe, {
            'style': 'Unknown',
            'holding_period': 'Variable',
            'description': 'Custom timeframe',
            'monitoring': 'As needed',
            'suitable_for': 'All traders'
        })

    def _extract_indicators(self, df: pd.DataFrame) -> Dict:
        """Extract current indicator values from dataframe"""
        latest = df.iloc[-1]

        indicators = {}
        indicator_fields = ['RSI', 'MACD', 'MACD_Signal', 'MACD_Hist',
                          'Stoch_K', 'Stoch_D', 'ATR',
                          'MA_20', 'MA_50', 'MA_200',
                          'BB_Upper', 'BB_Middle', 'BB_Lower']

        for field in indicator_fields:
            if field in df.columns:
                value = latest.get(field)
                if not pd.isna(value):
                    indicators[field] = round(value, 5)

        return indicators

    def record_trade(self, trade: Dict):
        """
        Record a trade for performance tracking

        Args:
            trade: Trade dictionary
        """
        self.trades.append(trade)

    def calculate_performance(self) -> Dict:
        """
        Calculate trading performance metrics

        Returns:
            Dictionary with performance statistics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'average_profit': 0.0,
                'average_loss': 0.0,
                'profit_factor': 0.0,
                'total_pnl': 0.0
            }

        df = pd.DataFrame(self.trades)

        # Calculate metrics
        total_trades = len(df)
        winning_trades = df[df.get('pnl', 0) > 0]
        losing_trades = df[df.get('pnl', 0) < 0]

        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0

        avg_profit = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0.0
        avg_loss = abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0.0

        total_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0.0
        total_loss = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0.0

        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')

        total_pnl = df['pnl'].sum() if 'pnl' in df.columns else 0.0

        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'average_profit': avg_profit,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl,
            'max_drawdown': self.current_drawdown
        }

    def get_performance_report(self) -> str:
        """
        Generate a formatted performance report

        Returns:
            Formatted report string
        """
        metrics = self.calculate_performance()

        report = []
        report.append("=" * 60)
        report.append("TRADING PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"\nTotal Trades: {metrics['total_trades']}")
        report.append(f"Winning Trades: {metrics['winning_trades']}")
        report.append(f"Losing Trades: {metrics['losing_trades']}")
        report.append(f"Win Rate: {metrics['win_rate']:.2%}")
        report.append(f"\nAverage Profit: ${metrics['average_profit']:.2f}")
        report.append(f"Average Loss: ${metrics['average_loss']:.2f}")
        report.append(f"Profit Factor: {metrics['profit_factor']:.2f}")
        report.append(f"\nTotal P&L: ${metrics['total_pnl']:.2f}")
        report.append(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
        report.append("=" * 60)

        return "\n".join(report)
