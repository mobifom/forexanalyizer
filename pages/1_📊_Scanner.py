"""
Multi-Pair Scanner Page
Scan multiple currency pairs and metals simultaneously
"""

import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.forex_analyzer import ForexAnalyzer
from src.auth.authentication_db import AuthenticatorDB, Permissions
from src.utils.opportunities import add_opportunities_to_session
from src.database.signals_db import SignalsDB
from src.database.analysis_db import AnalysisDB
from src.utils.signal_display import SignalDisplayFormatter
from datetime import datetime, timedelta

st.set_page_config(page_title="Multi-Pair Scanner", page_icon="📊", layout="wide")

# Check authentication with database
if 'auth' not in st.session_state:
    st.session_state.auth = AuthenticatorDB()

auth = st.session_state.auth

if not auth.is_authenticated():
    st.error("🔒 Please login first")
    st.info("Return to the main page to login")
    st.stop()

if not auth.has_permission(Permissions.SCAN_PAIRS):
    st.error("🔒 You don't have permission to scan pairs")
    st.stop()

# Render user info in sidebar
auth.render_user_info()

st.title("📊 Multi-Pair Scanner")
st.markdown("Scan multiple assets simultaneously to find the best trading opportunities")

# Initialize
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ForexAnalyzer()

# Initialize signals database
if 'signals_db' not in st.session_state:
    st.session_state.signals_db = SignalsDB('data/signals.db')

# Initialize analysis database
if 'analysis_db' not in st.session_state:
    st.session_state.analysis_db = AnalysisDB('data/analysis.db')

# Sidebar
with st.sidebar:
    st.header("Scanner Settings")

    # Preset selections
    scan_type = st.radio(
        "Quick Select",
        ["Forex Major Pairs", "Indices", "Crypto", "Precious Metals", "All Assets", "Custom"]
    )

    if scan_type == "Forex Major Pairs":
        selected_symbols = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X']
    elif scan_type == "Indices":
        selected_symbols = ['US30', 'US100']
    elif scan_type == "Crypto":
        selected_symbols = ['BTC/USD', 'ETH/USD']
    elif scan_type == "Precious Metals":
        selected_symbols = ['XAU_USD', 'XAG_USD']
    elif scan_type == "All Assets":
        selected_symbols = [
            'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X',
            'XAU_USD', 'XAG_USD',
            'US30', 'US100',
            'BTC/USD', 'ETH/USD'
        ]
    else:
        # Custom selection
        available_symbols = {
            '💱 Forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCHF=X', 'NZDUSD=X', 'USDCAD=X'],
            '📊 Indices': ['US30', 'US100'],
            '₿ Crypto': ['BTC/USD', 'ETH/USD'],
            '🥇 Metals': ['XAU_USD', 'XAG_USD']
        }

        selected_symbols = []
        for category, symbols in available_symbols.items():
            st.markdown(f"**{category}**")
            for symbol in symbols:
                display_name = symbol
                if symbol == 'US30':
                    display_name = 'US30 (Dow Jones)'
                elif symbol == 'US100':
                    display_name = 'US100 (NASDAQ 100)'
                elif symbol == 'BTC/USD':
                    display_name = 'BTC/USD (Bitcoin)'
                elif symbol == 'ETH/USD':
                    display_name = 'ETH/USD (Ethereum)'

                if st.checkbox(display_name, key=symbol):
                    selected_symbols.append(symbol)

    st.divider()

    # Timeframe selection
    st.subheader("⏰ Timeframes")
    timeframe_mode = st.radio(
        "View Mode",
        ["Multi-Timeframe View", "Single Timeframe"],
        help="Choose to see all timeframes or focus on one"
    )

    if timeframe_mode == "Single Timeframe":
        selected_timeframe = st.selectbox(
            "Select Timeframe",
            ["15m", "1h", "4h", "1d"],
            index=3,  # Default to 1d
            help="Choose which timeframe to analyze"
        )
    else:
        selected_timeframe = None

    st.divider()

    account_balance = st.number_input(
        "Account Balance ($)",
        min_value=100,
        value=10000,
        step=100
    )

    use_ml = st.checkbox("Use ML Model", value=True)

    # Advanced Settings (Collapsible)
    with st.expander("⚙️ Advanced Settings", expanded=False):
        st.markdown("**Signal Quality**")

        min_timeframes = st.slider(
            "Min Timeframes",
            min_value=1,
            max_value=4,
            value=st.session_state.analyzer.config.get('confluence', {}).get('min_timeframes_agree', 2),
            key='scanner_min_tf'
        )

        min_confidence = st.slider(
            "Min Confidence",
            min_value=0.3,
            max_value=0.8,
            value=st.session_state.analyzer.config.get('confluence', {}).get('min_confidence', 0.5),
            step=0.05,
            format="%.0f%%",
            key='scanner_min_conf'
        )

        st.markdown("**Quick Presets**")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🛡️ Safe", key='scanner_conservative', use_container_width=True):
                min_timeframes = 3
                min_confidence = 0.6

        with col2:
            if st.button("⚖️ Balanced", key='scanner_balanced', use_container_width=True):
                min_timeframes = 2
                min_confidence = 0.5

        with col3:
            if st.button("🚀 Aggressive", key='scanner_aggressive', use_container_width=True):
                min_timeframes = 1
                min_confidence = 0.4

        # Update config
        st.session_state.analyzer.config['confluence']['min_timeframes_agree'] = min_timeframes
        st.session_state.analyzer.config['confluence']['min_confidence'] = min_confidence

    scan_button = st.button("🔍 Scan All", type="primary", use_container_width=True)

    # Refresh button (admin only)
    if auth.has_permission(Permissions.REFRESH_DATA):
        refresh_all_button = st.button("🔄 Refresh All Data", use_container_width=True,
                                       help="Clear cache and fetch fresh data for all selected symbols")
    else:
        refresh_all_button = False

