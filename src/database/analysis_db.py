"""
Analysis Database Manager
Stores and manages trading analysis results with weekly rotation
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import os
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def convert_numpy_types(obj):
    """
    Convert numpy and pandas types to native Python types for JSON serialization

    Args:
        obj: Object to convert

    Returns:
        Converted object
    """
    # Handle None first
    if obj is None:
        return None

    # Get type name for robust checking
    type_name = type(obj).__name__

    # Handle pandas DataFrame - convert to dict
    if isinstance(obj, pd.DataFrame):
        # Convert DataFrame to a serializable dict
        # IMPORTANT: index might be DatetimeIndex with Timestamp objects!
        return {
            'columns': [convert_numpy_types(col) for col in obj.columns.tolist()],
            'index': [convert_numpy_types(idx) for idx in obj.index.tolist()],
            'data': [[convert_numpy_types(val) for val in row] for row in obj.values.tolist()],
            '_type': 'DataFrame'
        }

    # Handle pandas Series
    if isinstance(obj, pd.Series):
        # IMPORTANT: index might be DatetimeIndex with Timestamp objects!
        return {
            'index': [convert_numpy_types(idx) for idx in obj.index.tolist()],
            'data': [convert_numpy_types(val) for val in obj.values.tolist()],
            '_type': 'Series'
        }

    # Handle pandas NA/NaN values
    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass  # Not a scalar that can be checked with pd.isna

    # Handle pandas Timestamp - use both isinstance and type name
    if isinstance(obj, pd.Timestamp) or type_name == 'Timestamp':
        try:
            return obj.isoformat()
        except:
            return str(obj)

    # Handle datetime objects (in case they're regular datetime, not pd.Timestamp)
    if type_name in ('datetime', 'date'):
        try:
            return obj.isoformat()
        except:
            return str(obj)

    # Handle pandas Timedelta
    if isinstance(obj, pd.Timedelta) or type_name == 'Timedelta':
        return str(obj)

    # Handle numpy integer types - use type name as fallback
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8, np.uint64, np.uint32, np.uint16, np.uint8)) or \
       type_name in ('int64', 'int32', 'int16', 'int8', 'uint64', 'uint32', 'uint16', 'uint8'):
        return int(obj)

    # Handle numpy floating types - use type name as fallback
    if isinstance(obj, (np.float64, np.float32, np.float16)) or \
       type_name in ('float64', 'float32', 'float16'):
        try:
            if np.isnan(obj):
                return None
            elif np.isinf(obj):
                return None
            return float(obj)
        except:
            return float(obj)

    # Handle numpy boolean
    if isinstance(obj, np.bool_) or type_name == 'bool_':
        return bool(obj)

    # Handle numpy arrays
    if isinstance(obj, np.ndarray) or type_name == 'ndarray':
        return [convert_numpy_types(item) for item in obj.tolist()]

    # Handle Python complex numbers
    if isinstance(obj, complex):
        return {'real': obj.real, 'imag': obj.imag}

    # Handle collections recursively
    if isinstance(obj, dict):
        return {str(key): convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, set):
        return [convert_numpy_types(item) for item in obj]

    # Catch-all for any datetime-like objects with isoformat method
    # This catches any Timestamp/datetime objects that slipped through above checks
    if hasattr(obj, 'isoformat') and callable(getattr(obj, 'isoformat')):
        try:
            return obj.isoformat()
        except:
            return str(obj)

    # Return as-is for standard Python types
    return obj


class AnalysisDB:
    """Manages SQLite database for analysis results"""

    def __init__(self, db_path: str = 'data/analysis.db'):
        """
        Initialize analysis database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info(f"Analysis database initialized at {db_path}")

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
            # Create analysis_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,

                    -- Analysis results
                    consensus TEXT,
                    confidence REAL,
                    signal_strength TEXT,

                    -- Timeframe breakdown
                    tf_15m_signal TEXT,
                    tf_1h_signal TEXT,
                    tf_4h_signal TEXT,
                    tf_1d_signal TEXT,

                    tf_15m_confidence REAL,
                    tf_1h_confidence REAL,
                    tf_4h_confidence REAL,
                    tf_1d_confidence REAL,

                    -- Technical indicators
                    rsi REAL,
                    macd REAL,
                    price REAL,
                    atr REAL,

                    -- Trend analysis
                    trend_strength REAL,
                    momentum TEXT,
                    reversal_detected INTEGER DEFAULT 0,
                    reversal_type TEXT,

                    -- Support/Resistance
                    nearest_support REAL,
                    nearest_resistance REAL,

                    -- Risk management
                    stop_loss REAL,
                    take_profit REAL,
                    risk_reward_ratio REAL,

                    -- Full analysis (JSON)
                    full_analysis TEXT,

                    -- Metadata
                    created_at TEXT NOT NULL,
                    data_timestamp TEXT NOT NULL,
                    is_latest INTEGER DEFAULT 1
                )
            ''')

            # Create analysis_changes table (tracks what changed between analyses)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,

                    previous_signal TEXT,
                    current_signal TEXT,
                    signal_changed INTEGER DEFAULT 0,

                    confidence_change REAL,
                    confidence_direction TEXT,

                    change_type TEXT,
                    change_description TEXT,

                    previous_analysis_id INTEGER,
                    current_analysis_id INTEGER,

                    created_at TEXT NOT NULL,

                    FOREIGN KEY (previous_analysis_id) REFERENCES analysis_results (id),
                    FOREIGN KEY (current_analysis_id) REFERENCES analysis_results (id)
                )
            ''')

            # Create analysis_summary table (daily/hourly summaries)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    period TEXT NOT NULL,

                    total_assets_analyzed INTEGER,
                    buy_signals INTEGER,
                    sell_signals INTEGER,
                    hold_signals INTEGER,

                    signal_changes INTEGER,
                    avg_confidence REAL,

                    reversals_detected INTEGER,

                    created_at TEXT NOT NULL
                )
            ''')

            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_asset_symbol
                ON analysis_results (asset_symbol)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timeframe
                ON analysis_results (timeframe)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON analysis_results (created_at)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_is_latest
                ON analysis_results (is_latest)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_asset_timeframe
                ON analysis_results (asset_symbol, timeframe, is_latest)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_changes_asset
                ON analysis_changes (asset_symbol)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_summary_date
                ON analysis_summary (date, period)
            ''')

            conn.commit()
            logger.info("Analysis database tables created successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise

        finally:
            conn.close()

    def store_analysis(
        self,
        asset_symbol: str,
        timeframe: str,
        analysis_data: Dict
    ) -> Tuple[bool, Optional[int]]:
        """
        Store analysis results in database

        Args:
            asset_symbol: Asset symbol (e.g., 'EURUSD=X')
            timeframe: Timeframe (e.g., '1d', '4h')
            analysis_data: Analysis results dictionary

        Returns:
            Tuple of (success, analysis_id)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Get previous latest analysis for comparison
            previous = self.get_latest_analysis(asset_symbol, timeframe)

            # Check if this is a duplicate by comparing all fields except timestamps
            if previous:
                consensus_data = analysis_data.get('consensus', {})
                current_data = analysis_data.get('current_data', {})
                tf_analyses = analysis_data.get('timeframe_analyses', {})
                reversal_data = analysis_data.get('reversal_detection', {})

                # Compare all columns (except id, created_at, data_timestamp, is_latest)
                is_duplicate = True

                # Compare consensus and confidence
                if previous.get('consensus') != consensus_data.get('consensus', 'HOLD'):
                    is_duplicate = False
                elif abs(previous.get('confidence', 0.0) - consensus_data.get('confidence', 0.0)) > 0.001:
                    is_duplicate = False

                # Compare signal strength
                elif previous.get('signal_strength') != analysis_data.get('signal_strength', 'NEUTRAL'):
                    is_duplicate = False

                # Compare timeframe signals
                elif previous.get('tf_15m_signal') != tf_analyses.get('15m', {}).get('enhanced_signal', 'HOLD'):
                    is_duplicate = False
                elif previous.get('tf_1h_signal') != tf_analyses.get('1h', {}).get('enhanced_signal', 'HOLD'):
                    is_duplicate = False
                elif previous.get('tf_4h_signal') != tf_analyses.get('4h', {}).get('enhanced_signal', 'HOLD'):
                    is_duplicate = False
                elif previous.get('tf_1d_signal') != tf_analyses.get('1d', {}).get('enhanced_signal', 'HOLD'):
                    is_duplicate = False

                # Compare timeframe confidences (allow 0.1% difference)
                elif abs(previous.get('tf_15m_confidence', 0.0) - tf_analyses.get('15m', {}).get('signal_confidence', 0.0)) > 0.001:
                    is_duplicate = False
                elif abs(previous.get('tf_1h_confidence', 0.0) - tf_analyses.get('1h', {}).get('signal_confidence', 0.0)) > 0.001:
                    is_duplicate = False
                elif abs(previous.get('tf_4h_confidence', 0.0) - tf_analyses.get('4h', {}).get('signal_confidence', 0.0)) > 0.001:
                    is_duplicate = False
                elif abs(previous.get('tf_1d_confidence', 0.0) - tf_analyses.get('1d', {}).get('signal_confidence', 0.0)) > 0.001:
                    is_duplicate = False

                # Compare RSI (allow 0.01 difference)
                elif current_data.get('rsi') is not None and previous.get('rsi') is not None:
                    if abs(previous.get('rsi', 0.0) - current_data.get('rsi', 0.0)) > 0.01:
                        is_duplicate = False

                # Compare MACD (allow 0.01 difference)
                elif current_data.get('macd') is not None and previous.get('macd') is not None:
                    if abs(previous.get('macd', 0.0) - current_data.get('macd', 0.0)) > 0.01:
                        is_duplicate = False

                # Compare price (allow 0.00001 difference - 5 decimal places)
                elif current_data.get('price') is not None and previous.get('price') is not None:
                    if abs(previous.get('price', 0.0) - current_data.get('price', 0.0)) > 0.00001:
                        is_duplicate = False

                # Compare ATR (allow 0.001 difference)
                elif current_data.get('atr') is not None and previous.get('atr') is not None:
                    if abs(previous.get('atr', 0.0) - current_data.get('atr', 0.0)) > 0.001:
                        is_duplicate = False

                # Compare trend strength (allow 0.001 difference)
                elif abs(previous.get('trend_strength', 0.0) - analysis_data.get('trend_strength', 0.0)) > 0.001:
                    is_duplicate = False

                # Compare momentum
                elif previous.get('momentum') != analysis_data.get('momentum', 'NEUTRAL'):
                    is_duplicate = False

                # Compare reversal detection
                elif bool(previous.get('reversal_detected', 0)) != bool(reversal_data.get('is_reversal', False)):
                    is_duplicate = False
                elif previous.get('reversal_type') != reversal_data.get('reversal_type'):
                    is_duplicate = False

                # Compare support/resistance (allow 0.00001 difference)
                elif analysis_data.get('nearest_support') is not None and previous.get('nearest_support') is not None:
                    if abs(previous.get('nearest_support', 0.0) - analysis_data.get('nearest_support', 0.0)) > 0.00001:
                        is_duplicate = False
                elif analysis_data.get('nearest_resistance') is not None and previous.get('nearest_resistance') is not None:
                    if abs(previous.get('nearest_resistance', 0.0) - analysis_data.get('nearest_resistance', 0.0)) > 0.00001:
                        is_duplicate = False

                # Compare stop loss/take profit (allow 0.00001 difference)
                elif analysis_data.get('stop_loss') is not None and previous.get('stop_loss') is not None:
                    if abs(previous.get('stop_loss', 0.0) - analysis_data.get('stop_loss', 0.0)) > 0.00001:
                        is_duplicate = False
                elif analysis_data.get('take_profit') is not None and previous.get('take_profit') is not None:
                    if abs(previous.get('take_profit', 0.0) - analysis_data.get('take_profit', 0.0)) > 0.00001:
                        is_duplicate = False

                # Compare risk/reward ratio (allow 0.001 difference)
                elif analysis_data.get('risk_reward_ratio') is not None and previous.get('risk_reward_ratio') is not None:
                    if abs(previous.get('risk_reward_ratio', 0.0) - analysis_data.get('risk_reward_ratio', 0.0)) > 0.001:
                        is_duplicate = False

                # If all comparisons passed, it's a duplicate
                if is_duplicate:
                    logger.info(f"Duplicate analysis detected for {asset_symbol} {timeframe} - skipping save")
                    return True, previous.get('id')

            # Mark all previous analyses for this asset/timeframe as not latest
            cursor.execute('''
                UPDATE analysis_results
                SET is_latest = 0
                WHERE asset_symbol = ? AND timeframe = ?
            ''', (asset_symbol, timeframe))

            # Extract data from analysis
            consensus_data = analysis_data.get('consensus', {})
            current_data = analysis_data.get('current_data', {})
            tf_analyses = analysis_data.get('timeframe_analyses', {})

            # Insert new analysis
            cursor.execute('''
                INSERT INTO analysis_results (
                    asset_symbol, timeframe,
                    consensus, confidence, signal_strength,
                    tf_15m_signal, tf_1h_signal, tf_4h_signal, tf_1d_signal,
                    tf_15m_confidence, tf_1h_confidence, tf_4h_confidence, tf_1d_confidence,
                    rsi, macd, price, atr,
                    trend_strength, momentum, reversal_detected, reversal_type,
                    nearest_support, nearest_resistance,
                    stop_loss, take_profit, risk_reward_ratio,
                    full_analysis,
                    created_at, data_timestamp, is_latest
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset_symbol,
                timeframe,
                consensus_data.get('consensus', 'HOLD'),
                consensus_data.get('confidence', 0.0),
                analysis_data.get('signal_strength', 'NEUTRAL'),
                tf_analyses.get('15m', {}).get('enhanced_signal', 'HOLD'),
                tf_analyses.get('1h', {}).get('enhanced_signal', 'HOLD'),
                tf_analyses.get('4h', {}).get('enhanced_signal', 'HOLD'),
                tf_analyses.get('1d', {}).get('enhanced_signal', 'HOLD'),
                tf_analyses.get('15m', {}).get('signal_confidence', 0.0),
                tf_analyses.get('1h', {}).get('signal_confidence', 0.0),
                tf_analyses.get('4h', {}).get('signal_confidence', 0.0),
                tf_analyses.get('1d', {}).get('signal_confidence', 0.0),
                current_data.get('rsi'),
                current_data.get('macd'),
                current_data.get('price'),
                current_data.get('atr'),
                analysis_data.get('trend_strength', 0.0),
                analysis_data.get('momentum', 'NEUTRAL'),
                1 if analysis_data.get('reversal_detection', {}).get('is_reversal', False) else 0,
                analysis_data.get('reversal_detection', {}).get('reversal_type'),
                analysis_data.get('nearest_support'),
                analysis_data.get('nearest_resistance'),
                analysis_data.get('stop_loss'),
                analysis_data.get('take_profit'),
                analysis_data.get('risk_reward_ratio'),
                json.dumps(convert_numpy_types(analysis_data)),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                1
            ))

            analysis_id = cursor.lastrowid

            # Track changes if previous analysis exists
            if previous:
                self._track_changes(
                    cursor,
                    asset_symbol,
                    timeframe,
                    previous,
                    analysis_data,
                    previous['id'],
                    analysis_id
                )

            conn.commit()
            logger.info(f"Analysis stored for {asset_symbol} {timeframe} (ID: {analysis_id})")

            return True, analysis_id

        except Exception as e:
            logger.error(f"Error storing analysis: {e}")
            logger.error(f"Analysis data type: {type(analysis_data)}")

            # Try to identify the problematic field - test AFTER conversion
            try:
                converted_data = convert_numpy_types(analysis_data)
                for key, value in converted_data.items():
                    try:
                        json.dumps({key: value})
                    except TypeError as te:
                        logger.error(f"Problematic field '{key}' AFTER conversion: type={type(value)}, error={te}")
                        # Log the original value type for comparison
                        original_value = analysis_data.get(key)
                        logger.error(f"  Original type: {type(original_value)}, Original value class: {type(original_value).__name__}")

                        # If it's a dict, check nested values - GO DEEPER
                        if isinstance(value, dict):
                            for nested_key, nested_value in value.items():
                                try:
                                    json.dumps({nested_key: nested_value})
                                except TypeError as nested_te:
                                    logger.error(f"    Nested field '{nested_key}': type={type(nested_value).__name__}, error={nested_te}")

                                    # GO EVEN DEEPER - check the dict inside
                                    if isinstance(nested_value, dict):
                                        for deep_key, deep_value in nested_value.items():
                                            logger.error(f"      Deep field '{deep_key}': type={type(deep_value).__name__}")
                                            # Check if it has isoformat method
                                            if hasattr(deep_value, 'isoformat'):
                                                logger.error(f"        ⚠️ HAS ISOFORMAT! Type: {type(deep_value)}, calling: {deep_value.isoformat()}")

                                            # If it's another dict, go DEEPER
                                            if isinstance(deep_value, dict):
                                                for deeper_key, deeper_value in deep_value.items():
                                                    if hasattr(deeper_value, 'isoformat'):
                                                        logger.error(f"        ⚠️⚠️ FOUND TIMESTAMP 4 LEVELS DEEP! Field: {deep_key}.{deeper_key}, Type: {type(deeper_value).__name__}")
            except Exception as debug_error:
                logger.error(f"Error during debug: {debug_error}")
                import traceback
                logger.error(f"Debug traceback: {traceback.format_exc()}")

            conn.rollback()
            return False, None

        finally:
            conn.close()

    def _track_changes(
        self,
        cursor,
        asset_symbol: str,
        timeframe: str,
        previous: Dict,
        current: Dict,
        previous_id: int,
        current_id: int
    ):
        """
        Track changes between analyses

        Args:
            cursor: Database cursor
            asset_symbol: Asset symbol
            timeframe: Timeframe
            previous: Previous analysis data
            current: Current analysis data
            previous_id: Previous analysis ID
            current_id: Current analysis ID
        """
        try:
            prev_consensus = previous.get('consensus', 'HOLD')
            curr_consensus = current.get('consensus', {}).get('consensus', 'HOLD')

            prev_confidence = previous.get('confidence', 0.0)
            curr_confidence = current.get('consensus', {}).get('confidence', 0.0)

            signal_changed = prev_consensus != curr_consensus
            confidence_change = curr_confidence - prev_confidence

            if confidence_change > 0:
                confidence_direction = 'UP'
            elif confidence_change < 0:
                confidence_direction = 'DOWN'
            else:
                confidence_direction = 'STABLE'

            # Determine change type
            if signal_changed:
                if prev_consensus == 'HOLD' and curr_consensus in ['BUY', 'SELL']:
                    change_type = 'NEW_SIGNAL'
                    change_desc = f"New {curr_consensus} signal generated"
                elif prev_consensus in ['BUY', 'SELL'] and curr_consensus == 'HOLD':
                    change_type = 'SIGNAL_CANCELLED'
                    change_desc = f"{prev_consensus} signal cancelled"
                elif (prev_consensus == 'BUY' and curr_consensus == 'SELL') or \
                     (prev_consensus == 'SELL' and curr_consensus == 'BUY'):
                    change_type = 'SIGNAL_REVERSAL'
                    change_desc = f"Signal reversed from {prev_consensus} to {curr_consensus}"
                else:
                    change_type = 'SIGNAL_CHANGE'
                    change_desc = f"Signal changed from {prev_consensus} to {curr_consensus}"
            elif abs(confidence_change) >= 0.1:
                change_type = 'CONFIDENCE_CHANGE'
                change_desc = f"Confidence {'increased' if confidence_change > 0 else 'decreased'} by {abs(confidence_change):.2%}"
            else:
                change_type = 'NO_SIGNIFICANT_CHANGE'
                change_desc = "No significant changes detected"

            # Insert change record
            cursor.execute('''
                INSERT INTO analysis_changes (
                    asset_symbol, timeframe,
                    previous_signal, current_signal, signal_changed,
                    confidence_change, confidence_direction,
                    change_type, change_description,
                    previous_analysis_id, current_analysis_id,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset_symbol,
                timeframe,
                prev_consensus,
                curr_consensus,
                1 if signal_changed else 0,
                confidence_change,
                confidence_direction,
                change_type,
                change_desc,
                previous_id,
                current_id,
                datetime.now().isoformat()
            ))

            logger.info(f"Change tracked: {change_type} for {asset_symbol} {timeframe}")

        except Exception as e:
            logger.error(f"Error tracking changes: {e}")

    def get_latest_analysis(
        self,
        asset_symbol: str,
        timeframe: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get latest analysis for asset

        Args:
            asset_symbol: Asset symbol
            timeframe: Timeframe (optional, returns all if None)

        Returns:
            Analysis dictionary or None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if timeframe:
                cursor.execute('''
                    SELECT * FROM analysis_results
                    WHERE asset_symbol = ? AND timeframe = ? AND is_latest = 1
                    ORDER BY created_at DESC LIMIT 1
                ''', (asset_symbol, timeframe))
            else:
                cursor.execute('''
                    SELECT * FROM analysis_results
                    WHERE asset_symbol = ? AND is_latest = 1
                    ORDER BY created_at DESC
                ''', (asset_symbol,))

            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error getting latest analysis: {e}")
            return None

        finally:
            conn.close()

    def get_analysis_changes(
        self,
        asset_symbol: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict]:
        """
        Get recent analysis changes

        Args:
            asset_symbol: Asset symbol (optional, all if None)
            hours: Hours to look back

        Returns:
            List of change dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

            if asset_symbol:
                cursor.execute('''
                    SELECT * FROM analysis_changes
                    WHERE asset_symbol = ? AND created_at >= ?
                    ORDER BY created_at DESC
                ''', (asset_symbol, cutoff_time))
            else:
                cursor.execute('''
                    SELECT * FROM analysis_changes
                    WHERE created_at >= ?
                    ORDER BY created_at DESC
                ''', (cutoff_time,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting analysis changes: {e}")
            return []

        finally:
            conn.close()

    def get_analysis_history(
        self,
        asset_symbol: str,
        timeframe: str,
        days: int = 7
    ) -> List[Dict]:
        """
        Get analysis history for asset

        Args:
            asset_symbol: Asset symbol
            timeframe: Timeframe
            days: Days to look back

        Returns:
            List of analysis dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

            cursor.execute('''
                SELECT * FROM analysis_results
                WHERE asset_symbol = ? AND timeframe = ? AND created_at >= ?
                ORDER BY created_at DESC
            ''', (asset_symbol, timeframe, cutoff_time))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting analysis history: {e}")
            return []

        finally:
            conn.close()

    def cleanup_old_data(self, days: int = 7):
        """
        Clean up analysis data older than specified days (weekly rotation)

        Args:
            days: Days to keep (default: 7)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

            # Delete old analysis results (except latest)
            cursor.execute('''
                DELETE FROM analysis_results
                WHERE created_at < ? AND is_latest = 0
            ''', (cutoff_time,))

            deleted_analyses = cursor.rowcount

            # Delete old changes
            cursor.execute('''
                DELETE FROM analysis_changes
                WHERE created_at < ?
            ''', (cutoff_time,))

            deleted_changes = cursor.rowcount

            # Delete old summaries
            cursor.execute('''
                DELETE FROM analysis_summary
                WHERE created_at < ?
            ''', (cutoff_time,))

            deleted_summaries = cursor.rowcount

            conn.commit()

            logger.info(
                f"Cleanup completed: {deleted_analyses} analyses, "
                f"{deleted_changes} changes, {deleted_summaries} summaries deleted"
            )

            return deleted_analyses, deleted_changes, deleted_summaries

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            conn.rollback()
            return 0, 0, 0

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
            # Total analyses
            cursor.execute('SELECT COUNT(*) FROM analysis_results')
            total_analyses = cursor.fetchone()[0]

            # Latest analyses
            cursor.execute('SELECT COUNT(*) FROM analysis_results WHERE is_latest = 1')
            latest_analyses = cursor.fetchone()[0]

            # Total changes
            cursor.execute('SELECT COUNT(*) FROM analysis_changes')
            total_changes = cursor.fetchone()[0]

            # Recent changes (last 24 hours)
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            cursor.execute('''
                SELECT COUNT(*) FROM analysis_changes WHERE created_at >= ?
            ''', (cutoff,))
            recent_changes = cursor.fetchone()[0]

            # Oldest record
            cursor.execute('SELECT MIN(created_at) FROM analysis_results')
            oldest = cursor.fetchone()[0]

            # Current signals distribution
            cursor.execute('''
                SELECT consensus, COUNT(*) as count
                FROM analysis_results
                WHERE is_latest = 1
                GROUP BY consensus
            ''')
            signal_dist = {row[0]: row[1] for row in cursor.fetchall()}

            return {
                'total_analyses': total_analyses,
                'latest_analyses': latest_analyses,
                'total_changes': total_changes,
                'recent_changes_24h': recent_changes,
                'oldest_record': oldest,
                'signal_distribution': signal_dist
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

        finally:
            conn.close()
