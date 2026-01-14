"""
Trading Signals Database Manager
Stores and manages trading signals with weekly rotation
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class SignalsDB:
    """Manages SQLite database for trading signals"""

    def __init__(self, db_path: str = 'data/signals.db'):
        """
        Initialize signals database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info(f"Signals database initialized at {db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection

        Returns:
            SQLite connection object
        """
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def _init_database(self):
        """Initialize database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Create trading_signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,

                    -- Signal information
                    signal_type TEXT NOT NULL,  -- BUY or SELL
                    strength_level REAL NOT NULL,  -- Confidence 0-1
                    strength_category TEXT,  -- WEAK, MODERATE, STRONG, VERY_STRONG

                    -- Entry points (JSON array of prices)
                    entry_point_1 REAL,
                    entry_point_2 REAL,
                    entry_point_3 REAL,
                    entry_points_json TEXT,  -- Full entry points data

                    -- Take profit levels (JSON array of prices)
                    take_profit_1 REAL,
                    take_profit_2 REAL,
                    take_profit_3 REAL,
                    take_profits_json TEXT,  -- Full take profit data

                    -- Stop loss levels
                    stop_loss_tight REAL,
                    stop_loss_standard REAL,
                    stop_loss_wide REAL,
                    stop_losses_json TEXT,  -- Full stop loss data

                    -- Risk metrics
                    risk_reward_ratio REAL,
                    risk_percentage REAL,

                    -- Additional context
                    trend_direction TEXT,
                    momentum TEXT,
                    reversal_detected INTEGER DEFAULT 0,
                    reversal_type TEXT,

                    -- Price at signal generation
                    current_price REAL NOT NULL,

                    -- Metadata
                    created_at TEXT NOT NULL,
                    week_number INTEGER NOT NULL,  -- For weekly rotation
                    year INTEGER NOT NULL,  -- For weekly rotation
                    is_active INTEGER DEFAULT 1  -- 1 = active, 0 = archived
                )
            ''')

            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_signals_asset_symbol
                ON trading_signals (asset_symbol)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_signals_timeframe
                ON trading_signals (timeframe)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_signals_created_at
                ON trading_signals (created_at)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_signals_active
                ON trading_signals (is_active)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_signals_week
                ON trading_signals (year, week_number)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_signals_asset_tf_active
                ON trading_signals (asset_symbol, timeframe, is_active)
            ''')

            conn.commit()
            logger.info("Signals database tables created successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def store_signal(
        self,
        asset_symbol: str,
        timeframe: str,
        signal_type: str,
        strength_level: float,
        current_price: float,
        entry_points: Dict = None,
        take_profits: Dict = None,
        stop_losses: Dict = None,
        risk_metrics: Dict = None,
        context: Dict = None
    ) -> Optional[int]:
        """
        Store a trading signal in database

        Args:
            asset_symbol: Asset symbol (e.g., 'EURUSD=X')
            timeframe: Timeframe (e.g., '1d', '4h')
            signal_type: 'BUY' or 'SELL'
            strength_level: Signal confidence (0-1)
            current_price: Current market price
            entry_points: Dict with entry point data
            take_profits: Dict with take profit data
            stop_losses: Dict with stop loss data
            risk_metrics: Dict with risk/reward metrics
            context: Additional context (trend, momentum, reversals)

        Returns:
            Signal ID if successful, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Calculate week number and year
            now = datetime.now()
            week_number = now.isocalendar()[1]
            year = now.year

            # Categorize strength
            if strength_level >= 0.75:
                strength_cat = 'VERY_STRONG'
            elif strength_level >= 0.6:
                strength_cat = 'STRONG'
            elif strength_level >= 0.45:
                strength_cat = 'MODERATE'
            else:
                strength_cat = 'WEAK'

            # Extract entry points
            ep1 = entry_points.get('entry_1_immediate', {}).get('price') if entry_points else None
            ep2 = entry_points.get('entry_2_pullback', {}).get('price') if entry_points else None
            ep3 = entry_points.get('entry_3_aggressive', {}).get('price') if entry_points else None

            # Extract take profits
            tp1 = take_profits.get('tp1_quick', {}).get('price') if take_profits else None
            tp2 = take_profits.get('tp2_conservative', {}).get('price') if take_profits else None
            tp3 = take_profits.get('tp3_extended', {}).get('price') if take_profits else None

            # Extract stop losses
            sl_tight = stop_losses.get('tight_1atr', {}).get('price') if stop_losses else None
            sl_standard = stop_losses.get('standard_2atr', {}).get('price') if stop_losses else None
            sl_wide = stop_losses.get('wide_3atr', {}).get('price') if stop_losses else None

            # Extract risk metrics
            rr_ratio = risk_metrics.get('risk_reward_ratio') if risk_metrics else None
            risk_pct = risk_metrics.get('risk_percentage') if risk_metrics else None

            # Extract context
            trend = context.get('trend_direction', 'NEUTRAL') if context else 'NEUTRAL'
            momentum = context.get('momentum', 'NEUTRAL') if context else 'NEUTRAL'
            reversal = 1 if context and context.get('reversal_detected') else 0
            reversal_type = context.get('reversal_type') if context else None

            # Insert signal
            cursor.execute('''
                INSERT INTO trading_signals (
                    asset_symbol, timeframe,
                    signal_type, strength_level, strength_category,
                    entry_point_1, entry_point_2, entry_point_3, entry_points_json,
                    take_profit_1, take_profit_2, take_profit_3, take_profits_json,
                    stop_loss_tight, stop_loss_standard, stop_loss_wide, stop_losses_json,
                    risk_reward_ratio, risk_percentage,
                    trend_direction, momentum, reversal_detected, reversal_type,
                    current_price,
                    created_at, week_number, year, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset_symbol, timeframe,
                signal_type, strength_level, strength_cat,
                ep1, ep2, ep3, json.dumps(entry_points) if entry_points else None,
                tp1, tp2, tp3, json.dumps(take_profits) if take_profits else None,
                sl_tight, sl_standard, sl_wide, json.dumps(stop_losses) if stop_losses else None,
                rr_ratio, risk_pct,
                trend, momentum, reversal, reversal_type,
                current_price,
                now.isoformat(), week_number, year, 1
            ))

            signal_id = cursor.lastrowid
            conn.commit()

            logger.info(f"Signal stored: {asset_symbol} {timeframe} {signal_type} (ID: {signal_id})")
            return signal_id

        except Exception as e:
            logger.error(f"Error storing signal: {e}")
            conn.rollback()
            return None

        finally:
            conn.close()

    def get_signals(
        self,
        asset_symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
        signal_type: Optional[str] = None,
        limit: int = 20,
        active_only: bool = True
    ) -> List[Dict]:
        """
        Get trading signals from database

        Args:
            asset_symbol: Filter by asset symbol (optional)
            timeframe: Filter by timeframe (optional)
            signal_type: Filter by signal type (optional)
            limit: Maximum number of signals to return
            active_only: Only return active signals (default True)

        Returns:
            List of signal dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = 'SELECT * FROM trading_signals WHERE 1=1'
            params = []

            if asset_symbol:
                query += ' AND asset_symbol = ?'
                params.append(asset_symbol)

            if timeframe:
                query += ' AND timeframe = ?'
                params.append(timeframe)

            if signal_type:
                query += ' AND signal_type = ?'
                params.append(signal_type)

            if active_only:
                query += ' AND is_active = 1'

            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            return []

        finally:
            conn.close()

    def get_signals_by_timeframe(
        self,
        asset_symbol: str,
        limit_per_timeframe: int = 20,
        active_only: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Get signals grouped by timeframe

        Args:
            asset_symbol: Asset symbol
            limit_per_timeframe: Maximum signals per timeframe
            active_only: Only return active signals

        Returns:
            Dictionary mapping timeframe to list of signals
        """
        timeframes = ['15m', '1h', '4h', '1d']
        result = {}

        for tf in timeframes:
            signals = self.get_signals(
                asset_symbol=asset_symbol,
                timeframe=tf,
                limit=limit_per_timeframe,
                active_only=active_only
            )
            if signals:
                result[tf] = signals

        return result

    def cleanup_old_signals(self, days: int = 7):
        """
        Archive signals older than specified days (weekly rotation)

        Args:
            days: Days to keep active (default: 7)

        Returns:
            Number of signals archived
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

            # Mark old signals as inactive instead of deleting
            cursor.execute('''
                UPDATE trading_signals
                SET is_active = 0
                WHERE created_at < ? AND is_active = 1
            ''', (cutoff_time,))

            archived_count = cursor.rowcount
            conn.commit()

            logger.info(f"Archived {archived_count} old signals")
            return archived_count

        except Exception as e:
            logger.error(f"Error cleaning up signals: {e}")
            conn.rollback()
            return 0

        finally:
            conn.close()

    def delete_archived_signals(self, days: int = 30):
        """
        Permanently delete archived signals older than specified days

        Args:
            days: Days to keep archived signals (default: 30)

        Returns:
            Number of signals deleted
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute('''
                DELETE FROM trading_signals
                WHERE created_at < ? AND is_active = 0
            ''', (cutoff_time,))

            deleted_count = cursor.rowcount
            conn.commit()

            logger.info(f"Deleted {deleted_count} archived signals")
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting archived signals: {e}")
            conn.rollback()
            return 0

        finally:
            conn.close()

    def get_stats(self) -> Dict:
        """
        Get database statistics

        Returns:
            Statistics dictionary
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Total signals
            cursor.execute('SELECT COUNT(*) FROM trading_signals WHERE is_active = 1')
            total_active = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM trading_signals WHERE is_active = 0')
            total_archived = cursor.fetchone()[0]

            # Signals by type
            cursor.execute('''
                SELECT signal_type, COUNT(*) as count
                FROM trading_signals
                WHERE is_active = 1
                GROUP BY signal_type
            ''')
            signal_types = {row[0]: row[1] for row in cursor.fetchall()}

            # Signals by timeframe
            cursor.execute('''
                SELECT timeframe, COUNT(*) as count
                FROM trading_signals
                WHERE is_active = 1
                GROUP BY timeframe
            ''')
            timeframes = {row[0]: row[1] for row in cursor.fetchall()}

            # This week's signals
            now = datetime.now()
            week_number = now.isocalendar()[1]
            year = now.year

            cursor.execute('''
                SELECT COUNT(*) FROM trading_signals
                WHERE year = ? AND week_number = ? AND is_active = 1
            ''', (year, week_number))
            this_week = cursor.fetchone()[0]

            return {
                'total_active_signals': total_active,
                'total_archived_signals': total_archived,
                'signals_by_type': signal_types,
                'signals_by_timeframe': timeframes,
                'this_week_signals': this_week
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

        finally:
            conn.close()
