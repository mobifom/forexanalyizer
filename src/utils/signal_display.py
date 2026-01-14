"""
Signal Display Utilities
Format and display trading signals in Streamlit UI
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime


class SignalDisplayFormatter:
    """Format trading signals for display in UI"""

    @staticmethod
    def format_signals_table(signals: List[Dict]) -> pd.DataFrame:
        """
        Convert list of signals to formatted DataFrame for display

        Args:
            signals: List of signal dictionaries from database

        Returns:
            Formatted DataFrame
        """
        if not signals:
            return pd.DataFrame()

        # Extract relevant fields
        formatted_data = []
        for signal in signals:
            row = {
                'Date': datetime.fromisoformat(signal['created_at']).strftime('%Y-%m-%d %H:%M'),
                'Signal': signal['signal_type'],
                'Strength': signal['strength_category'],
                'Confidence': f"{signal['strength_level']:.1%}",
                'Entry': SignalDisplayFormatter._format_price(signal.get('entry_point_1')),
                'Stop Loss': SignalDisplayFormatter._format_price(signal.get('stop_loss_standard')),
                'Take Profit': SignalDisplayFormatter._format_price(signal.get('take_profit_2')),
                'R:R': SignalDisplayFormatter._format_rr(signal.get('risk_reward_ratio')),
                'Trend': signal.get('trend_direction', '-'),
                'Price': SignalDisplayFormatter._format_price(signal.get('current_price'))
            }
            formatted_data.append(row)

        return pd.DataFrame(formatted_data)

    @staticmethod
    def _format_price(price: Optional[float]) -> str:
        """Format price value"""
        if price is None:
            return '-'
        return f"{price:.5f}"

    @staticmethod
    def _format_rr(ratio: Optional[float]) -> str:
        """Format risk:reward ratio"""
        if ratio is None:
            return '-'
        return f"1:{ratio:.2f}"

    @staticmethod
    def display_signal_table(
        signals: List[Dict],
        timeframe: str,
        title: Optional[str] = None
    ):
        """
        Display signals table in Streamlit

        Args:
            signals: List of signal dictionaries
            timeframe: Timeframe identifier
            title: Optional custom title
        """
        if not signals or len(signals) == 0:
            st.info(f"No recommendations recorded for {timeframe.upper()} timeframe yet")
            return

        # Only show title if provided (to avoid duplication)
        if title:
            st.subheader(title)

        # Convert to DataFrame
        df = SignalDisplayFormatter.format_signals_table(signals)

        if df.empty:
            st.info("No signals to display")
            return

        # Color code signals
        def color_signal(val):
            if val == 'BUY':
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif val == 'SELL':
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            else:
                return ''

        def color_strength(val):
            if val == 'VERY_STRONG':
                return 'background-color: #28a745; color: white; font-weight: bold'
            elif val == 'STRONG':
                return 'background-color: #5cb85c; color: white'
            elif val == 'MODERATE':
                return 'background-color: #ffc107; color: black'
            elif val == 'WEAK':
                return 'background-color: #dc3545; color: white'
            else:
                return ''

        # Apply styling
        styled_df = df.style.applymap(color_signal, subset=['Signal'])
        styled_df = styled_df.applymap(color_strength, subset=['Strength'])

        st.dataframe(styled_df, use_container_width=True, height=400)

        # Display summary stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            buy_count = sum(1 for s in signals if s['signal_type'] == 'BUY')
            st.metric("BUY", buy_count)

        with col2:
            sell_count = sum(1 for s in signals if s['signal_type'] == 'SELL')
            st.metric("SELL", sell_count)

        with col3:
            strong_count = sum(1 for s in signals if s['strength_category'] in ['STRONG', 'VERY_STRONG'])
            st.metric("Strong", strong_count)

        with col4:
            avg_confidence = sum(s['strength_level'] for s in signals) / len(signals)
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")

    @staticmethod
    def display_signal_details(signal: Dict):
        """
        Display detailed information for a single recommendation

        Args:
            signal: Signal dictionary from database
        """
        st.markdown(f"### Recommendation Details")

        # Basic info
        col1, col2, col3 = st.columns(3)

        with col1:
            signal_emoji = "🟢" if signal['signal_type'] == 'BUY' else "🔴"
            st.markdown(f"**Type**: {signal_emoji} {signal['signal_type']}")
            st.markdown(f"**Strength**: {signal['strength_category']}")

        with col2:
            st.markdown(f"**Confidence**: {signal['strength_level']:.1%}")
            st.markdown(f"**Timeframe**: {signal['timeframe'].upper()}")

        with col3:
            created_at = datetime.fromisoformat(signal['created_at'])
            st.markdown(f"**Date**: {created_at.strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**Price**: {signal['current_price']:.5f}")

        st.divider()

        # Entry points
        if signal.get('entry_points_json'):
            import json
            entry_data = json.loads(signal['entry_points_json'])

            st.markdown("#### 📍 Entry Points")
            entry_col1, entry_col2, entry_col3 = st.columns(3)

            with entry_col1:
                ep1 = entry_data.get('entry_1_immediate', {})
                if ep1:
                    st.metric(
                        "Entry 1 (Immediate)",
                        f"{ep1.get('price', 0):.5f}",
                        delta=ep1.get('description', '')
                    )

            with entry_col2:
                ep2 = entry_data.get('entry_2_pullback', {})
                if ep2:
                    st.metric(
                        "Entry 2 (Pullback)",
                        f"{ep2.get('price', 0):.5f}",
                        delta=ep2.get('description', '')
                    )

            with entry_col3:
                ep3 = entry_data.get('entry_3_aggressive', {})
                if ep3:
                    st.metric(
                        "Entry 3 (Aggressive)",
                        f"{ep3.get('price', 0):.5f}",
                        delta=ep3.get('description', '')
                    )

        st.divider()

        # Take profits & Stop losses
        col_tp, col_sl = st.columns(2)

        with col_tp:
            st.markdown("#### 🎯 Take Profit Levels")
            if signal.get('take_profits_json'):
                import json
                tp_data = json.loads(signal['take_profits_json'])

                tp1 = tp_data.get('tp1_quick', {})
                if tp1:
                    st.success(f"**TP1 (Quick)**: {tp1.get('price', 0):.5f}")

                tp2 = tp_data.get('tp2_conservative', {})
                if tp2:
                    st.success(f"**TP2 (Conservative)**: {tp2.get('price', 0):.5f}")

                tp3 = tp_data.get('tp3_extended', {})
                if tp3:
                    st.success(f"**TP3 (Extended)**: {tp3.get('price', 0):.5f}")

        with col_sl:
            st.markdown("#### 🛡️ Stop Loss Levels")
            if signal.get('stop_losses_json'):
                import json
                sl_data = json.loads(signal['stop_losses_json'])

                sl1 = sl_data.get('tight_1atr', {})
                if sl1:
                    st.error(f"**SL Tight (1 ATR)**: {sl1.get('price', 0):.5f}")

                sl2 = sl_data.get('standard_2atr', {})
                if sl2:
                    st.error(f"**SL Standard (2 ATR)**: {sl2.get('price', 0):.5f}")

                sl3 = sl_data.get('wide_3atr', {})
                if sl3:
                    st.error(f"**SL Wide (3 ATR)**: {sl3.get('price', 0):.5f}")

        st.divider()

        # Risk metrics & Context
        col_risk, col_context = st.columns(2)

        with col_risk:
            st.markdown("#### 📊 Risk Metrics")
            if signal.get('risk_reward_ratio'):
                st.info(f"**Risk:Reward Ratio**: 1:{signal['risk_reward_ratio']:.2f}")
            if signal.get('risk_percentage'):
                st.info(f"**Risk Percentage**: {signal['risk_percentage']:.2f}%")

        with col_context:
            st.markdown("#### 🔍 Market Context")
            st.info(f"**Trend**: {signal.get('trend_direction', 'N/A')}")
            st.info(f"**Momentum**: {signal.get('momentum', 'N/A')}")
            if signal.get('reversal_detected'):
                st.warning(f"⚠️ **Reversal Detected**: {signal.get('reversal_type', 'Unknown')}")

    @staticmethod
    def create_signals_summary_card(
        signals_by_timeframe: Dict[str, List[Dict]],
        asset_symbol: str
    ):
        """
        Create a summary card showing recommendation counts by timeframe

        Args:
            signals_by_timeframe: Dictionary mapping timeframe to signals list
            asset_symbol: Asset symbol
        """
        st.markdown(f"### 📊 Signal History for {asset_symbol}")
        st.caption("Showing last 20 signals per timeframe")

        if not signals_by_timeframe:
            st.info("No recommendations recorded yet. Run an analysis to generate recommendations.")
            return

        # Create summary table
        summary_data = []
        for tf in ['15m', '1h', '4h', '1d']:
            if tf in signals_by_timeframe:
                signals = signals_by_timeframe[tf]
                buy_count = sum(1 for s in signals if s['signal_type'] == 'BUY')
                sell_count = sum(1 for s in signals if s['signal_type'] == 'SELL')
                latest_signal = signals[0] if signals else None

                summary_data.append({
                    'Timeframe': tf.upper(),
                    'Total Recommendations': len(signals),
                    'BUY': buy_count,
                    'SELL': sell_count,
                    'Latest': latest_signal['signal_type'] if latest_signal else '-',
                    'Date': datetime.fromisoformat(latest_signal['created_at']).strftime('%Y-%m-%d') if latest_signal else '-'
                })

        if summary_data:
            summary_df = pd.DataFrame(summary_data)

            # Color code latest recommendation
            def color_latest_signal(val):
                if val == 'BUY':
                    return 'background-color: #d4edda; color: #155724'
                elif val == 'SELL':
                    return 'background-color: #f8d7da; color: #721c24'
                else:
                    return ''

            styled_summary = summary_df.style.applymap(color_latest_signal, subset=['Latest'])
            st.dataframe(styled_summary, use_container_width=True)
