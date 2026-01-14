"""
Data Snapshots Database
Stores OHLCV data snapshots from scheduled fetches for GUI consumption
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)


class DataSnapshotsDB:
    """Manages data snapshots for GUI consumption"""

    def __init__(self, db_path: str = 'data/data_snapshots.db'):
        """
        Initialize data snapshots database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        self._create_tables()
        logger.info(f"Data snapshots database initialized at {db_path}")

    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        """Create database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create data_snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                data_blob BLOB NOT NULL,
                row_count INTEGER,
                start_date TEXT,
                end_date TEXT,
                last_close_price REAL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                UNIQUE(asset_symbol, timeframe)
            )
        ''')

        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_asset_timeframe
            ON data_snapshots(asset_symbol, timeframe)
        ''')

        # Create index for fetched_at
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_fetched_at
            ON data_snapshots(fetched_at)
        ''')

        conn.commit()
        conn.close()

        logger.info("Data snapshots database tables created successfully")

    def save_snapshot(
        self,
        asset_symbol: str,
        timeframe: str,
        data: pd.DataFrame,
        source: str = 'twelvedata'
    ) -> bool:
        """
        Save or update data snapshot

        Args:
            asset_symbol: Asset symbol (e.g., 'EURUSD=X')
            timeframe: Timeframe (e.g., '15m', '1h', '4h', '1d')
            data: OHLCV DataFrame
            source: Data source name

        Returns:
            True if successful
        """
        try:
            if data is None or len(data) == 0:
                logger.warning(f"Cannot save empty snapshot for {asset_symbol} {timeframe}")
                return False

            # Serialize DataFrame to pickle
            data_blob = pickle.dumps(data)

            # Extract metadata
            row_count = len(data)
            start_date = data.index[0].isoformat() if hasattr(data.index[0], 'isoformat') else str(data.index[0])
            end_date = data.index[-1].isoformat() if hasattr(data.index[-1], 'isoformat') else str(data.index[-1])
            last_close_price = float(data['Close'].iloc[-1]) if 'Close' in data.columns else None

            conn = self._get_connection()
            cursor = conn.cursor()

            # Insert or replace snapshot
            cursor.execute('''
                INSERT OR REPLACE INTO data_snapshots
                (asset_symbol, timeframe, data_blob, row_count, start_date, end_date,
                 last_close_price, fetched_at, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset_symbol,
                timeframe,
                data_blob,
                row_count,
                start_date,
                end_date,
                last_close_price,
                datetime.now().isoformat(),
                source
            ))

            conn.commit()
            conn.close()

            logger.info(f"✅ Saved snapshot: {asset_symbol} {timeframe} ({row_count} rows)")
            return True

        except Exception as e:
            logger.error(f"Error saving snapshot for {asset_symbol} {timeframe}: {e}")
            return False

    def get_snapshot(
        self,
        asset_symbol: str,
        timeframe: str,
        max_age_minutes: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """
        Get latest data snapshot

        Args:
            asset_symbol: Asset symbol
            timeframe: Timeframe
            max_age_minutes: Maximum age of snapshot in minutes (None = any age)

        Returns:
            DataFrame if found and fresh enough, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT data_blob, fetched_at, row_count
                FROM data_snapshots
                WHERE asset_symbol = ? AND timeframe = ?
            ''', (asset_symbol, timeframe))

            row = cursor.fetchone()
            conn.close()

            if not row:
                logger.debug(f"No snapshot found for {asset_symbol} {timeframe}")
                return None

            # Check age if specified
            if max_age_minutes is not None:
                fetched_at = datetime.fromisoformat(row['fetched_at'])
                age_minutes = (datetime.now() - fetched_at).total_seconds() / 60

                if age_minutes > max_age_minutes:
                    logger.debug(
                        f"Snapshot too old for {asset_symbol} {timeframe}: "
                        f"{age_minutes:.1f} min > {max_age_minutes} min"
                    )
                    return None

            # Deserialize DataFrame
            data = pickle.loads(row['data_blob'])

            logger.debug(
                f"✅ Loaded snapshot: {asset_symbol} {timeframe} "
                f"({row['row_count']} rows, fetched at {row['fetched_at']})"
            )

            return data

        except Exception as e:
            logger.error(f"Error loading snapshot for {asset_symbol} {timeframe}: {e}")
            return None

    def get_snapshot_info(self, asset_symbol: str, timeframe: str) -> Optional[Dict]:
        """
        Get snapshot metadata without loading full data

        Args:
            asset_symbol: Asset symbol
            timeframe: Timeframe

        Returns:
            Metadata dictionary or None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT asset_symbol, timeframe, row_count, start_date, end_date,
                       last_close_price, fetched_at, source
                FROM data_snapshots
                WHERE asset_symbol = ? AND timeframe = ?
            ''', (asset_symbol, timeframe))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return {
                'asset_symbol': row['asset_symbol'],
                'timeframe': row['timeframe'],
                'row_count': row['row_count'],
                'start_date': row['start_date'],
                'end_date': row['end_date'],
                'last_close_price': row['last_close_price'],
                'fetched_at': row['fetched_at'],
                'source': row['source'],
                'age_minutes': (datetime.now() - datetime.fromisoformat(row['fetched_at'])).total_seconds() / 60
            }

        except Exception as e:
            logger.error(f"Error getting snapshot info: {e}")
            return None

    def get_all_snapshots_for_asset(self, asset_symbol: str) -> Dict[str, pd.DataFrame]:
        """
        Get all timeframe snapshots for an asset

        Args:
            asset_symbol: Asset symbol

        Returns:
            Dictionary mapping timeframe to DataFrame
        """
        snapshots = {}

        for timeframe in ['15m', '1h', '4h', '1d']:
            data = self.get_snapshot(asset_symbol, timeframe)
            if data is not None:
                snapshots[timeframe] = data

        return snapshots

    def get_available_assets(self) -> List[str]:
        """
        Get list of assets with available snapshots

        Returns:
            List of unique asset symbols
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT DISTINCT asset_symbol
                FROM data_snapshots
                ORDER BY asset_symbol
            ''')

            assets = [row['asset_symbol'] for row in cursor.fetchall()]
            conn.close()

            return assets

        except Exception as e:
            logger.error(f"Error getting available assets: {e}")
            return []

    def get_snapshot_summary(self) -> List[Dict]:
        """
        Get summary of all snapshots

        Returns:
            List of snapshot metadata
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT asset_symbol, timeframe, row_count, last_close_price,
                       fetched_at, source
                FROM data_snapshots
                ORDER BY asset_symbol,
                         CASE timeframe
                             WHEN '1d' THEN 1
                             WHEN '4h' THEN 2
                             WHEN '1h' THEN 3
                             WHEN '15m' THEN 4
                             ELSE 5
                         END
            ''')

            summaries = []
            for row in cursor.fetchall():
                fetched_at = datetime.fromisoformat(row['fetched_at'])
                age_minutes = (datetime.now() - fetched_at).total_seconds() / 60

                summaries.append({
                    'asset_symbol': row['asset_symbol'],
                    'timeframe': row['timeframe'],
                    'row_count': row['row_count'],
                    'last_close_price': row['last_close_price'],
                    'fetched_at': row['fetched_at'],
                    'age_minutes': age_minutes,
                    'source': row['source']
                })

            conn.close()
            return summaries

        except Exception as e:
            logger.error(f"Error getting snapshot summary: {e}")
            return []

    def cleanup_old_snapshots(self, days: int = 1) -> int:
        """
        Delete snapshots older than specified days

        Args:
            days: Keep snapshots from last N days

        Returns:
            Number of snapshots deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM data_snapshots
                WHERE fetched_at < ?
            ''', (cutoff_date.isoformat(),))

            deleted = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"Cleaned up {deleted} old snapshots (older than {days} days)")
            return deleted

        except Exception as e:
            logger.error(f"Error cleaning up snapshots: {e}")
            return 0

    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Total snapshots
            cursor.execute('SELECT COUNT(*) as count FROM data_snapshots')
            total_snapshots = cursor.fetchone()['count']

            # Unique assets
            cursor.execute('SELECT COUNT(DISTINCT asset_symbol) as count FROM data_snapshots')
            unique_assets = cursor.fetchone()['count']

            # Latest snapshot
            cursor.execute('''
                SELECT asset_symbol, timeframe, fetched_at
                FROM data_snapshots
                ORDER BY fetched_at DESC
                LIMIT 1
            ''')
            latest = cursor.fetchone()

            # Oldest snapshot
            cursor.execute('''
                SELECT asset_symbol, timeframe, fetched_at
                FROM data_snapshots
                ORDER BY fetched_at ASC
                LIMIT 1
            ''')
            oldest = cursor.fetchone()

            conn.close()

            return {
                'total_snapshots': total_snapshots,
                'unique_assets': unique_assets,
                'latest_snapshot': dict(latest) if latest else None,
                'oldest_snapshot': dict(oldest) if oldest else None
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