# Handle refresh all button
if refresh_all_button:
    if not selected_symbols:
        st.warning("Please select at least one symbol to refresh")
    else:
        st.info(f"Refreshing data for {len(selected_symbols)} symbols...")

        import shutil
        from src.data.data_fetcher import ForexDataFetcher

        fetcher = ForexDataFetcher()
        cache_dir = 'data/cache'

        # Clear cache for selected symbols
        if os.path.exists(cache_dir):
            for symbol in selected_symbols:
                symbol_clean = symbol.replace('=', '_').replace('/', '_')
                for file in os.listdir(cache_dir):
                    if symbol_clean in file:
                        try:
                            os.remove(os.path.join(cache_dir, file))
                        except:
                            pass

        # Clear in-memory cache for selected symbols
        for symbol in selected_symbols:
            if fetcher.memory_cache:
                fetcher.memory_cache.invalidate(symbol=symbol)

        # Fetch fresh data for each symbol
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, symbol in enumerate(selected_symbols):
            status_text.text(f"Fetching fresh data for {symbol}... (bypassing cache)")

            try:
                for tf in ['1d', '4h', '1h', '15m']:
                    # Use use_cache=True but cache is already invalidated, so it will fetch fresh
                    # and then cache the new data for future use
                    df = fetcher.fetch_data(symbol, tf, use_cache=True, use_snapshot=False)
                    if df is not None and len(df) > 0:
                        # Data is now cached for future use
                        pass
                st.success(f"✅ {symbol} - Fresh data fetched and cached")
            except Exception as e:
                st.error(f"❌ {symbol} - Error: {str(e)}")

            progress_bar.progress((idx + 1) / len(selected_symbols))

        # Show final cache stats
        cache_stats = st.session_state.analyzer.get_cache_stats()
        status_text.text(f"✅ All data refreshed! Cache: {cache_stats.get('fresh_entries', 0)} entries")
        st.success("Ready to scan with latest market data!")

