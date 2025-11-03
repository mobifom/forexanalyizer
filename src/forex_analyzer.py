"""
Main Forex Analyzer Application
Combines all components for comprehensive forex analysis
"""

import pandas as pd
import logging
from typing import Dict, Optional
import os

from .data.data_fetcher import ForexDataFetcher
from .indicators.technical_indicators import TechnicalIndicators, SignalGenerator
from .indicators.support_resistance import SupportResistance
from .analysis.multi_timeframe import MultiTimeframeAnalyzer
from .ml.prediction_model import ForexMLModel, EnsembleVoting
from .risk.risk_manager import RiskManager
from .utils.config_loader import load_config, get_default_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ForexAnalyzer:
    """Main forex analysis application"""

    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        Initialize Forex Analyzer

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        try:
            self.config = load_config(config_path)
            logger.info(f"Configuration loaded from {config_path}")
        except FileNotFoundError:
            logger.warning(f"Config file not found, using defaults")
            self.config = get_default_config()

        # Get API keys from config or environment variables
        twelvedata_key = self.config.get('twelvedata', {}).get('api_key') or os.getenv('TWELVEDATA_API_KEY')
        finnhub_key = self.config.get('finnhub', {}).get('api_key') or os.getenv('FINNHUB_API_KEY')
        oanda_key = self.config.get('oanda', {}).get('api_key') or os.getenv('OANDA_API_KEY')
        oanda_account_type = self.config.get('oanda', {}).get('account_type', 'practice')
        data_source = self.config.get('data', {}).get('data_source', 'auto')

        # Initialize components
        self.data_fetcher = ForexDataFetcher(
            cache_dir='data/cache',
            cache_duration_minutes=self.config['data'].get('cache_duration_minutes', 60),
            data_source=data_source,
            twelvedata_api_key=twelvedata_key,
            finnhub_api_key=finnhub_key,
            oanda_api_key=oanda_key,
            oanda_account_type=oanda_account_type
        )

        self.mtf_analyzer = MultiTimeframeAnalyzer(self.config)
        self.ml_model = ForexMLModel(self.config)
        self.risk_manager = RiskManager(self.config)

        # Try to load pre-trained model
        if os.path.exists('models/forex_model.pkl'):
            self.ml_model.load('models/forex_model.pkl')
            logger.info("Loaded pre-trained ML model")
        else:
            logger.info("No pre-trained model found")

    def analyze_pair(
        self,
        symbol: str,
        account_balance: float = 10000.0,
        use_ml: bool = True
    ) -> Dict:
        """
        Perform complete analysis on a forex pair

        Args:
            symbol: Forex pair symbol (e.g., 'EURUSD=X')
            account_balance: Account balance for position sizing
            use_ml: Whether to use ML model predictions

        Returns:
            Complete analysis dictionary
        """
        logger.info(f"Analyzing {symbol}...")

        # Fetch data for all timeframes
        timeframes = self.config.get('timeframes', ['1d', '4h', '1h', '15m'])
        data = self.data_fetcher.fetch_multiple_timeframes(symbol, timeframes)

        if not data:
            logger.error(f"Failed to fetch data for {symbol}")
            return {'error': 'Failed to fetch data'}

        # Multi-timeframe analysis
        mtf_analysis = self.mtf_analyzer.analyze_multiple_timeframes(data)

        if not mtf_analysis:
            logger.error("Multi-timeframe analysis failed")
            return {'error': 'Analysis failed'}

        # Get consensus
        consensus = self.mtf_analyzer.get_timeframe_consensus(mtf_analysis)

        # ML prediction (using daily data)
        ml_prediction = {'signal': 'HOLD', 'confidence': 0.0}
        if use_ml and '1d' in data and self.ml_model.model is not None:
            df_with_indicators = TechnicalIndicators.add_all_indicators(
                data['1d'].copy(),
                self.config['indicators']
            )
            ml_prediction = self.ml_model.predict(df_with_indicators)

        # Get technical signals from daily timeframe
        technical_signals = {}
        if '1d' in mtf_analysis:
            technical_signals = mtf_analysis['1d']['signals']

        # Ensemble voting (combine technical and ML)
        final_decision = EnsembleVoting.vote(
            technical_signals,
            ml_prediction,
            weights={'ml': 0.5, 'technical': 0.5}
        )

        # Get current price
        current_price = data['1d']['Close'].iloc[-1]

        # Create trade plan if signal is not HOLD
        trade_plan = None
        multi_tf_trade_plans = None

        if final_decision['signal'] != 'HOLD':
            # Create standard trade plan (for backward compatibility)
            trade_plan = self.risk_manager.create_trade_plan(
                signal=final_decision['signal'],
                entry_price=current_price,
                confidence=final_decision['confidence'],
                account_balance=account_balance,
                df=data['1d']
            )

            # Create multi-timeframe trade plans
            multi_tf_trade_plans = self.risk_manager.create_multi_timeframe_trade_plans(
                signal=final_decision['signal'],
                entry_price=current_price,
                confidence=final_decision['confidence'],
                account_balance=account_balance,
                dataframes=data,
                timeframes=['15m', '1h', '4h', '1d']
            )

        # Compile complete analysis
        result = {
            'symbol': symbol,
            'current_price': current_price,
            'timestamp': pd.Timestamp.now().isoformat(),
            'multi_timeframe_consensus': consensus,
            'ml_prediction': ml_prediction,
            'final_decision': final_decision,
            'trade_plan': trade_plan,
            'multi_tf_trade_plans': multi_tf_trade_plans,
            'timeframe_analyses': mtf_analysis
        }

        return result

    def train_model(self, symbol: str = 'EURUSD=X', save_path: str = 'models/forex_model.pkl'):
        """
        Train the ML model on historical data

        Args:
            symbol: Forex pair to train on
            save_path: Path to save the trained model
        """
        logger.info(f"Training ML model on {symbol}...")

        # Fetch daily data
        df = self.data_fetcher.fetch_data(symbol, '1d', use_cache=False)

        if df is None or len(df) < 500:
            logger.error("Insufficient data for training")
            return

        # Add all indicators
        df = TechnicalIndicators.add_all_indicators(df, self.config['indicators'])

        # Train model
        results = self.ml_model.train(df, save_path)

        logger.info("Training complete:")
        logger.info(f"  Train accuracy: {results.get('train_score', 0):.2%}")
        logger.info(f"  Test accuracy: {results.get('test_score', 0):.2%}")

        return results

    def generate_report(self, analysis: Dict) -> str:
        """
        Generate a formatted analysis report

        Args:
            analysis: Analysis dictionary from analyze_pair()

        Returns:
            Formatted report string
        """
        if 'error' in analysis:
            return f"ERROR: {analysis['error']}"

        report = []
        report.append("\n" + "=" * 70)
        report.append("FOREX TRADING ANALYSIS REPORT")
        report.append("=" * 70)

        # Symbol and price
        report.append(f"\nSymbol: {analysis['symbol']}")
        report.append(f"Current Price: {analysis['current_price']:.5f}")
        report.append(f"Analysis Time: {analysis['timestamp']}")

        # Final decision
        final = analysis['final_decision']
        report.append("\n" + "-" * 70)
        report.append("FINAL RECOMMENDATION")
        report.append("-" * 70)
        report.append(f"Signal: {final['signal']}")
        report.append(f"Confidence: {final['confidence']:.2%}")
        report.append(f"  Technical Signal: {final['technical_signal']} ({final['technical_confidence']:.2%})")
        report.append(f"  ML Signal: {final['ml_signal']} ({final['ml_confidence']:.2%})")

        # Multi-timeframe consensus
        consensus = analysis['multi_timeframe_consensus']
        report.append("\n" + "-" * 70)
        report.append("TIMEFRAME CONSENSUS")
        report.append("-" * 70)
        report.append(f"Consensus: {consensus['consensus']}")
        report.append(f"Agreement: {consensus['agreement_count']}/{consensus['total_timeframes']} timeframes")
        report.append(f"BUY signals: {consensus['buy_timeframes']}")
        report.append(f"SELL signals: {consensus['sell_timeframes']}")
        report.append(f"HOLD signals: {consensus['hold_timeframes']}")

        # Trade plan
        if analysis['trade_plan']:
            plan = analysis['trade_plan']
            if plan.get('approved', False):
                report.append("\n" + "-" * 70)
                report.append("TRADE PLAN")
                report.append("-" * 70)
                report.append(f"Entry Price: {plan['entry_price']:.5f}")
                report.append(f"Stop Loss: {plan['stop_loss']:.5f}")
                report.append(f"Take Profit: {plan['take_profit']:.5f}")
                report.append(f"Position Size: {plan['position_size_lots']:.2f} lots ({plan['position_size_units']:.0f} units)")
                report.append(f"Risk Amount: ${plan['risk_amount']:.2f} ({plan['risk_percentage']:.2f}%)")
                report.append(f"Potential Profit: ${plan['potential_profit']:.2f}")
                report.append(f"Potential Loss: ${plan['potential_loss']:.2f}")
                report.append(f"Risk:Reward Ratio: 1:{plan['risk_reward_ratio']:.2f}")
            else:
                report.append("\n" + "-" * 70)
                report.append("TRADE NOT RECOMMENDED")
                report.append("-" * 70)
                for reason in plan.get('reasons', []):
                    report.append(f"  - {reason}")

        # Detailed timeframe analysis
        report.append("\n" + "-" * 70)
        report.append("DETAILED TIMEFRAME ANALYSIS")
        report.append("-" * 70)

        for tf in ['1d', '4h', '1h', '15m']:
            if tf not in analysis['timeframe_analyses']:
                continue

            tf_data = analysis['timeframe_analyses'][tf]
            report.append(f"\n[{tf.upper()}]:")
            report.append(f"  Trend Strength: {tf_data['trend_strength']:.2%}")
            report.append(f"  Momentum: {tf_data['momentum']}")

            signals = tf_data['signals']
            report.append(f"  Signals: MA={signals.get('ma_cross', 'N/A')}, "
                         f"RSI={signals.get('rsi', 'N/A')}, "
                         f"MACD={signals.get('macd', 'N/A')}")

            if tf_data['support_levels']:
                report.append(f"  Support: {tf_data['support_levels'][0]:.5f}")
            if tf_data['resistance_levels']:
                report.append(f"  Resistance: {tf_data['resistance_levels'][0]:.5f}")

        # Enhanced recommendations (ForexApp_V2 style)
        from .utils.recommendation_formatter import RecommendationFormatter

        report.append("\n" + "=" * 70)
        report.append("ENHANCED RECOMMENDATIONS (Multi-Entry & Multi-Target)")
        report.append("=" * 70)

        # Add multi-timeframe summary
        summary = RecommendationFormatter.format_multi_timeframe_summary(
            analysis['timeframe_analyses'],
            analysis['symbol']
        )
        report.append(summary)

        # Add detailed enhanced recommendations for each timeframe
        for tf in ['15m', '1h', '4h', '1d']:
            if tf not in analysis['timeframe_analyses']:
                continue

            tf_data = analysis['timeframe_analyses'][tf]
            enhanced_rec = tf_data.get('enhanced_recommendation')

            if enhanced_rec:
                formatted = RecommendationFormatter.format_enhanced_recommendation(
                    enhanced_rec,
                    analysis['symbol']
                )
                report.append(formatted)

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def scan_multiple_pairs(
        self,
        pairs: Optional[list] = None,
        account_balance: float = 10000.0
    ) -> Dict[str, Dict]:
        """
        Scan multiple currency pairs

        Args:
            pairs: List of pairs to scan (uses config if None)
            account_balance: Account balance for position sizing

        Returns:
            Dictionary mapping pair to analysis
        """
        if pairs is None:
            pairs = self.config.get('currency_pairs', ['EURUSD=X'])

        results = {}
        for pair in pairs:
            logger.info(f"\n{'='*70}")
            logger.info(f"Scanning {pair}...")
            logger.info(f"{'='*70}")

            try:
                analysis = self.analyze_pair(pair, account_balance)
                results[pair] = analysis

                # Print quick summary
                if 'error' not in analysis:
                    final = analysis['final_decision']
                    print(f"\n{pair}: {final['signal']} (Confidence: {final['confidence']:.2%})")
            except Exception as e:
                logger.error(f"Error analyzing {pair}: {e}")
                results[pair] = {'error': str(e)}

        return results
