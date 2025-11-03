"""
Multi-Pair Scanner Page
Scan multiple currency pairs and metals simultaneously
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.forex_analyzer import ForexAnalyzer
from src.auth.authentication import Authenticator, Permissions

st.set_page_config(page_title="Multi-Pair Scanner", page_icon="📊", layout="wide")

# Check authentication
if 'auth' not in st.session_state:
    st.session_state.auth = Authenticator()

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

# Sidebar
with st.sidebar:
    st.header("Scanner Settings")

    # Preset selections
    scan_type = st.radio(
        "Quick Select",
        ["Forex Major Pairs", "Precious Metals", "All Assets", "Custom"]
    )

    if scan_type == "Forex Major Pairs":
        selected_symbols = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X']
    elif scan_type == "Precious Metals":
        selected_symbols = ['XAU_USD', 'XAG_USD']
    elif scan_type == "All Assets":
        selected_symbols = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'XAU_USD', 'XAG_USD']
    else:
        # Custom selection
        available_symbols = {
            'Forex': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'USDCHF=X', 'NZDUSD=X', 'USDCAD=X'],
            'Metals': ['XAU_USD', 'XAG_USD']
        }

        selected_symbols = []
        for category, symbols in available_symbols.items():
            st.markdown(f"**{category}**")
            for symbol in symbols:
                if st.checkbox(symbol, key=symbol):
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

    refresh_all_button = st.button("🔄 Refresh All Data", use_container_width=True,
                                   help="Clear cache and fetch fresh data for all selected symbols")

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

        # Fetch fresh data for each symbol
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, symbol in enumerate(selected_symbols):
            status_text.text(f"Refreshing {symbol}...")

            try:
                for tf in ['1d', '4h', '1h', '15m']:
                    fetcher.fetch_data(symbol, tf)
                st.success(f"✅ {symbol} - Data refreshed")
            except Exception as e:
                st.error(f"❌ {symbol} - Error: {str(e)}")

            progress_bar.progress((idx + 1) / len(selected_symbols))

        status_text.text("✅ All data refreshed!")
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
            status_text.text(f"Analyzing {symbol}...")

            try:
                analysis = st.session_state.analyzer.analyze_pair(
                    symbol=symbol,
                    account_balance=account_balance,
                    use_ml=use_ml
                )

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