# Main content
if scan_button:
    if not selected_symbols:
        st.warning("Please select at least one symbol to scan")
    else:
        st.info(f"Scanning {len(selected_symbols)} symbols...")

        results = []

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, symbol in enumerate(selected_symbols):
            # Get cache stats before analysis
            cache_stats_before = st.session_state.analyzer.get_cache_stats()
            fresh_before = cache_stats_before.get('fresh_entries', 0)

            status_text.text(f"Analyzing {symbol}... ⚡ Using cached data")

            try:
                analysis = st.session_state.analyzer.analyze_pair(
                    symbol=symbol,
                    account_balance=account_balance,
                    use_ml=use_ml
                )

                # Check if data was served from cache
                cache_stats_after = st.session_state.analyzer.get_cache_stats()
                fresh_after = cache_stats_after.get('fresh_entries', 0)

                if fresh_after == fresh_before + 4:  # All 4 timeframes were fetched fresh
                    cache_status = "🔄 Fresh data fetched"
                elif fresh_after > fresh_before:
                    cache_status = f"⚡ Partial cache ({fresh_after - fresh_before} fresh)"
                else:
                    cache_status = "⚡ Served from cache (instant)"

                # Extract and store opportunities
                if 'error' not in analysis:
                    add_opportunities_to_session(st.session_state, symbol, analysis)

                    # Show cache status as success message
                    if 'cache_status' in locals():
                        st.success(f"✅ {symbol} - {cache_status}")

                if 'error' not in analysis:
                    if timeframe_mode == "Multi-Timeframe View":
                        # Collect data for each timeframe
                        tf_analyses = analysis.get('timeframe_analyses', {})

                        for tf in ['15m', '1h', '4h', '1d']:
                            if tf in tf_analyses:
                                tf_data = tf_analyses[tf]
                                tf_signal_data = tf_data.get('signals', {})

                                # Get signals for this timeframe
                                tf_signals = []
                                for sig_type, sig_val in tf_signal_data.items():
                                    if sig_val in ['BUY', 'SELL', 'HOLD']:
                                        tf_signals.append(sig_val)

                                # Determine overall signal for this timeframe
                                buy_count = tf_signals.count('BUY')
                                sell_count = tf_signals.count('SELL')

                                if buy_count > sell_count:
                                    tf_signal = 'BUY'
                                elif sell_count > buy_count:
                                    tf_signal = 'SELL'
                                else:
                                    tf_signal = 'HOLD'

                                # Get multi-TF trade plan for this timeframe
                                mtf_plans = analysis.get('multi_tf_trade_plans', {})
                                tf_plan = None
                                if mtf_plans and mtf_plans.get('approved'):
                                    tf_plan = mtf_plans.get('timeframe_plans', {}).get(tf)

                                result = {
                                    'Symbol': symbol,
                                    'Timeframe': tf.upper(),
                                    'Signal': tf_signal,
                                    'Price': analysis['current_price'],
                                    'RSI': tf_data.get('dataframe', pd.DataFrame()).get('RSI', pd.Series()).iloc[-1] if not tf_data.get('dataframe', pd.DataFrame()).empty else None,
                                    'Trend': tf_signal_data.get('ma_signal', '-'),
                                    'Momentum': tf_signal_data.get('macd_signal', '-')
                                }

                                # Add trade plan details if available
                                if tf_plan:
                                    # Get recommended entries/stops/targets
                                    entry_imm = tf_plan['entry_points'].get('entry_1_immediate', {})
                                    sl_std = tf_plan['stop_losses'].get('standard_2atr', {})
                                    tp_rec = tf_plan['take_profits'].get('tp2_conservative', {})

                                    result['Entry'] = entry_imm.get('price')
                                    result['Stop Loss'] = sl_std.get('price')
                                    result['Take Profit'] = tp_rec.get('price')
                                    result['Risk %'] = sl_std.get('risk_pct')
                                    result['R:R'] = tf_plan['risk_reward_ratios'].get('tp2_conservative', 'N/A')
                                    result['Duration'] = tf_plan['expected_execution'].get('duration_readable', 'N/A')
                                else:
                                    result['Entry'] = None
                                    result['Stop Loss'] = None
                                    result['Take Profit'] = None
                                    result['Risk %'] = None
                                    result['R:R'] = None
                                    result['Duration'] = None

                                results.append(result)

                    else:
                        # Single timeframe mode
                        tf = selected_timeframe
                        tf_analyses = analysis.get('timeframe_analyses', {})

                        if tf in tf_analyses:
                            tf_data = tf_analyses[tf]
                            tf_signal_data = tf_data.get('signals', {})

                            # Get signals for this timeframe
                            tf_signals = []
                            for sig_type, sig_val in tf_signal_data.items():
                                if sig_val in ['BUY', 'SELL', 'HOLD']:
                                    tf_signals.append(sig_val)

                            # Determine overall signal for this timeframe
                            buy_count = tf_signals.count('BUY')
                            sell_count = tf_signals.count('SELL')

                            if buy_count > sell_count:
                                tf_signal = 'BUY'
                            elif sell_count > buy_count:
                                tf_signal = 'SELL'
                            else:
                                tf_signal = 'HOLD'

                            # Get multi-TF trade plan for this timeframe
                            mtf_plans = analysis.get('multi_tf_trade_plans', {})
                            tf_plan = None
                            if mtf_plans and mtf_plans.get('approved'):
                                tf_plan = mtf_plans.get('timeframe_plans', {}).get(tf)

                            result = {
                                'Symbol': symbol,
                                'Signal': tf_signal,
                                'Price': analysis['current_price'],
                                'RSI': tf_data.get('dataframe', pd.DataFrame()).get('RSI', pd.Series()).iloc[-1] if not tf_data.get('dataframe', pd.DataFrame()).empty else None,
                                'Trend': tf_signal_data.get('ma_signal', '-'),
                                'Momentum': tf_signal_data.get('macd_signal', '-')
                            }

                            # Add trade plan details if available
                            if tf_plan:
                                # Get recommended entries/stops/targets
                                entry_imm = tf_plan['entry_points'].get('entry_1_immediate', {})
                                sl_std = tf_plan['stop_losses'].get('standard_2atr', {})
                                tp_rec = tf_plan['take_profits'].get('tp2_conservative', {})

                                result['Entry'] = entry_imm.get('price')
                                result['Stop Loss'] = sl_std.get('price')
                                result['Take Profit'] = tp_rec.get('price')
                                result['Risk %'] = sl_std.get('risk_pct')
                                result['R:R'] = tf_plan['risk_reward_ratios'].get('tp2_conservative', 'N/A')
                                result['Duration'] = tf_plan['expected_execution'].get('duration_readable', 'N/A')
                            else:
                                result['Entry'] = None
                                result['Stop Loss'] = None
                                result['Take Profit'] = None
                                result['Risk %'] = None
                                result['R:R'] = None
                                result['Duration'] = None

                            results.append(result)

            except Exception as e:
                st.error(f"Error analyzing {symbol}: {str(e)}")

            progress_bar.progress((idx + 1) / len(selected_symbols))

        status_text.empty()
        progress_bar.empty()

        # Display results
        if results:
            df = pd.DataFrame(results)

            if timeframe_mode == "Multi-Timeframe View":
                st.success(f"✅ Scan complete! Analyzed {len(selected_symbols)} symbols across {len(df)} timeframe entries")

                # Show opportunities notification
                if 'opportunities' in st.session_state and len(st.session_state.opportunities) > 0:
                    total_opps = len(st.session_state.opportunities)
                    st.info(f"🎯 {total_opps} trading opportunities available - Check the **🎯 Opportunities** page!")

                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    buy_count = len(df[df['Signal'] == 'BUY'])
                    st.metric("BUY Signals", buy_count)

                with col2:
                    sell_count = len(df[df['Signal'] == 'SELL'])
                    st.metric("SELL Signals", sell_count)

                with col3:
                    hold_count = len(df[df['Signal'] == 'HOLD'])
                    st.metric("HOLD Signals", hold_count)

                with col4:
                    total_entries = len(df)
                    st.metric("Total Entries", total_entries)
            else:
                st.success(f"✅ Scan complete! Analyzed {len(results)} symbols on {selected_timeframe.upper()} timeframe")

                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    buy_count = len(df[df['Signal'] == 'BUY'])
                    st.metric("BUY Signals", buy_count)

                with col2:
                    sell_count = len(df[df['Signal'] == 'SELL'])
                    st.metric("SELL Signals", sell_count)

                with col3:
                    hold_count = len(df[df['Signal'] == 'HOLD'])
                    st.metric("HOLD Signals", hold_count)

                with col4:
                    avg_rsi = df['RSI'].mean() if 'RSI' in df.columns and not df['RSI'].isna().all() else 0
                    st.metric("Avg RSI", f"{avg_rsi:.1f}" if avg_rsi else "N/A")

            # Tabs for different views
            if timeframe_mode == "Multi-Timeframe View":
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔥 Heatmap", "🎯 BUY Signals", "🔴 SELL Signals"])
            else:
                tab1, tab2, tab3 = st.tabs(["📊 Overview", "🎯 BUY Signals", "🔴 SELL Signals"])

            with tab1:
                st.subheader("All Scan Results")

                # Color code signals
                def color_signal(val):
                    if val == 'BUY':
                        return 'background-color: #d4edda; color: #155724'
                    elif val == 'SELL':
                        return 'background-color: #f8d7da; color: #721c24'
                    else:
                        return 'background-color: #fff3cd; color: #856404'

                # Custom formatter that handles None values
                def safe_format(val, format_str):
                    if pd.isna(val) or val is None:
                        return '-'
                    return format_str.format(val)

                if timeframe_mode == "Multi-Timeframe View":
                    # Show timeframe in the display
                    styled_df = df.style.applymap(color_signal, subset=['Signal'])

                    # Apply formatting with None handling
                    format_dict = {}
                    if 'Price' in df.columns:
                        format_dict['Price'] = lambda x: safe_format(x, '{:.5f}')
                    if 'RSI' in df.columns:
                        format_dict['RSI'] = lambda x: safe_format(x, '{:.1f}')
                    if 'Risk %' in df.columns:
                        format_dict['Risk %'] = lambda x: safe_format(x, '{:.2f}%')
                    if 'Entry' in df.columns:
                        format_dict['Entry'] = lambda x: safe_format(x, '{:.5f}')
                    if 'Stop Loss' in df.columns:
                        format_dict['Stop Loss'] = lambda x: safe_format(x, '{:.5f}')
                    if 'Take Profit' in df.columns:
                        format_dict['Take Profit'] = lambda x: safe_format(x, '{:.5f}')

                    st.dataframe(
                        styled_df.format(format_dict),
                        use_container_width=True
                    )
                else:
                    styled_df = df.style.applymap(color_signal, subset=['Signal'])

                    # Apply formatting with None handling
                    format_dict = {}
                    if 'Price' in df.columns:
                        format_dict['Price'] = lambda x: safe_format(x, '{:.5f}')
                    if 'RSI' in df.columns:
                        format_dict['RSI'] = lambda x: safe_format(x, '{:.1f}')
                    if 'Risk %' in df.columns:
                        format_dict['Risk %'] = lambda x: safe_format(x, '{:.2f}%')
                    if 'Entry' in df.columns:
                        format_dict['Entry'] = lambda x: safe_format(x, '{:.5f}')
                    if 'Stop Loss' in df.columns:
                        format_dict['Stop Loss'] = lambda x: safe_format(x, '{:.5f}')
                    if 'Take Profit' in df.columns:
                        format_dict['Take Profit'] = lambda x: safe_format(x, '{:.5f}')

                    st.dataframe(
                        styled_df.format(format_dict),
                        use_container_width=True
                    )

            if timeframe_mode == "Multi-Timeframe View":
                with tab2:
                    st.subheader("🔥 Multi-Timeframe Heatmap")
                    st.markdown("Visual representation of signals across all timeframes")

                    # Create pivot table for heatmap
                    heatmap_data = df.pivot_table(
                        index='Symbol',
                        columns='Timeframe',
                        values='Signal',
                        aggfunc='first'
                    )

                    # Convert signals to numeric for coloring
                    signal_map = {'BUY': 1, 'HOLD': 0, 'SELL': -1}
                    heatmap_numeric = heatmap_data.applymap(lambda x: signal_map.get(x, 0) if pd.notna(x) else 0)

                    # Create heatmap using plotly
                    import plotly.graph_objects as go

                    fig = go.Figure(data=go.Heatmap(
                        z=heatmap_numeric.values,
                        x=heatmap_numeric.columns,
                        y=heatmap_numeric.index,
                        colorscale=[
                            [0, '#f8d7da'],    # SELL - Red
                            [0.5, '#fff3cd'],  # HOLD - Yellow
                            [1, '#d4edda']     # BUY - Green
                        ],
                        text=heatmap_data.values,
                        texttemplate='%{text}',
                        textfont={"size": 12},
                        colorbar=dict(
                            title="Signal",
                            tickvals=[-1, 0, 1],
                            ticktext=['SELL', 'HOLD', 'BUY']
                        ),
                        hoverongaps=False
                    ))

                    fig.update_layout(
                        title="Signal Heatmap Across Timeframes",
                        xaxis_title="Timeframe",
                        yaxis_title="Symbol",
                        height=400 + (len(heatmap_data.index) * 30),
                        yaxis_autorange='reversed'
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Show strongest signals
                    st.markdown("### 💪 Strongest Signals")
                    st.markdown("*Pairs with consistent signals across multiple timeframes*")

                    # Count BUY/SELL per symbol
                    signal_strength = df.groupby('Symbol')['Signal'].value_counts().unstack(fill_value=0)

                    if 'BUY' in signal_strength.columns:
                        strong_buys = signal_strength.sort_values('BUY', ascending=False)
                        st.markdown("**🟢 Strong BUY Candidates:**")
                        for symbol, row in strong_buys.head(3).iterrows():
                            if row.get('BUY', 0) >= 2:
                                st.success(f"**{symbol}**: {int(row['BUY'])} timeframes showing BUY")

                    if 'SELL' in signal_strength.columns:
                        strong_sells = signal_strength.sort_values('SELL', ascending=False)
                        st.markdown("**🔴 Strong SELL Candidates:**")
                        for symbol, row in strong_sells.head(3).iterrows():
                            if row.get('SELL', 0) >= 2:
                                st.error(f"**{symbol}**: {int(row['SELL'])} timeframes showing SELL")

            # BUY Signals tab
            buy_tab = tab3 if timeframe_mode == "Multi-Timeframe View" else tab2
            with buy_tab:
                buy_df = df[df['Signal'] == 'BUY']

                if len(buy_df) > 0:
                    st.subheader(f"🟢 {len(buy_df)} BUY Opportunities")

                    if timeframe_mode == "Multi-Timeframe View":
                        # Group by symbol
                        for symbol in buy_df['Symbol'].unique():
                            symbol_df = buy_df[buy_df['Symbol'] == symbol]
                            timeframes_str = ", ".join(symbol_df['Timeframe'].tolist())

                            with st.expander(f"{symbol} - BUY on {timeframes_str}"):
                                for idx, row in symbol_df.iterrows():
                                    st.markdown(f"**{row['Timeframe']} Timeframe**")
                                    col1, col2, col3, col4 = st.columns(4)

                                    with col1:
                                        st.metric("Price", f"${row['Price']:.5f}")
                                        if pd.notna(row.get('RSI')):
                                            st.metric("RSI", f"{row['RSI']:.1f}")

                                    with col2:
                                        if pd.notna(row.get('Entry')):
                                            st.metric("Entry", f"${row['Entry']:.5f}")
                                        if pd.notna(row.get('Duration')):
                                            st.caption(f"⏱️ {row['Duration']}")

                                    with col3:
                                        if pd.notna(row.get('Stop Loss')):
                                            st.metric("Stop Loss", f"${row['Stop Loss']:.5f}")
                                        if pd.notna(row.get('Risk %')):
                                            st.caption(f"Risk: {row['Risk %']:.2f}%")

                                    with col4:
                                        if pd.notna(row.get('Take Profit')):
                                            st.metric("Take Profit", f"${row['Take Profit']:.5f}")
                                        if pd.notna(row.get('R:R')) and row.get('R:R') != 'N/A':
                                            st.caption(f"R:R 1:{row['R:R']}")

                                    st.divider()
                    else:
                        # Single timeframe mode
                        for idx, row in buy_df.iterrows():
                            with st.expander(f"{row['Symbol']} - {row['Signal']}"):
                                col1, col2, col3, col4 = st.columns(4)

                                with col1:
                                    st.metric("Price", f"${row['Price']:.5f}")
                                    if pd.notna(row.get('RSI')):
                                        st.metric("RSI", f"{row['RSI']:.1f}")

                                with col2:
                                    if pd.notna(row.get('Entry')):
                                        st.metric("Entry", f"${row['Entry']:.5f}")
                                    if pd.notna(row.get('Duration')):
                                        st.caption(f"⏱️ {row['Duration']}")

                                with col3:
                                    if pd.notna(row.get('Stop Loss')):
                                        st.metric("Stop Loss", f"${row['Stop Loss']:.5f}")
                                    if pd.notna(row.get('Risk %')):
                                        st.caption(f"Risk: {row['Risk %']:.2f}%")

                                with col4:
                                    if pd.notna(row.get('Take Profit')):
                                        st.metric("Take Profit", f"${row['Take Profit']:.5f}")
                                    if pd.notna(row.get('R:R')) and row.get('R:R') != 'N/A':
                                        st.caption(f"R:R 1:{row['R:R']}")
                else:
                    st.info("No BUY signals found in this scan")

            # SELL Signals tab
            sell_tab = tab4 if timeframe_mode == "Multi-Timeframe View" else tab3
            with sell_tab:
                sell_df = df[df['Signal'] == 'SELL']

                if len(sell_df) > 0:
                    st.subheader(f"🔴 {len(sell_df)} SELL Opportunities")

                    if timeframe_mode == "Multi-Timeframe View":
                        # Group by symbol
                        for symbol in sell_df['Symbol'].unique():
                            symbol_df = sell_df[sell_df['Symbol'] == symbol]
                            timeframes_str = ", ".join(symbol_df['Timeframe'].tolist())

                            with st.expander(f"{symbol} - SELL on {timeframes_str}"):
                                for idx, row in symbol_df.iterrows():
                                    st.markdown(f"**{row['Timeframe']} Timeframe**")
                                    col1, col2, col3, col4 = st.columns(4)

                                    with col1:
                                        st.metric("Price", f"${row['Price']:.5f}")
                                        if pd.notna(row.get('RSI')):
                                            st.metric("RSI", f"{row['RSI']:.1f}")

                                    with col2:
                                        if pd.notna(row.get('Entry')):
                                            st.metric("Entry", f"${row['Entry']:.5f}")
                                        if pd.notna(row.get('Duration')):
                                            st.caption(f"⏱️ {row['Duration']}")

                                    with col3:
                                        if pd.notna(row.get('Stop Loss')):
                                            st.metric("Stop Loss", f"${row['Stop Loss']:.5f}")
                                        if pd.notna(row.get('Risk %')):
                                            st.caption(f"Risk: {row['Risk %']:.2f}%")

                                    with col4:
                                        if pd.notna(row.get('Take Profit')):
                                            st.metric("Take Profit", f"${row['Take Profit']:.5f}")
                                        if pd.notna(row.get('R:R')) and row.get('R:R') != 'N/A':
                                            st.caption(f"R:R 1:{row['R:R']}")

                                    st.divider()
                    else:
                        # Single timeframe mode
                        for idx, row in sell_df.iterrows():
                            with st.expander(f"{row['Symbol']} - {row['Signal']}"):
                                col1, col2, col3, col4 = st.columns(4)

                                with col1:
                                    st.metric("Price", f"${row['Price']:.5f}")
                                    if pd.notna(row.get('RSI')):
                                        st.metric("RSI", f"{row['RSI']:.1f}")

                                with col2:
                                    if pd.notna(row.get('Entry')):
                                        st.metric("Entry", f"${row['Entry']:.5f}")
                                    if pd.notna(row.get('Duration')):
                                        st.caption(f"⏱️ {row['Duration']}")

                                with col3:
                                    if pd.notna(row.get('Stop Loss')):
                                        st.metric("Stop Loss", f"${row['Stop Loss']:.5f}")
                                    if pd.notna(row.get('Risk %')):
                                        st.caption(f"Risk: {row['Risk %']:.2f}%")

                                with col4:
                                    if pd.notna(row.get('Take Profit')):
                                        st.metric("Take Profit", f"${row['Take Profit']:.5f}")
                                    if pd.notna(row.get('R:R')) and row.get('R:R') != 'N/A':
                                        st.caption(f"R:R 1:{row['R:R']}")
                else:
                    st.info("No SELL signals found in this scan")

else:
    st.info("👈 Select symbols from the sidebar and click **Scan All** to begin")

# V2 Recommendations Section
st.divider()
st.header("🎯 V2 Recommendations")

# Show active filters
filter_text = f"**Filters**: Asset Type: {scan_type}"
if timeframe_mode == "Single Timeframe":
    filter_text += f" | Timeframe: {selected_timeframe.upper()}"
else:
    filter_text += f" | Timeframe: All"
st.markdown(filter_text)

# Check if database has any signals
all_available_signals = st.session_state.signals_db.get_signals(limit=1, active_only=True)
if all_available_signals:
    total_signals = st.session_state.signals_db.get_stats().get('total_active_signals', 0)
    st.success(f"✅ Database contains {total_signals} active recommendation(s). Select assets from sidebar to view.")
else:
    st.warning("⚠️ No recommendations in database yet. Run an analysis first.")

st.markdown("---")

# Determine which assets to display based on sidebar
assets_to_display = []

if selected_symbols and len(selected_symbols) > 0:
    # Use sidebar selections
    assets_to_display = selected_symbols
    st.info(f"📊 Showing recommendations for {len(selected_symbols)} selected asset(s)")
else:
    # No sidebar selection - find all assets with stored data
    all_symbols = [
        'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCHF=X', 'NZDUSD=X', 'USDCAD=X',
        'XAU_USD', 'XAG_USD',
        'US30', 'US100',
        'BTC/USD', 'ETH/USD'
    ]

    # Filter to only show assets with stored data
    for symbol in all_symbols:
        signals = st.session_state.signals_db.get_signals(
            asset_symbol=symbol,
            limit=1,
            active_only=True
        )
        if signals:
            assets_to_display.append(symbol)

    if assets_to_display:
        st.info(f"📊 Showing all assets with stored recommendations ({len(assets_to_display)} found)")
    else:
        st.warning("⚠️ No stored recommendations found. Run an analysis first.")

# Display recommendations for each asset
if assets_to_display:
    for idx, asset_symbol in enumerate(assets_to_display):
        with st.container():
            st.subheader(f"📈 {asset_symbol}")

            # Get signals based on timeframe mode
            if timeframe_mode == "Single Timeframe" and selected_timeframe:
                # Single timeframe - filter by selected timeframe
                signals = st.session_state.signals_db.get_signals(
                    asset_symbol=asset_symbol,
                    timeframe=selected_timeframe,
                    limit=20,
                    active_only=True
                )

                if signals:
                    signals_by_tf = {selected_timeframe: signals}
                else:
                    signals_by_tf = {}
            else:
                # Multi-timeframe - get all timeframes
                signals_by_tf = st.session_state.signals_db.get_signals_by_timeframe(
                    asset_symbol=asset_symbol,
                    limit_per_timeframe=20,
                    active_only=True
                )

            # Display summary card
            if signals_by_tf:
                SignalDisplayFormatter.create_signals_summary_card(signals_by_tf, asset_symbol)
                st.divider()

                # Create tabs for each timeframe
                available_tfs = list(signals_by_tf.keys())

                if len(available_tfs) == 1:
                    # Single timeframe - display directly
                    tf = available_tfs[0]
                    signal_count = len(signals_by_tf[tf])
                    st.markdown(f"**{tf.upper()} Timeframe** - Showing Last {signal_count} Signal{'s' if signal_count != 1 else ''} (max 20)")

                    # Display the signal table
                    SignalDisplayFormatter.display_signal_table(
                        signals_by_tf[tf],
                        tf,
                        None  # No custom title, using markdown above
                    )

                    # Show detailed view for most recent recommendation
                    if signals_by_tf[tf]:
                        with st.expander("📋 View Latest Recommendation Details", expanded=False):
                            SignalDisplayFormatter.display_signal_details(signals_by_tf[tf][0])
                else:
                    # Multiple timeframes - use tabs
                    tab_labels = [f"{tf.upper()} - Last {len(signals_by_tf[tf])} signals" for tf in available_tfs]
                    tabs = st.tabs(tab_labels)

                    for tf_idx, tf in enumerate(available_tfs):
                        with tabs[tf_idx]:
                            signal_count = len(signals_by_tf[tf])
                            st.caption(f"Showing last {signal_count} signal{'s' if signal_count != 1 else ''} (max 20 per timeframe)")

                            # Display the signal table
                            SignalDisplayFormatter.display_signal_table(
                                signals_by_tf[tf],
                                tf,
                                None  # Title shown in tab
                            )

                            # Show detailed view for most recent recommendation
                            if signals_by_tf[tf]:
                                with st.expander("📋 View Latest Recommendation Details", expanded=False):
                                    SignalDisplayFormatter.display_signal_details(signals_by_tf[tf][0])
            else:
                # No signals found
                if timeframe_mode == "Single Timeframe" and selected_timeframe:
                    st.info(f"💡 No recommendations for {asset_symbol} on **{selected_timeframe.upper()}** timeframe. Try a different timeframe or run analysis.")
                else:
                    st.info(f"💡 No recommendations for {asset_symbol}. Run an analysis to generate recommendations.")

            # Add spacing between assets
            if idx < len(assets_to_display) - 1:
                st.markdown("---")
else:
    # This message only shows if assets_to_display is empty but we already showed warning above
    pass

st.divider()

# ============================================================================
# 📈 ANALYSIS HISTORY SECTION
# ============================================================================

st.header("📈 Analysis History")
st.markdown("View historical analysis results stored in the database")

# Get database stats
analysis_stats = st.session_state.analysis_db.get_stats()
total_analyses = analysis_stats.get('total_analyses', 0)
latest_analyses = analysis_stats.get('latest_analyses', 0)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Analyses Stored", total_analyses)
with col2:
    st.metric("Current (Latest) Analyses", latest_analyses)
with col3:
    changes_24h = analysis_stats.get('recent_changes_24h', 0)
    st.metric("Changes in Last 24h", changes_24h)

if total_analyses > 0:
    # Filters
    st.subheader("🔍 Filters")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Get all assets that have analyses
        conn = st.session_state.analysis_db._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT asset_symbol FROM analysis_results ORDER BY asset_symbol')
        available_assets = [row[0] for row in cursor.fetchall()]
        conn.close()

        filter_asset = st.selectbox(
            "Select Asset",
            ["All Assets"] + available_assets,
            key="history_asset_filter"
        )

    with col2:
        filter_timeframe = st.selectbox(
            "Select Timeframe",
            ["All Timeframes", "1d", "4h", "1h", "15m"],
            key="history_timeframe_filter"
        )

    with col3:
        filter_days = st.slider(
            "Days to Look Back",
            min_value=1,
            max_value=30,
            value=7,
            key="history_days_filter"
        )

    with col4:
        show_latest_only = st.checkbox(
            "Latest Only",
            value=False,
            help="Show only the most recent analysis for each asset/timeframe",
            key="history_latest_only"
        )

    # Fetch historical data
    if filter_asset != "All Assets":
        if filter_timeframe != "All Timeframes":
            # Specific asset and timeframe
            history_data = st.session_state.analysis_db.get_analysis_history(
                filter_asset,
                filter_timeframe,
                filter_days
            )
        else:
            # Specific asset, all timeframes
            conn = st.session_state.analysis_db._get_connection()
            cursor = conn.cursor()

            since_date = (datetime.now() - timedelta(days=filter_days)).isoformat()

            query = '''
                SELECT * FROM analysis_results
                WHERE asset_symbol = ? AND created_at >= ?
            '''
            params = [filter_asset, since_date]

            if show_latest_only:
                query += ' AND is_latest = 1'

            query += ' ORDER BY created_at DESC'

            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            conn.close()

            history_data = [dict(zip(columns, row)) for row in rows]
    else:
        # All assets
        conn = st.session_state.analysis_db._get_connection()
        cursor = conn.cursor()

        since_date = (datetime.now() - timedelta(days=filter_days)).isoformat()

        query = 'SELECT * FROM analysis_results WHERE created_at >= ?'
        params = [since_date]

        if filter_timeframe != "All Timeframes":
            query += ' AND timeframe = ?'
            params.append(filter_timeframe)

        if show_latest_only:
            query += ' AND is_latest = 1'

        query += ' ORDER BY created_at DESC LIMIT 100'

        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        history_data = [dict(zip(columns, row)) for row in rows]

    # Display results
    if history_data:
        st.success(f"📊 Found **{len(history_data)}** analysis record(s)")

        # Prepare data for display
        display_data = []
        for record in history_data:
            # Format timestamp
            try:
                dt = datetime.fromisoformat(record['created_at'])
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = record['created_at']

            # Get signal emoji
            signal = record.get('consensus', 'HOLD')
            if signal == 'BUY':
                signal_display = '🟢 BUY'
            elif signal == 'SELL':
                signal_display = '🔴 SELL'
            else:
                signal_display = '⚪ HOLD'

            # Format reversal
            reversal = ''
            if record.get('reversal_detected'):
                reversal = f"⚠️ {record.get('reversal_type', 'REVERSAL')}"

            display_data.append({
                'Timestamp': timestamp,
                'Asset': record['asset_symbol'],
                'TF': record['timeframe'],
                'Signal': signal_display,
                'Confidence': f"{record.get('confidence', 0):.1%}",
                'Price': f"${record.get('price', 0):.5f}" if record.get('price') else 'N/A',
                'RSI': f"{record.get('rsi', 0):.1f}" if record.get('rsi') else 'N/A',
                'Trend': f"{record.get('trend_strength', 0):.1%}" if record.get('trend_strength') else 'N/A',
                'Momentum': record.get('momentum', 'N/A'),
                'Reversal': reversal,
                'Latest': '✅' if record.get('is_latest') else ''
            })

        # Display as dataframe
        df = pd.DataFrame(display_data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Show signal distribution
        if len(history_data) > 1:
            st.subheader("📊 Signal Distribution")
            signal_dist = analysis_stats.get('signal_distribution', {})
            if signal_dist:
                col1, col2, col3 = st.columns(3)
                total = sum(signal_dist.values())

                with col1:
                    buy_count = signal_dist.get('BUY', 0)
                    buy_pct = (buy_count / total * 100) if total > 0 else 0
                    st.metric("🟢 BUY Signals", f"{buy_count} ({buy_pct:.1f}%)")

                with col2:
                    sell_count = signal_dist.get('SELL', 0)
                    sell_pct = (sell_count / total * 100) if total > 0 else 0
                    st.metric("🔴 SELL Signals", f"{sell_count} ({sell_pct:.1f}%)")

                with col3:
                    hold_count = signal_dist.get('HOLD', 0)
                    hold_pct = (hold_count / total * 100) if total > 0 else 0
                    st.metric("⚪ HOLD Signals", f"{hold_count} ({hold_pct:.1f}%)")
    else:
        st.info("📭 No analysis records found for the selected filters. Try adjusting the filters or run some analyses first.")

else:
    st.info("📭 No analysis data available. Run some analyses to populate the history.")

st.divider()

if not scan_button:
    st.markdown("""
    ### How to Use the Scanner

    1. **Select timeframe mode**: Choose between Multi-Timeframe View or Single Timeframe
       - **Multi-Timeframe View**: See signals across all timeframes (15m, 1h, 4h, 1d) with a heatmap
       - **Single Timeframe**: Focus on one specific timeframe

    2. **Select symbols** using quick presets or custom selection
       - Forex Major Pairs
       - Precious Metals
       - All Assets
       - Custom selection

    3. **Set your account balance** for accurate position sizing

    4. **Click Scan All** to analyze all selected symbols

    5. **Review results** in multiple views:
       - **Overview**: Table view of all results
       - **Heatmap** (Multi-TF only): Visual matrix of signals across timeframes
       - **BUY Signals**: Detailed breakdown of buy opportunities
       - **SELL Signals**: Detailed breakdown of sell opportunities

    ### Multi-Timeframe View Features

    When using Multi-Timeframe View, you'll see:
    - Signal for each timeframe (15M, 1H, 4H, 1D)
    - Heatmap showing signal strength across timeframes
    - Strongest signals (pairs with 2+ timeframes agreeing)
    - Expected execution time for each timeframe
    - Trade plans optimized for each timeframe

    ### Single Timeframe Features

    When selecting a specific timeframe:
    - Focused analysis on that timeframe only
    - RSI, Trend, and Momentum indicators
    - Trade plan optimized for your selected timeframe
    - Expected duration and risk metrics
    """)
