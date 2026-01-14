"""
Trading Opportunities Page
Display all available trading opportunities across analyzed assets
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.auth.authentication_db import AuthenticatorDB, Permissions
from src.database.signals_db import SignalsDB
from src.utils.signal_display import SignalDisplayFormatter

st.set_page_config(page_title="Trading Opportunities", page_icon="🎯", layout="wide")

# Check authentication with database
if 'auth' not in st.session_state:
    st.session_state.auth = AuthenticatorDB()

auth = st.session_state.auth

if not auth.is_authenticated():
    st.error("🔒 Please login first")
    st.info("Return to the main page to login")
    st.stop()

# Render user info in sidebar
auth.render_user_info()

st.title("🎯 Trading Opportunities")
st.markdown("View all available trading opportunities across analyzed assets")

# Initialize opportunities storage in session state
if 'opportunities' not in st.session_state:
    st.session_state.opportunities = []

# Initialize signals database
if 'signals_db' not in st.session_state:
    st.session_state.signals_db = SignalsDB('data/signals.db')

# Sidebar filters
with st.sidebar:
    st.header("Filters")

    # Signal filter
    signal_filter = st.multiselect(
        "Signal Type",
        ["BUY", "SELL"],
        default=["BUY", "SELL"]
    )

    # Timeframe filter
    timeframe_filter = st.multiselect(
        "Timeframe",
        ["15M", "1H", "4H", "1D"],
        default=["15M", "1H", "4H", "1D"]
    )

    # Confidence filter
    min_confidence = st.slider(
        "Minimum Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        format="%.0f%%"
    )

    # Sorting
    sort_by = st.selectbox(
        "Sort By",
        ["Confidence (High to Low)", "Confidence (Low to High)",
         "Symbol (A-Z)", "Timeframe", "Signal Type"]
    )

    st.divider()

    # Clear opportunities
    if st.button("🗑️ Clear All Opportunities", use_container_width=True):
        st.session_state.opportunities = []
        st.rerun()

# Main content
# Initialize filtered_opps
filtered_opps = []

if len(st.session_state.opportunities) == 0:
    st.info("👋 No opportunities available yet")
    st.markdown("""
    ### How to get started:
    1. Go to the **Home** page or **Scanner** page
    2. Analyze one or more currency pairs/assets
    3. Opportunities will be automatically detected and displayed here

    **Note:** Opportunities are calculated during analysis and stored for your review.
    """)
else:
    # Filter opportunities
    for opp in st.session_state.opportunities:
        # Apply filters
        if opp['signal'] not in signal_filter:
            continue
        if opp['timeframe'] not in timeframe_filter:
            continue
        if opp['confidence'] < min_confidence:
            continue

        filtered_opps.append(opp)

    # Sort opportunities
    if sort_by == "Confidence (High to Low)":
        filtered_opps.sort(key=lambda x: x['confidence'], reverse=True)
    elif sort_by == "Confidence (Low to High)":
        filtered_opps.sort(key=lambda x: x['confidence'])
    elif sort_by == "Symbol (A-Z)":
        filtered_opps.sort(key=lambda x: x['symbol'])
    elif sort_by == "Timeframe":
        tf_order = {"15M": 0, "1H": 1, "4H": 2, "1D": 3}
        filtered_opps.sort(key=lambda x: tf_order.get(x['timeframe'], 999))
    elif sort_by == "Signal Type":
        filtered_opps.sort(key=lambda x: x['signal'])

    # Display summary metrics
    st.markdown("### 📊 Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Opportunities", len(filtered_opps))

    with col2:
        buy_count = sum(1 for opp in filtered_opps if opp['signal'] == 'BUY')
        st.metric("BUY Signals", buy_count)

    with col3:
        sell_count = sum(1 for opp in filtered_opps if opp['signal'] == 'SELL')
        st.metric("SELL Signals", sell_count)

    with col4:
        avg_confidence = sum(opp['confidence'] for opp in filtered_opps) / len(filtered_opps) if filtered_opps else 0
        st.metric("Avg Confidence", f"{avg_confidence:.1%}")

    st.markdown("---")

    # Display opportunities
    if len(filtered_opps) == 0:
        st.warning("No opportunities match your filter criteria")
    else:
        st.markdown(f"### 🎯 Opportunities ({len(filtered_opps)})")

        # Display in cards
        for idx, opp in enumerate(filtered_opps):
            with st.expander(
                f"{'🟢' if opp['signal'] == 'BUY' else '🔴'} {opp['symbol']} - {opp['signal']} on {opp['timeframe']} ({opp['confidence']:.1%} confidence)",
                expanded=idx < 3  # Expand first 3
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**📊 Signal Details**")
                    st.markdown(f"- **Symbol:** {opp['symbol']}")
                    st.markdown(f"- **Signal:** {'🟢 ' if opp['signal'] == 'BUY' else '🔴 '}{opp['signal']}")
                    st.markdown(f"- **Timeframe:** {opp['timeframe']}")
                    st.markdown(f"- **Confidence:** {opp['confidence']:.1%}")
                    st.markdown(f"- **Detected:** {opp['timestamp']}")

                with col2:
                    st.markdown("**💰 Price Levels**")
                    if 'current_price' in opp:
                        st.markdown(f"- **Current Price:** ${opp['current_price']:.5f}")
                    if 'support_levels' in opp and opp['support_levels']:
                        st.markdown(f"- **Nearest Support:** ${opp['support_levels'][0]:.5f}")
                    if 'resistance_levels' in opp and opp['resistance_levels']:
                        st.markdown(f"- **Nearest Resistance:** ${opp['resistance_levels'][0]:.5f}")
                    if 'entry_price' in opp:
                        st.markdown(f"- **Entry Price:** ${opp['entry_price']:.5f}")

                with col3:
                    st.markdown("**📈 Indicators**")
                    if 'rsi' in opp:
                        rsi_emoji = "🔥" if opp['rsi'] > 70 else "❄️" if opp['rsi'] < 30 else "➖"
                        st.markdown(f"- **RSI:** {rsi_emoji} {opp['rsi']:.1f}")
                    if 'trend' in opp:
                        st.markdown(f"- **Trend:** {opp['trend']}")
                    if 'momentum' in opp:
                        st.markdown(f"- **Momentum:** {opp['momentum']}")
                    if 'score' in opp:
                        st.markdown(f"- **Score:** {opp['score']:.1f}/5.0")

                # Display reasons if available
                if 'reasons' in opp and opp['reasons']:
                    st.markdown("**💡 Reasons:**")
                    for reason in opp['reasons']:
                        st.markdown(f"- {reason}")

                # Action link to view full analysis in new tab
                # Create URL with auto-login token
                import base64
                username = st.session_state.get('username', '')
                auto_login_token = base64.b64encode(username.encode()).decode() if username else ''
                analysis_url = f"/?symbol={opp['symbol']}&auto_login={auto_login_token}"

                st.markdown(
                    f"""
                    <a href="{analysis_url}" target="_blank" style="text-decoration: none;">
                        <button style="
                            width: 100%;
                            padding: 0.5rem 1rem;
                            background-color: #0066cc;
                            color: white;
                            border: none;
                            border-radius: 0.375rem;
                            font-size: 1rem;
                            font-weight: 500;
                            cursor: pointer;
                            transition: background-color 0.2s;
                        " onmouseover="this.style.backgroundColor='#0052a3'"
                           onmouseout="this.style.backgroundColor='#0066cc'">
                            📋 View Full Analysis (New Tab)
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )

