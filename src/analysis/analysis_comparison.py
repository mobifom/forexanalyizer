"""
Analysis Comparison Module
Compares current analysis with stored previous analysis
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalysisComparison:
    """Compare and format analysis changes"""

    @staticmethod
    def compare_analyses(previous: Dict, current: Dict) -> Dict:
        """
        Compare two analyses and generate change report

        Args:
            previous: Previous analysis data
            current: Current analysis data

        Returns:
            Comparison dictionary
        """
        if not previous:
            return {
                'is_first_analysis': True,
                'has_changes': False,
                'changes': []
            }

        changes = []

        # Compare consensus signal
        prev_consensus = previous.get('consensus', 'HOLD')
        curr_consensus = current.get('consensus', {}).get('consensus', 'HOLD')

        if prev_consensus != curr_consensus:
            changes.append({
                'type': 'SIGNAL_CHANGE',
                'field': 'consensus',
                'previous': prev_consensus,
                'current': curr_consensus,
                'significance': 'HIGH',
                'description': f"Signal changed from {prev_consensus} to {curr_consensus}"
            })

        # Compare confidence
        prev_conf = previous.get('confidence', 0.0)
        curr_conf = current.get('consensus', {}).get('confidence', 0.0)
        conf_change = curr_conf - prev_conf

        if abs(conf_change) >= 0.1:  # 10% threshold
            changes.append({
                'type': 'CONFIDENCE_CHANGE',
                'field': 'confidence',
                'previous': prev_conf,
                'current': curr_conf,
                'change': conf_change,
                'significance': 'MEDIUM' if abs(conf_change) < 0.2 else 'HIGH',
                'description': f"Confidence {'increased' if conf_change > 0 else 'decreased'} by {abs(conf_change):.1%}"
            })

        # Compare timeframe signals
        timeframes = ['15m', '1h', '4h', '1d']
        for tf in timeframes:
            prev_tf = previous.get(f'tf_{tf}_signal', 'HOLD')
            curr_tf = current.get('timeframe_analyses', {}).get(tf, {}).get('enhanced_signal', 'HOLD')

            if prev_tf != curr_tf:
                changes.append({
                    'type': 'TIMEFRAME_SIGNAL_CHANGE',
                    'field': f'{tf}_signal',
                    'previous': prev_tf,
                    'current': curr_tf,
                    'significance': 'MEDIUM',
                    'description': f"{tf} signal changed from {prev_tf} to {curr_tf}"
                })

        # Compare reversal detection
        prev_reversal = previous.get('reversal_detected', 0) == 1
        curr_reversal = current.get('reversal_detection', {}).get('is_reversal', False)

        if not prev_reversal and curr_reversal:
            reversal_type = current.get('reversal_detection', {}).get('reversal_type', 'Unknown')
            changes.append({
                'type': 'REVERSAL_DETECTED',
                'field': 'reversal',
                'previous': False,
                'current': True,
                'significance': 'HIGH',
                'description': f"NEW: {reversal_type} reversal detected"
            })
        elif prev_reversal and not curr_reversal:
            changes.append({
                'type': 'REVERSAL_CLEARED',
                'field': 'reversal',
                'previous': True,
                'current': False,
                'significance': 'MEDIUM',
                'description': "Reversal warning cleared"
            })

        # Compare RSI (if available)
        prev_rsi = previous.get('rsi')
        curr_rsi = current.get('current_data', {}).get('rsi')

        if prev_rsi and curr_rsi:
            rsi_change = curr_rsi - prev_rsi

            # Check for significant RSI changes
            if prev_rsi <= 30 and curr_rsi > 30:
                changes.append({
                    'type': 'RSI_CHANGE',
                    'field': 'rsi',
                    'previous': prev_rsi,
                    'current': curr_rsi,
                    'significance': 'MEDIUM',
                    'description': f"RSI moved out of oversold zone ({prev_rsi:.1f} → {curr_rsi:.1f})"
                })
            elif prev_rsi >= 70 and curr_rsi < 70:
                changes.append({
                    'type': 'RSI_CHANGE',
                    'field': 'rsi',
                    'previous': prev_rsi,
                    'current': curr_rsi,
                    'significance': 'MEDIUM',
                    'description': f"RSI moved out of overbought zone ({prev_rsi:.1f} → {curr_rsi:.1f})"
                })
            elif curr_rsi <= 30 and prev_rsi > 30:
                changes.append({
                    'type': 'RSI_CHANGE',
                    'field': 'rsi',
                    'previous': prev_rsi,
                    'current': curr_rsi,
                    'significance': 'HIGH',
                    'description': f"RSI entered oversold zone ({prev_rsi:.1f} → {curr_rsi:.1f})"
                })
            elif curr_rsi >= 70 and prev_rsi < 70:
                changes.append({
                    'type': 'RSI_CHANGE',
                    'field': 'rsi',
                    'previous': prev_rsi,
                    'current': curr_rsi,
                    'significance': 'HIGH',
                    'description': f"RSI entered overbought zone ({prev_rsi:.1f} → {curr_rsi:.1f})"
                })

        return {
            'is_first_analysis': False,
            'has_changes': len(changes) > 0,
            'change_count': len(changes),
            'changes': changes,
            'previous_timestamp': previous.get('created_at'),
            'comparison_time': datetime.now().isoformat()
        }

    @staticmethod
    def format_change_summary(comparison: Dict) -> str:
        """
        Format comparison as human-readable summary

        Args:
            comparison: Comparison dictionary

        Returns:
            Formatted string
        """
        if comparison.get('is_first_analysis'):
            return "📊 First analysis for this asset"

        if not comparison.get('has_changes'):
            return "✅ No significant changes since last analysis"

        changes = comparison.get('changes', [])
        high_changes = [c for c in changes if c['significance'] == 'HIGH']
        medium_changes = [c for c in changes if c['significance'] == 'MEDIUM']

        summary = []

        if high_changes:
            summary.append("🔴 **High Priority Changes:**")
            for change in high_changes:
                summary.append(f"  • {change['description']}")

        if medium_changes:
            summary.append("\n🟡 **Medium Priority Changes:**")
            for change in medium_changes:
                summary.append(f"  • {change['description']}")

        return "\n".join(summary)

    @staticmethod
    def get_signal_emoji(signal: str) -> str:
        """Get emoji for signal"""
        emojis = {
            'BUY': '🟢',
            'STRONG BUY': '🟢🟢',
            'SELL': '🔴',
            'STRONG SELL': '🔴🔴',
            'HOLD': '🟡'
        }
        return emojis.get(signal, '⚪')

    @staticmethod
    def get_change_emoji(change_type: str) -> str:
        """Get emoji for change type"""
        emojis = {
            'SIGNAL_CHANGE': '🔄',
            'CONFIDENCE_CHANGE': '📊',
            'TIMEFRAME_SIGNAL_CHANGE': '⏱️',
            'REVERSAL_DETECTED': '⚠️',
            'REVERSAL_CLEARED': '✅',
            'RSI_CHANGE': '📈'
        }
        return emojis.get(change_type, '•')

    @staticmethod
    def format_change_notification(change: Dict, asset_symbol: str) -> str:
        """
        Format single change as notification message

        Args:
            change: Change dictionary
            asset_symbol: Asset symbol

        Returns:
            Formatted notification string
        """
        emoji = AnalysisComparison.get_change_emoji(change['type'])
        significance = change.get('significance', 'LOW')

        prefix = {
            'HIGH': '🚨',
            'MEDIUM': 'ℹ️',
            'LOW': '•'
        }.get(significance, '•')

        return f"{prefix} {emoji} **{asset_symbol}**: {change['description']}"

    @staticmethod
    def generate_change_report(
        asset_symbol: str,
        timeframe: str,
        comparison: Dict
    ) -> Dict:
        """
        Generate comprehensive change report

        Args:
            asset_symbol: Asset symbol
            timeframe: Timeframe
            comparison: Comparison dictionary

        Returns:
            Report dictionary
        """
        return {
            'asset_symbol': asset_symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'is_first_analysis': comparison.get('is_first_analysis', False),
            'has_changes': comparison.get('has_changes', False),
            'change_count': comparison.get('change_count', 0),
            'changes': comparison.get('changes', []),
            'summary': AnalysisComparison.format_change_summary(comparison),
            'notifications': [
                AnalysisComparison.format_change_notification(change, asset_symbol)
                for change in comparison.get('changes', [])
                if change.get('significance') in ['HIGH', 'MEDIUM']
            ]
        }
