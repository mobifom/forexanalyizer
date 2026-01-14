#!/usr/bin/env python3
"""
Run the Smart Scheduler for Automated Data Retrieval and Analysis
This script starts the scheduler in background and monitors API usage
"""

import logging
import time
import signal
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import load_config
from src.scheduler.smart_scheduler import SmartScheduler
from src.forex_analyzer import ForexAnalyzer
from src.data.data_fetcher import ForexDataFetcher
from src.database.analysis_db import AnalysisDB
from src.database.signals_db import SignalsDB
from src.database.data_snapshots_db import DataSnapshotsDB
from src.analysis.analysis_comparison import AnalysisComparison

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScheduledAnalyzer:
    """Wrapper to integrate scheduler with ForexAnalyzer"""

    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize scheduled analyzer

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)

        # Initialize scheduler first to get API key provider
        self.scheduler = SmartScheduler(self.config)

        # Get API key provider from scheduler (if using key rotation)
        api_key_provider = None
        if self.scheduler.using_key_rotation:
            api_key_provider = self.scheduler.api_tracker.get_current_key

        # Get data source configuration
        data_config = self.config.get('data', {})
        data_source = data_config.get('data_source', 'auto')

        # Initialize components
        self.data_fetcher = ForexDataFetcher(
            cache_dir='data/cache',
            cache_duration_minutes=data_config.get('cache_duration_minutes', 20),
            data_source=data_source,
            twelvedata_api_key_provider=api_key_provider
        )

        self.analyzer = ForexAnalyzer(self.config)

        # Initialize databases
        self.analysis_db = AnalysisDB()
        self.signals_db = SignalsDB()
        self.snapshots_db = DataSnapshotsDB()

        # Register callbacks
        self.scheduler.register_fetch_callback(self.fetch_data)
        self.scheduler.register_analysis_callback(self.analyze_data)

        # Get assets and timeframes from config
        self.assets = self.config.get('currency_pairs', [])
        self.timeframes = self.config.get('timeframes', ['1d', '4h', '1h', '15m'])

        # Last cleanup time
        self.last_cleanup = time.time()

        logger.info(f"Initialized ScheduledAnalyzer with {len(self.assets)} assets")

    def fetch_data(self, asset: str, timeframe: str) -> bool:
        """
        Fetch data for asset/timeframe

        Args:
            asset: Asset symbol
            timeframe: Timeframe identifier

        Returns:
            True if successful
        """
        try:
            # Map symbol to data source format
            symbol = self._map_symbol(asset)

            # Fetch data
            df = self.data_fetcher.fetch_ohlcv(
                symbol=symbol,
                interval=timeframe,
                period='365d'
            )

            if df is not None and len(df) > 0:
                logger.info(f"✅ Successfully fetched {asset} {timeframe}: {len(df)} candles")

                # Save snapshot to database for GUI consumption
                data_source = 'twelvedata' if self.data_fetcher.twelvedata_fetcher else 'yfinance'
                self.snapshots_db.save_snapshot(
                    asset_symbol=asset,
                    timeframe=timeframe,
                    data=df,
                    source=data_source
                )

                return True
            else:
                logger.warning(f"❌ No data returned for {asset} {timeframe}")
                return False

        except Exception as e:
            logger.error(f"❌ Error fetching {asset} {timeframe}: {e}")
            return False

    def analyze_data(self, asset: str, timeframes: list):
        """
        Analyze data for asset across timeframes

        Args:
            asset: Asset symbol
            timeframes: List of timeframes to analyze
        """
        try:
            logger.info(f"🔍 Starting analysis for {asset} across {timeframes}")

            # Map symbol
            symbol = self._map_symbol(asset)

            # Fetch data for all timeframes
            data_dict = {}
            for tf in timeframes:
                df = self.data_fetcher.fetch_ohlcv(
                    symbol=symbol,
                    interval=tf,
                    period='365d'
                )
                if df is not None and len(df) > 0:
                    data_dict[tf] = df

            if not data_dict:
                logger.warning(f"No data available for {asset} analysis")
                return

            # Perform multi-timeframe analysis
            analyses = self.analyzer.multi_tf_analyzer.analyze_multiple_timeframes(data_dict)

            # Get consensus
            consensus = self.analyzer.multi_tf_analyzer.get_timeframe_consensus(analyses)

            # Prepare analysis data for storage
            analysis_data = {
                'consensus': consensus,
                'timeframe_analyses': {tf: analyses.get(tf, {}) for tf in timeframes if tf in analyses},
                'current_data': analyses.get('1d', {}).get('current_data', {}) if '1d' in analyses else {},
                'trend_strength': analyses.get('1d', {}).get('trend_strength', 0.0) if '1d' in analyses else 0.0,
                'momentum': analyses.get('1d', {}).get('momentum', 'NEUTRAL') if '1d' in analyses else 'NEUTRAL',
                'reversal_detection': analyses.get('1d', {}).get('reversal_detection', {}) if '1d' in analyses else {}
            }

            # Get previous analysis from database
            primary_tf = '1d' if '1d' in timeframes else timeframes[0]
            previous_analysis = self.analysis_db.get_latest_analysis(asset, primary_tf)

            # Compare with previous
            comparison = AnalysisComparison.compare_analyses(previous_analysis, analysis_data)

            # Store new analysis
            success, analysis_id = self.analysis_db.store_analysis(asset, primary_tf, analysis_data)

            # Log results
            logger.info(f"📊 {asset} Analysis Results:")
            logger.info(f"   Consensus: {consensus['consensus']}")
            logger.info(f"   Confidence: {consensus['confidence']:.2%}")
            logger.info(f"   Agreement: {consensus['agreement_count']}/{consensus['total_timeframes']} timeframes")

            if consensus.get('filtered_reasons'):
                logger.info(f"   Filtered: {consensus['filtered_reasons']}")

            if consensus.get('has_reversal_warning'):
                logger.warning(f"   ⚠️  Reversal detected!")

            # Log changes
            if comparison.get('has_changes'):
                logger.info(f"📝 Changes since last analysis:")
                for change in comparison.get('changes', []):
                    if change.get('significance') == 'HIGH':
                        logger.warning(f"   🔴 {change['description']}")
                    elif change.get('significance') == 'MEDIUM':
                        logger.info(f"   🟡 {change['description']}")

            if success:
                logger.info(f"✅ Analysis stored (ID: {analysis_id})")

            # Run cleanup if needed (once per day)
            self._check_and_run_cleanup()

        except Exception as e:
            logger.error(f"❌ Error analyzing {asset}: {e}")

    def _map_symbol(self, asset: str) -> str:
        """
        Map config symbol to data source format

        Args:
            asset: Symbol from config

        Returns:
            Mapped symbol for data source
        """
        # Symbol mappings for different data sources
        mappings = {
            # Crypto symbols
            'BTC/USD': 'BTC-USD',
            'ETH/USD': 'ETH-USD',

            # Indices (TwelveData vs yfinance)
            'US30': '^DJI',      # Fallback to yfinance Dow Jones
            'US100': '^NDX',     # Fallback to yfinance NASDAQ 100

            # Others pass through
        }

        return mappings.get(asset, asset)

    def _check_and_run_cleanup(self):
        """Check if cleanup is needed and run it"""
        # Run cleanup once per day
        now = time.time()
        time_since_cleanup = now - self.last_cleanup

        # 24 hours = 86400 seconds
        if time_since_cleanup >= 86400:
            logger.info("🧹 Running weekly data cleanup...")

            # Keep 7 days of active data
            deleted_analyses = self.analysis_db.cleanup_old_data(days=7)
            archived_signals = self.signals_db.cleanup_old_signals(days=7)

            # Delete very old archived signals (30+ days)
            deleted_signals = self.signals_db.delete_archived_signals(days=30)

            logger.info(f"✅ Cleanup completed:")
            logger.info(f"   - {deleted_analyses[0]} old analyses removed")
            logger.info(f"   - {archived_signals} signals archived")
            logger.info(f"   - {deleted_signals} old archived signals deleted")

            self.last_cleanup = now

    def print_stats(self):
        """Print database statistics"""
        analysis_stats = self.analysis_db.get_stats()
        signal_stats = self.signals_db.get_stats()

        print("\n" + "=" * 60)
        print("📊 ANALYSIS DATABASE STATISTICS")
        print("=" * 60)
        print(f"Total analyses: {analysis_stats.get('total_analyses', 0)}")
        print(f"Latest analyses: {analysis_stats.get('latest_analyses', 0)}")
        print(f"Total changes tracked: {analysis_stats.get('total_changes', 0)}")
        print(f"Changes (last 24h): {analysis_stats.get('recent_changes_24h', 0)}")

        if analysis_stats.get('oldest_record'):
            print(f"Oldest record: {analysis_stats.get('oldest_record')}")

        signal_dist = analysis_stats.get('signal_distribution', {})
        if signal_dist:
            print("\nCurrent Signal Distribution:")
            for signal, count in signal_dist.items():
                print(f"  {signal}: {count}")

        print("\n" + "=" * 60)
        print("📈 SIGNALS DATABASE STATISTICS")
        print("=" * 60)
        print(f"Active signals: {signal_stats.get('total_active_signals', 0)}")
        print(f"Archived signals: {signal_stats.get('total_archived_signals', 0)}")
        print(f"This week's signals: {signal_stats.get('this_week_signals', 0)}")

        signals_by_type = signal_stats.get('signals_by_type', {})
        if signals_by_type:
            print("\nActive Signals by Type:")
            for sig_type, count in signals_by_type.items():
                print(f"  {sig_type}: {count}")

        signals_by_tf = signal_stats.get('signals_by_timeframe', {})
        if signals_by_tf:
            print("\nActive Signals by Timeframe:")
            for tf, count in signals_by_tf.items():
                print(f"  {tf}: {count}")

        print("=" * 60)

    def start(self):
        """Start the scheduler"""
        logger.info("=" * 60)
        logger.info("🚀 STARTING FOREX ANALYZER SCHEDULER WITH ANALYSIS TRACKING")
        logger.info("=" * 60)
        logger.info(f"Assets: {len(self.assets)}")
        logger.info(f"Timeframes: {self.timeframes}")
        logger.info(f"Schedule:")
        for tf, interval in self.scheduler.fetch_intervals.items():
            logger.info(f"  {tf}: Every {interval} minutes")
        logger.info("\nFeatures:")
        logger.info("  ✅ Analysis results stored in database")
        logger.info("  ✅ Change tracking enabled")
        logger.info("  ✅ Weekly data rotation (7 days)")
        logger.info("=" * 60)

        # Print initial stats
        self.print_stats()

        # Start scheduler
        self.scheduler.start(self.assets, self.timeframes)

        logger.info("✅ Scheduler running. Press Ctrl+C to stop.")

    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.scheduler.stop()

        # Print final stats
        self.print_stats()

        logger.info("✅ Scheduler stopped")

    def print_usage_report(self):
        """Print current API usage report"""
        print(self.scheduler.get_usage_report())


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\n🛑 Received interrupt signal")
    if 'scheduled_analyzer' in globals():
        scheduled_analyzer.stop()
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Create and start scheduler
    global scheduled_analyzer
    scheduled_analyzer = ScheduledAnalyzer()
    scheduled_analyzer.start()

    # Monitor loop
    try:
        report_counter = 0
        while True:
            time.sleep(300)  # Check every 5 minutes

            report_counter += 1

            # Print API usage every 5 minutes
            scheduled_analyzer.print_usage_report()

            # Print stats every 15 minutes (every 3rd report)
            if report_counter % 3 == 0:
                scheduled_analyzer.print_stats()

    except KeyboardInterrupt:
        scheduled_analyzer.stop()


if __name__ == '__main__':
    main()