# Display opportunities as table (alternative view)
st.markdown("---")
if st.checkbox("📊 Show Table View", value=False):
    if len(filtered_opps) > 0:
        # Convert to DataFrame
        df_opps = pd.DataFrame(filtered_opps)

        # Select relevant columns
        display_cols = ['symbol', 'signal', 'timeframe', 'confidence', 'timestamp']
        if 'current_price' in df_opps.columns:
            display_cols.insert(4, 'current_price')
        if 'score' in df_opps.columns:
            display_cols.append('score')

        df_display = df_opps[display_cols].copy()

        # Format columns
        if 'confidence' in df_display.columns:
            df_display['confidence'] = df_display['confidence'].apply(lambda x: f"{x:.1%}")
        if 'current_price' in df_display.columns:
            df_display['current_price'] = df_display['current_price'].apply(lambda x: f"${x:.5f}")
        if 'score' in df_display.columns:
            df_display['score'] = df_display['score'].apply(lambda x: f"{x:.1f}/5.0")

        # Rename columns
        df_display.columns = [col.replace('_', ' ').title() for col in df_display.columns]

        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No opportunities to display in table view")

# ============================================================================
# 📊 SIGNAL HISTORY SECTION
# ============================================================================

st.divider()
st.header("📊 Signal History & Recommendations")
st.markdown("Historical trading signals and recommendations from the database")

# Get all available signals
all_available_signals = st.session_state.signals_db.get_signals(limit=1, active_only=True)

if all_available_signals:
    total_signals = st.session_state.signals_db.get_stats().get('total_active_signals', 0)
    st.success(f"✅ Database contains {total_signals} active recommendation(s)")

    # Get unique assets with signals
    assets_with_signals = []
    conn = st.session_state.signals_db._get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT asset_symbol FROM trading_signals WHERE is_active = 1 ORDER BY asset_symbol')
    assets_with_signals = [row[0] for row in cursor.fetchall()]
    conn.close()

    if assets_with_signals:
        st.subheader("🔍 Select Asset to View Signal History")

        selected_asset_for_history = st.selectbox(
            "Choose an asset",
            assets_with_signals,
            key="opportunities_asset_history_selector"
        )

        if selected_asset_for_history:
            st.markdown(f"### 📈 {selected_asset_for_history}")
            st.markdown("━" * 80)

            # Get signals by timeframe for this asset
            signals_by_tf = st.session_state.signals_db.get_signals_by_timeframe(
                asset_symbol=selected_asset_for_history,
                limit_per_timeframe=20,
                active_only=True
            )

            if signals_by_tf and any(signals_by_tf.values()):
                # Display summary card
                SignalDisplayFormatter.create_signals_summary_card(signals_by_tf, selected_asset_for_history)

                # Create tabs for each timeframe
                available_timeframes = [tf for tf, signals in signals_by_tf.items() if signals]

                if available_timeframes:
                    tabs = st.tabs([f"{tf.upper()} - Last {len(signals_by_tf[tf])} signals"
                                   for tf in available_timeframes])

                    for tab_idx, tf in enumerate(available_timeframes):
                        with tabs[tab_idx]:
                            SignalDisplayFormatter.display_signal_table(
                                signals_by_tf[tf],
                                tf,
                                None  # Title shown in tab
                            )

                            # Show detailed view for most recent signal
                            if signals_by_tf[tf]:
                                with st.expander("📋 View Latest Recommendation Details", expanded=False):
                                    SignalDisplayFormatter.display_signal_details(signals_by_tf[tf][0])
            else:
                st.info(f"💡 No signals found for {selected_asset_for_history}. Run an analysis to generate signals.")
else:
    st.info("📭 No signal history available. Run some analyses to populate the signal database.")
