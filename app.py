#!/usr/bin/env python3
"""
Forex Analyzer - Streamlit GUI
A professional web-based interface for forex and precious metals trading analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.forex_analyzer import ForexAnalyzer
from src.data.data_fetcher import ForexDataFetcher
from src.indicators.technical_indicators import TechnicalIndicators
from src.auth.authentication_db import AuthenticatorDB, Permissions
from src.utils.opportunities import add_opportunities_to_session

# Page configuration
st.set_page_config(
    page_title="Forex Analyzer Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .buy-signal {
        color: #28a745;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .sell-signal {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .hold-signal {
        color: #ffc107;
        font-weight: bold;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Try to auto-authenticate from browser localStorage
if 'auth' not in st.session_state:
    st.session_state.auth = AuthenticatorDB()

# Check for auto-login from localStorage (via query params)
query_params = st.query_params
auto_login_user = query_params.get("auto_login")

if auto_login_user and not st.session_state.auth.is_authenticated():
    try:
        import base64
        # Decode username from query param
        username = base64.b64decode(auto_login_user).decode()

        # Get user from database
        user = st.session_state.auth.db.get_user(username)
        if user:
            # Set session state for auto-login
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
            st.session_state['user_role'] = user['role']
            st.session_state['user_name'] = user['name']
            st.session_state['user_email'] = user['email']

            # Remove auto_login from URL to clean it up
            st.query_params.clear()
            st.query_params.update({"symbol": query_params.get("symbol", "")})
            st.rerun()
    except Exception:
        pass

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ForexAnalyzer()
    st.session_state.cache_preloaded = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'current_symbol' not in st.session_state:
    st.session_state.current_symbol = None


def _check_cache_exists() -> bool:
    """Check if file cache already has data (avoids unnecessary preloading on new sessions)"""
    import os
    from datetime import datetime, timedelta

    cache_dir = 'data/cache'
    if not os.path.exists(cache_dir):
        return False

    # Check if we have any recent cache files (less than 4 hours old)
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.pkl')]
    if not cache_files:
        return False

    # Check if at least some files are fresh
    fresh_count = 0
    max_age = timedelta(hours=4)

    for cache_file in cache_files[:10]:  # Check first 10 files
        cache_path = os.path.join(cache_dir, cache_file)
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            if datetime.now() - file_time < max_age:
                fresh_count += 1
        except Exception:
            pass

    # If we have at least 4 fresh cache files, skip preloading
    return fresh_count >= 4


# Preload data cache on first run (only if no fresh cache exists)
if not st.session_state.get('cache_preloaded', False):
    # First check if cache files already exist (from previous sessions or batch jobs)
    cache_exists = _check_cache_exists()

    if cache_exists:
        # Cache files exist - skip API preloading, just mark as done
        logger.info("📁 Existing cache files found - skipping API preload (new browser session)")
        st.session_state.cache_preloaded = True
        st.session_state.preload_stats = {'success': 0, 'failed': 0, 'skipped': True, 'reason': 'Cache files exist'}
    else:
        # No cache - need to preload from API
        with st.spinner('🚀 Preloading market data into cache... Please wait...'):
            try:
                # Get symbols from config
                config = st.session_state.analyzer.config
                symbols_to_preload = config.get('currency_pairs', [])[:4]  # Limit to first 4 to avoid long startup
                timeframes_to_preload = ['1d', '4h', '1h', '15m']

                preload_stats = st.session_state.analyzer.preload_cache(
                    symbols=symbols_to_preload,
                    timeframes=timeframes_to_preload
                )

                st.session_state.cache_preloaded = True
                st.session_state.preload_stats = preload_stats

                # Log success
                if preload_stats['success'] > 0:
                    logger.info(f"✨ Cache preloaded: {preload_stats['success']} items loaded, {preload_stats['failed']} failed")
            except Exception as e:
                logger.error(f"Error preloading cache: {e}")
                st.session_state.cache_preloaded = True  # Mark as attempted to avoid retrying

def create_candlestick_chart(df, symbol, timeframe):
    """Create an interactive candlestick chart with indicators"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'{symbol} - {timeframe}', 'Volume', 'RSI')
    )

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )

    # Moving averages
    if 'MA_20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MA_20'], name='MA 20',
                      line=dict(color='orange', width=1)),
            row=1, col=1
        )
    if 'MA_50' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MA_50'], name='MA 50',
                      line=dict(color='blue', width=1)),
            row=1, col=1
        )

    # Bollinger Bands
    if all(col in df.columns for col in ['BB_Upper', 'BB_Lower']):
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper',
                      line=dict(color='gray', width=1, dash='dash'),
                      showlegend=False),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower',
                      line=dict(color='gray', width=1, dash='dash'),
                      fill='tonexty', fillcolor='rgba(128,128,128,0.1)',
                      showlegend=False),
            row=1, col=1
        )

    # Volume
    colors = ['red' if row['Close'] < row['Open'] else 'green'
              for idx, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume',
               marker_color=colors, showlegend=False),
        row=2, col=1
    )

    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI',
                      line=dict(color='purple', width=2)),
            row=3, col=1
        )
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                     opacity=0.5, row=3, col=1)

    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        margin=dict(l=80, r=120, t=80, b=60)  # Add margins to prevent clipping
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)

    return fig

def create_combined_sr_chart(analysis, symbol):
    """Create a combined chart showing support/resistance levels across multiple timeframes"""
    # Define timeframes to display
    timeframes = ['15m', '1h', '4h']

    # Define colors for each timeframe
    tf_colors = {
        '15m': {'support': 'rgba(0, 255, 0, 0.3)', 'resistance': 'rgba(255, 0, 0, 0.3)', 'line': 'green'},
        '1h': {'support': 'rgba(0, 100, 255, 0.3)', 'resistance': 'rgba(255, 100, 0, 0.3)', 'line': 'blue'},
        '4h': {'support': 'rgba(255, 0, 255, 0.3)', 'resistance': 'rgba(255, 255, 0, 0.3)', 'line': 'purple'}
    }

    # Use the longest timeframe data as the base chart (4h)
    base_tf = '4h'
    if base_tf not in analysis['timeframe_analyses']:
        base_tf = timeframes[-1] if timeframes[-1] in analysis['timeframe_analyses'] else list(analysis['timeframe_analyses'].keys())[0]

    base_data = analysis['timeframe_analyses'][base_tf]
    df = base_data['dataframe'].tail(100)

    # Create figure with subplots (adding MACD as 4th subplot)
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=(f'{symbol} - Multi-Timeframe Support & Resistance', 'Volume', 'RSI', 'MACD')
    )

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )

    # Add moving averages
    if 'MA_20' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MA_20'], name='MA 20',
                      line=dict(color='orange', width=1)),
            row=1, col=1
        )
    if 'MA_50' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MA_50'], name='MA 50',
                      line=dict(color='blue', width=1)),
            row=1, col=1
        )

    # Add support and resistance levels for each timeframe
    # Collect all levels with metadata for smart positioning
    all_levels = []

    for tf_idx, tf in enumerate(timeframes):
        if tf not in analysis['timeframe_analyses']:
            continue

        tf_data = analysis['timeframe_analyses'][tf]
        colors = tf_colors[tf]

        # Collect support levels
        support_levels = tf_data.get('support_levels', [])[:4]
        for i, level in enumerate(support_levels):
            all_levels.append({
                'price': level,
                'tf': tf,
                'type': 'S',
                'number': i + 1,
                'color': colors['line'],
                'line_dash': 'dot',
                'tf_idx': tf_idx
            })

        # Collect resistance levels
        resistance_levels = tf_data.get('resistance_levels', [])[:4]
        for i, level in enumerate(resistance_levels):
            all_levels.append({
                'price': level,
                'tf': tf,
                'type': 'R',
                'number': i + 1,
                'color': colors['line'],
                'line_dash': 'dash',
                'tf_idx': tf_idx
            })

    # Sort all levels by price
    all_levels.sort(key=lambda x: x['price'])

    # Smart positioning: alternate between left and right, with vertical stagger
    # Group close levels and spread them out
    for idx, level_info in enumerate(all_levels):
        # Determine if this level is close to the previous one (within 0.1% range)
        if idx > 0:
            prev_price = all_levels[idx - 1]['price']
            price_diff_pct = abs(level_info['price'] - prev_price) / prev_price * 100

            # If levels are very close (< 0.1%), alternate left/right more aggressively
            if price_diff_pct < 0.1:
                # Use timeframe index to spread labels
                if level_info['tf_idx'] % 2 == 0:
                    position = "top right" if idx % 2 == 0 else "bottom right"
                else:
                    position = "top left" if idx % 2 == 0 else "bottom left"
            else:
                # Normal alternating pattern
                positions_cycle = ["top left", "top right", "bottom left", "bottom right"]
                position = positions_cycle[idx % 4]
        else:
            position = "top left"

        # Draw the horizontal line with annotation
        fig.add_hline(
            y=level_info['price'],
            line_dash=level_info['line_dash'],
            line_color=level_info['color'],
            opacity=0.6,
            annotation_text=f"{level_info['tf'].upper()} {level_info['type']}{level_info['number']}: ${level_info['price']:.2f}",
            annotation_position=position,
            annotation_font_size=8,
            annotation_font_color=level_info['color'],
            annotation_bgcolor="rgba(255, 255, 255, 0.9)",
            annotation_bordercolor=level_info['color'],
            annotation_borderwidth=1,
            annotation_borderpad=2,
            row=1, col=1
        )

    # Add volume bars
    colors_volume = ['red' if row['Close'] < row['Open'] else 'green'
                     for idx, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume',
               marker_color=colors_volume, showlegend=False),
        row=2, col=1
    )

    # Add RSI
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI',
                      line=dict(color='purple', width=2)),
            row=3, col=1
        )
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red",
                     opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green",
                     opacity=0.5, row=3, col=1)

    # Add MACD
    if all(col in df.columns for col in ['MACD', 'MACD_Signal']):
        # MACD Line
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD'], name='MACD',
                      line=dict(color='blue', width=2)),
            row=4, col=1
        )
        # Signal Line
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal',
                      line=dict(color='orange', width=2)),
            row=4, col=1
        )
        # MACD Histogram
        if 'MACD_Hist' in df.columns:
            colors_macd = ['red' if val < 0 else 'green' for val in df['MACD_Hist']]
            fig.add_trace(
                go.Bar(x=df.index, y=df['MACD_Hist'], name='MACD Histogram',
                       marker_color=colors_macd, showlegend=False, opacity=0.5),
                row=4, col=1
            )
        # Zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray",
                     opacity=0.5, row=4, col=1)

    # Update layout
    fig.update_layout(
        height=1100,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        margin=dict(l=80, r=150, t=80, b=60)  # Increased right margin for annotations
    )

    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1)

    return fig

def create_sr_summary_table(analysis, timeframes=['15m', '1h', '4h']):
    """Create a summary table of support and resistance levels ordered by value"""
    table_data = []

    for tf in timeframes:
        if tf not in analysis['timeframe_analyses']:
            continue

        tf_data = analysis['timeframe_analyses'][tf]

        # Add resistance levels
        resistance_levels = tf_data.get('resistance_levels', [])[:4]
        for i, level in enumerate(resistance_levels):
            table_data.append({
                'Type': 'Resistance',
                'Timeframe': tf.upper(),
                'Level': f'R{i+1}',
                'Value': level,
                'Value_Display': f'${level:.2f}'
            })

        # Add support levels
        support_levels = tf_data.get('support_levels', [])[:4]
        for i, level in enumerate(support_levels):
            table_data.append({
                'Type': 'Support',
                'Timeframe': tf.upper(),
                'Level': f'S{i+1}',
                'Value': level,
                'Value_Display': f'${level:.2f}'
            })

    # Sort by value descending (resistance first, then support)
    # First sort by value descending
    table_data.sort(key=lambda x: x['Value'], reverse=True)

    # Create DataFrame
    import pandas as pd
    df_table = pd.DataFrame(table_data)

    # Select and rename columns for display
    if not df_table.empty:
        df_display = df_table[['Type', 'Timeframe', 'Level', 'Value_Display']]
        df_display.columns = ['Type', 'Timeframe', 'Level', 'Price']
        return df_display
    else:
        return pd.DataFrame(columns=['Type', 'Timeframe', 'Level', 'Price'])

def display_signal_badge(signal, confidence):
    """Display a colored signal badge"""
    if signal == 'BUY':
        st.markdown(f'<div class="buy-signal">🟢 BUY ({confidence:.1%})</div>',
                   unsafe_allow_html=True)
    elif signal == 'SELL':
        st.markdown(f'<div class="sell-signal">🔴 SELL ({confidence:.1%})</div>',
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="hold-signal">🟡 HOLD ({confidence:.1%})</div>',
                   unsafe_allow_html=True)

def main():
    """Main application"""

    # Get authenticator from session state
    auth = st.session_state.auth

    # Check if user is authenticated
    if not auth.is_authenticated():
        auth.render_login_page()
        return

    # Render user info in sidebar
    auth.render_user_info()

    # Header
    st.markdown('<h1 class="main-header">📈 Forex Analyzer Pro</h1>',
                unsafe_allow_html=True)

    # Show data source status
    analyzer = st.session_state.analyzer
    if analyzer.data_fetcher.twelvedata_fetcher:
        st.success("✅ Real-time data enabled (Twelve Data API) - 10 minute auto-refresh")
    else:
        st.warning("⚠️ Using delayed data (Yahoo Finance) - Get real-time data: https://twelvedata.com/pricing")
        with st.expander("Why am I seeing Yahoo Finance?"):
            st.write("**Possible reasons:**")
            st.write("1. 🔄 **Session state cached** - Restart Streamlit to reload configuration")
            st.write("2. 🔑 **API key not configured** - Check `config/config.yaml` line 74")
            st.write("3. ⚠️ **API rate limit exceeded** - Free tier: 8 calls/min, 800/day")
            st.write("4. 🌐 **Network/firewall issue** - Check internet connection")
            st.write("\n**Quick fix:** Stop Streamlit (Ctrl+C) and run again: `streamlit run app.py`")

    # Check for navigation from Opportunities page
    if st.session_state.get('nav_to_home', False):
        url_symbol = st.session_state.get('nav_to_home_symbol', None)
        # Clear the navigation flags
        st.session_state.nav_to_home = False
    else:
        # Check for URL parameter
        query_params = st.query_params
        url_symbol = query_params.get("symbol", None)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Symbol selection
        st.subheader("Select Symbol")

        # If symbol is provided in URL or navigation, show it
        if url_symbol:
            st.info(f"📍 Viewing: {url_symbol}")
            symbol = url_symbol
            # Set default symbol type based on URL symbol
            if '=' in url_symbol or 'USD' in url_symbol:
                default_type = "Custom"
            elif '/' in url_symbol:
                default_type = "Crypto"
            elif url_symbol in ['US30', 'US100']:
                default_type = "Indices"
            elif url_symbol in ['XAU_USD', 'XAG_USD']:
                default_type = "Precious Metals"
            else:
                default_type = "Forex Pairs"
        else:
            default_type = "Forex Pairs"

        symbol_type = st.radio(
            "Asset Type",
            ["Forex Pairs", "Indices", "Crypto", "Precious Metals", "Custom"],
            index=["Forex Pairs", "Indices", "Crypto", "Precious Metals", "Custom"].index(default_type)
        )

        # Only show selection if not from URL, otherwise use URL symbol
        if not url_symbol:
            if symbol_type == "Forex Pairs":
                symbol = st.selectbox(
                    "Forex Pair",
                    ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X',
                     'USDCHF=X', 'NZDUSD=X', 'USDCAD=X']
                )
            elif symbol_type == "Indices":
                symbol = st.selectbox(
                    "Index",
                    ['US30', 'US100'],
                    format_func=lambda x: {
                        'US30': '📊 US30 (Dow Jones)',
                        'US100': '📈 US100 (NASDAQ 100)'
                    }[x]
                )
                st.caption("💡 US stock market indices")
            elif symbol_type == "Crypto":
                symbol = st.selectbox(
                    "Cryptocurrency",
                    ['BTC/USD', 'ETH/USD'],
                    format_func=lambda x: {
                        'BTC/USD': '₿ Bitcoin',
                        'ETH/USD': 'Ξ Ethereum'
                    }[x]
                )
                st.caption("💡 24/7 cryptocurrency markets")
            elif symbol_type == "Precious Metals":
                symbol = st.selectbox(
                    "Metal",
                    ['XAU_USD', 'XAG_USD'],
                    format_func=lambda x: {
                        'XAU_USD': '🥇 Gold Spot (per oz)',
                        'XAG_USD': '🥈 Silver Spot (per oz)'
                    }[x]
                )
                st.caption("💡 Using Oanda spot prices for real-time accuracy")
            else:
                symbol = st.text_input("Enter Symbol", "EURUSD=X")

        # Analysis options
        st.subheader("Analysis Options")
        use_ml = st.checkbox("Use ML Model", value=True)
        account_balance = st.number_input(
            "Account Balance ($)",
            min_value=100,
            value=10000,
            step=100
        )

        # Advanced Settings (Collapsible)
        with st.expander("⚙️ Advanced Settings", expanded=False):
            st.markdown("**Signal Quality Controls**")
            st.caption("Lower values = More signals but lower quality")

            min_timeframes = st.slider(
                "Min Timeframes Agreement",
                min_value=1,
                max_value=4,
                value=st.session_state.analyzer.config.get('confluence', {}).get('min_timeframes_agree', 2),
                help="How many timeframes must agree (1=25%, 2=50%, 3=75%, 4=100%)"
            )

            min_confidence = st.slider(
                "Min Confidence Score",
                min_value=0.3,
                max_value=0.8,
                value=st.session_state.analyzer.config.get('confluence', {}).get('min_confidence', 0.5),
                step=0.05,
                format="%.0f%%",
                help="Minimum confidence to accept signal (30%=Very Aggressive, 60%=Conservative)"
            )

            st.divider()
            st.markdown("**Risk Management**")

            risk_per_trade = st.slider(
                "Risk Per Trade",
                min_value=0.5,
                max_value=5.0,
                value=st.session_state.analyzer.config.get('risk_management', {}).get('risk_per_trade', 0.02) * 100,
                step=0.5,
                format="%.1f%%",
                help="Percentage of account to risk per trade"
            ) / 100

            atr_multiplier = st.slider(
                "Stop Loss (ATR Multiplier)",
                min_value=1.0,
                max_value=4.0,
                value=st.session_state.analyzer.config.get('risk_management', {}).get('atr_multiplier', 2.0),
                step=0.5,
                help="Stop loss distance (1.0=Tight, 4.0=Wide)"
            )

            min_risk_reward = st.slider(
                "Min Risk:Reward Ratio",
                min_value=1.0,
                max_value=3.0,
                value=st.session_state.analyzer.config.get('risk_management', {}).get('min_risk_reward', 1.5),
                step=0.1,
                format="1:%.1f",
                help="Minimum reward relative to risk (1:1.0=Aggressive, 1:3.0=Conservative)"
            )

            st.divider()
            st.markdown("**Indicator Sensitivity**")

            rsi_overbought = st.slider(
                "RSI Overbought",
                min_value=60,
                max_value=80,
                value=st.session_state.analyzer.config.get('indicators', {}).get('rsi_overbought', 70),
                step=5,
                help="Lower = More sensitive (triggers earlier)"
            )

            rsi_oversold = st.slider(
                "RSI Oversold",
                min_value=20,
                max_value=40,
                value=st.session_state.analyzer.config.get('indicators', {}).get('rsi_oversold', 30),
                step=5,
                help="Higher = More sensitive (triggers earlier)"
            )

            # Preset buttons
            st.divider()
            st.markdown("**Quick Presets**")
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if st.button("🛡️ Conservative", use_container_width=True):
                    st.session_state.preset = 'conservative'
                    st.rerun()

            with col_b:
                if st.button("⚖️ Balanced", use_container_width=True):
                    st.session_state.preset = 'balanced'
                    st.rerun()

            with col_c:
                if st.button("🚀 Aggressive", use_container_width=True):
                    st.session_state.preset = 'aggressive'
                    st.rerun()

            # Apply preset if selected
            if 'preset' in st.session_state:
                if st.session_state.preset == 'conservative':
                    min_timeframes = 3
                    min_confidence = 0.6
                    risk_per_trade = 0.01
                    atr_multiplier = 2.5
                    min_risk_reward = 2.0
                    rsi_overbought = 70
                    rsi_oversold = 30
                    st.success("✅ Conservative preset applied!")
                elif st.session_state.preset == 'balanced':
                    min_timeframes = 2
                    min_confidence = 0.5
                    risk_per_trade = 0.02
                    atr_multiplier = 2.0
                    min_risk_reward = 1.5
                    rsi_overbought = 70
                    rsi_oversold = 30
                    st.info("✅ Balanced preset applied!")
                elif st.session_state.preset == 'aggressive':
                    min_timeframes = 1
                    min_confidence = 0.4
                    risk_per_trade = 0.03
                    atr_multiplier = 1.5
                    min_risk_reward = 1.2
                    rsi_overbought = 65
                    rsi_oversold = 35
                    st.warning("✅ Aggressive preset applied!")

                # Clear preset after applying
                del st.session_state.preset

            # Update analyzer config with GUI values
            st.session_state.analyzer.config['confluence']['min_timeframes_agree'] = min_timeframes
            st.session_state.analyzer.config['confluence']['min_confidence'] = min_confidence
            st.session_state.analyzer.config['risk_management']['risk_per_trade'] = risk_per_trade
            st.session_state.analyzer.config['risk_management']['atr_multiplier'] = atr_multiplier
            st.session_state.analyzer.config['risk_management']['min_risk_reward'] = min_risk_reward
            st.session_state.analyzer.config['indicators']['rsi_overbought'] = rsi_overbought
            st.session_state.analyzer.config['indicators']['rsi_oversold'] = rsi_oversold

        # Analyze button
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)

        # Refresh Data button (admin only)
        if auth.has_permission(Permissions.REFRESH_DATA):
            refresh_button = st.button("🔄 Refresh Latest Data", use_container_width=True,
                                       help="Clear cache and fetch fresh data from market")
        else:
            refresh_button = False

        st.divider()

        # Quick actions
        st.subheader("Quick Actions")
        if st.button("📊 Scan Multiple Pairs", use_container_width=True):
            st.session_state.page = 'scanner'

        # Train ML Model button (admin only)
        if auth.has_permission(Permissions.TRAIN_MODEL):
            if st.button("🤖 Train ML Model", use_container_width=True):
                st.session_state.page = 'training'

        st.divider()

        # Cache statistics (collapsible)
        with st.expander("📊 Cache Statistics", expanded=False):
            try:
                cache_stats = st.session_state.analyzer.get_cache_stats()

                if 'error' not in cache_stats:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Fresh Entries", cache_stats.get('fresh_entries', 0))
                        st.metric("Symbols Cached", cache_stats.get('symbols_cached', 0))

                    with col2:
                        st.metric("Total Entries", cache_stats.get('total_entries', 0))
                        st.metric("Expired", cache_stats.get('expired_entries', 0))

                    # Show preload stats if available
                    if 'preload_stats' in st.session_state:
                        preload = st.session_state.preload_stats
                        st.caption(f"Preloaded on startup: {preload['success']} success, {preload['failed']} failed")
                else:
                    st.caption("In-memory cache not available")
            except Exception as e:
                st.caption(f"Error: {str(e)}")

        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Handle refresh button
    if refresh_button:
        with st.spinner(f'Fetching latest data for {symbol}...'):
            try:
                import shutil
                cache_dir = 'data/cache'

                # Clear in-memory cache for this symbol
                if st.session_state.analyzer.data_fetcher.memory_cache:
                    st.session_state.analyzer.data_fetcher.memory_cache.invalidate(symbol=symbol)
                    logger.info(f"Cleared in-memory cache for {symbol}")

                # Clear file cache for this symbol
                if os.path.exists(cache_dir):
                    for file in os.listdir(cache_dir):
                        if symbol.replace('=', '_').replace('/', '_') in file:
                            os.remove(os.path.join(cache_dir, file))

                # Fetch fresh data using the analyzer's data fetcher (with API keys)
                fetcher = st.session_state.analyzer.data_fetcher
                timeframes = ['1d', '4h', '1h', '15m']

                progress_bar = st.progress(0)
                for idx, tf in enumerate(timeframes):
                    df = fetcher.fetch_data(symbol, tf, use_cache=False)
                    if df is not None and len(df) > 0:
                        latest_price = df['Close'].iloc[-1]
                        latest_date = df.index[-1].strftime('%Y-%m-%d %H:%M')
                        st.success(f"✅ {tf.upper()}: Fetched {len(df)} candles | Latest: ${latest_price:.4f} ({latest_date})")
                    else:
                        st.error(f"❌ {tf.upper()}: Failed to fetch data")
                    progress_bar.progress((idx + 1) / len(timeframes))

                st.success(f"✅ Latest real-time data refreshed for {symbol}!")
                st.info("Click '🔍 Analyze' to run analysis with fresh data")

            except Exception as e:
                st.error(f"Error refreshing data: {str(e)}")

    # Auto-trigger analysis if symbol is from URL/navigation and not already analyzed
    auto_analyze = (url_symbol or st.session_state.get('auto_analyze_symbol')) and (
        'analysis_result' not in st.session_state or
        st.session_state.get('current_symbol') != (url_symbol or st.session_state.get('auto_analyze_symbol'))
    )

    # Clear auto analyze flag after checking
    if 'auto_analyze_symbol' in st.session_state and auto_analyze:
        # Keep the symbol for this run, will be cleared after analysis
        pass

    # Main content
    if analyze_button or auto_analyze:
        # Get cache stats before analysis
        cache_stats_before = st.session_state.analyzer.get_cache_stats()
        fresh_before = cache_stats_before.get('fresh_entries', 0)

        with st.spinner(f'Analyzing {symbol}... ⚡ Using cached data when available'):
            try:
                # Perform analysis
                analysis = st.session_state.analyzer.analyze_pair(
                    symbol=symbol,
                    account_balance=account_balance,
                    use_ml=use_ml
                )

                st.session_state.analysis_result = analysis
                st.session_state.current_symbol = symbol

                # Check if data was served from cache
                cache_stats_after = st.session_state.analyzer.get_cache_stats()
                fresh_after = cache_stats_after.get('fresh_entries', 0)

                if fresh_after == fresh_before + 4:  # All 4 timeframes were fetched fresh
                    st.info("🔄 Fresh data fetched from market")
                elif fresh_after > fresh_before:
                    st.success(f"⚡ Analysis complete - {4 - (fresh_after - fresh_before)} timeframes served from cache (instant)")
                else:
                    st.success("⚡ Analysis complete - All data served from cache (instant response!)")

                # Clear auto analyze flag after successful analysis
                if 'auto_analyze_symbol' in st.session_state:
                    del st.session_state.auto_analyze_symbol

                # Extract and store opportunities
                num_opps = add_opportunities_to_session(st.session_state, symbol, analysis)
                if num_opps > 0:
                    st.success(f"✅ Found {num_opps} trading opportunity(ies) - Check the 🎯 Opportunities page!")

            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                # Clear auto analyze flag even on error
                if 'auto_analyze_symbol' in st.session_state:
                    del st.session_state.auto_analyze_symbol
                return

    # Display results
    if st.session_state.analysis_result:
        analysis = st.session_state.analysis_result

        if 'error' in analysis:
            st.error(f"Analysis Error: {analysis['error']}")
            return

        # Overview section
        st.header(f"📊 Analysis Results - {st.session_state.current_symbol}")

        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            current_price = analysis['current_price']

            # Special handling for precious metals spot prices
            if st.session_state.current_symbol == 'XAU_USD':
                st.metric(
                    "Gold Spot",
                    f"${current_price:.2f}/oz",
                    help="Gold Spot Price - per troy ounce (Oanda)"
                )
            elif st.session_state.current_symbol == 'XAG_USD':
                st.metric(
                    "Silver Spot",
                    f"${current_price:.2f}/oz",
                    help="Silver Spot Price - per troy ounce (Oanda)"
                )
            else:
                st.metric(
                    "Current Price",
                    f"${current_price:.5f}"
                )

        with col2:
            final = analysis['final_decision']
            display_signal_badge(final['signal'], final['confidence'])

        with col3:
            consensus = analysis['multi_timeframe_consensus']
            st.metric(
                "Timeframe Agreement",
                f"{consensus['agreement_count']}/{consensus['total_timeframes']}"
            )

        with col4:
            if analysis.get('trade_plan') and analysis['trade_plan'].get('approved'):
                tp = analysis['trade_plan']
                st.metric(
                    "Risk:Reward",
                    f"1:{tp['risk_reward_ratio']:.2f}"
                )
            else:
                st.metric("Risk:Reward", "N/A")

        # Tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 V2 Recommendations", "📈 Charts", "📋 Trade Plan", "🎯 Multi-Timeframe", "📊 Technical Details"
        ])

        with tab1:
            st.subheader("🎯 Enhanced Recommendations (ForexApp V2 Style)")

            # Explanation box
            with st.expander("ℹ️ Understanding Recommendations", expanded=False):
                st.markdown("""
                **Two Types of Recommendations:**

                1. **Final Decision (Top)**: Combines ALL timeframes + ML model
                   - Shows HOLD when timeframes don't agree
                   - More conservative - prevents conflicting signals
                   - Best for beginners

                2. **Individual Timeframes (Below)**: Each timeframe analyzed independently
                   - Shows BUY/SELL for specific time horizons
                   - Can trade any timeframe that shows clear signal
                   - Best for experienced traders

                **💡 Pro Tip**: Even if Final Decision is HOLD, you can trade based on individual
                timeframe signals (like 1H SELL or 1D STRONG BUY). Just make sure you understand
                that timeframe's trading style!
                """)

            # Multi-timeframe summary table
            st.markdown("### 📊 Multi-Timeframe Summary")

            summary_data = []
            for tf in ['15m', '1h', '4h', '1d']:
                if tf in analysis['timeframe_analyses']:
                    tf_analysis = analysis['timeframe_analyses'][tf]
                    enhanced = tf_analysis.get('enhanced_recommendation', {})

                    if enhanced:
                        rec = enhanced.get('recommendation', 'N/A')
                        score = enhanced.get('score', 0)
                        price = enhanced.get('current_price', 0)

                        # Get stop loss and TP1
                        stop_losses = enhanced.get('stop_losses', {})
                        sl_price = stop_losses.get('standard_2atr', {}).get('price', 0)

                        take_profits = enhanced.get('take_profits', {})
                        tp1_price = take_profits.get('tp1_scalp', {}).get('price', 0) if take_profits else 0

                        # Determine color based on recommendation
                        if "BUY" in rec:
                            rec_color = "🟢"
                        elif "SELL" in rec:
                            rec_color = "🔴"
                        else:
                            rec_color = "🟡"

                        summary_data.append({
                            'Timeframe': tf.upper(),
                            'Recommendation': f"{rec_color} {rec}",
                            'Score': score,
                            'Current Price': f"${price:.5f}",
                            'Stop Loss': f"${sl_price:.5f}",
                            'Target (TP1)': f"${tp1_price:.5f}" if tp1_price > 0 else "N/A"
                        })

            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)

                # Count actionable signals
                actionable_count = sum(1 for item in summary_data
                                     if any(signal in item['Recommendation']
                                           for signal in ['STRONG BUY', 'BUY', 'STRONG SELL', 'SELL'])
                                           and 'HOLD' not in item['Recommendation'])

                if actionable_count > 0:
                    st.success(f"✅ {actionable_count} timeframe(s) showing actionable signals - Select below for details!")
                else:
                    st.info("ℹ️ All timeframes showing HOLD - No clear trading opportunities right now")

            st.divider()

            # Timeframe selector for detailed view
            st.markdown("### 📈 Detailed Analysis by Timeframe")

            selected_tf = st.selectbox(
                "Select timeframe for detailed view:",
                ['15m', '1h', '4h', '1d'],
                format_func=lambda x: {
                    '15m': '15 Minutes (Day Trading)',
                    '1h': '1 Hour (Intraday)',
                    '4h': '4 Hours (Swing Trading)',
                    '1d': '1 Day (Position Trading)'
                }[x]
            )

            if selected_tf in analysis['timeframe_analyses']:
                tf_analysis = analysis['timeframe_analyses'][selected_tf]
                enhanced = tf_analysis.get('enhanced_recommendation', {})
                df = tf_analysis['dataframe']

                if enhanced:
                    # Recommendation header
                    rec = enhanced.get('recommendation', 'N/A')
                    score = enhanced.get('score', 0)
                    current_price = enhanced.get('current_price', 0)

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if "BUY" in rec:
                            st.markdown(f'<div class="buy-signal">🟢 {rec}</div>', unsafe_allow_html=True)
                        elif "SELL" in rec:
                            st.markdown(f'<div class="sell-signal">🔴 {rec}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="hold-signal">🟡 {rec}</div>', unsafe_allow_html=True)

                    with col2:
                        st.metric("Signal Score", score)

                    with col3:
                        st.metric("Current Price", f"${current_price:.5f}")

                    # Create enhanced chart with entry points, stop losses, and take profits
                    st.markdown("#### 📊 Price Chart with Trading Levels")

                    # Create candlestick chart
                    fig = go.Figure()

                    # Candlesticks
                    fig.add_trace(go.Candlestick(
                        x=df.index[-100:],
                        open=df['Open'].tail(100),
                        high=df['High'].tail(100),
                        low=df['Low'].tail(100),
                        close=df['Close'].tail(100),
                        name='Price'
                    ))

                    # Add Moving Averages
                    if 'MA_20' in df.columns:
                        fig.add_trace(go.Scatter(
                            x=df.index[-100:],
                            y=df['MA_20'].tail(100),
                            name='MA 20',
                            line=dict(color='orange', width=1)
                        ))

                    if 'MA_50' in df.columns:
                        fig.add_trace(go.Scatter(
                            x=df.index[-100:],
                            y=df['MA_50'].tail(100),
                            name='MA 50',
                            line=dict(color='blue', width=1)
                        ))

                    # Add Bollinger Bands
                    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
                        fig.add_trace(go.Scatter(
                            x=df.index[-100:],
                            y=df['BB_Upper'].tail(100),
                            name='BB Upper',
                            line=dict(color='gray', width=1, dash='dash')
                        ))
                        fig.add_trace(go.Scatter(
                            x=df.index[-100:],
                            y=df['BB_Lower'].tail(100),
                            name='BB Lower',
                            line=dict(color='gray', width=1, dash='dash'),
                            fill='tonexty',
                            fillcolor='rgba(128,128,128,0.1)'
                        ))

                    # Add Entry Points with smart positioning
                    entry_points = enhanced.get('entry_points', {})
                    if entry_points:
                        # Staggered positioning to prevent overlap
                        # Larger yshift values and alternating sides for better separation
                        entry_position_config = [
                            {'position': 'top left', 'yshift': 15},      # E1: far up on left
                            {'position': 'bottom right', 'yshift': -15}, # E2: far down on right (opposite side!)
                            {'position': 'top right', 'yshift': 0}       # E3: centered on right
                        ]

                        for i, (entry_name, entry_data) in enumerate(entry_points.items(), 1):
                            entry_price = entry_data['price']
                            urgency = entry_data['urgency']

                            if urgency == 'NOW':
                                line_color = 'blue'
                                bg_color = 'rgba(0, 0, 255, 0.9)'  # Solid blue
                                dash = 'solid'
                            else:
                                line_color = 'cyan'
                                bg_color = 'rgba(0, 139, 139, 0.9)'  # Dark cyan
                                dash = 'dot'

                            # Get position config with vertical offset
                            pos_config = entry_position_config[(i-1) % len(entry_position_config)]

                            fig.add_hline(
                                y=entry_price,
                                line_dash=dash,
                                line_color=line_color,
                                line_width=2,
                                annotation_text=f"E{i}: ${entry_price:.5f}",
                                annotation_position=pos_config['position'],
                                annotation=dict(
                                    bgcolor=bg_color,
                                    font=dict(color="white", size=11, family="Arial Black"),
                                    borderpad=4,
                                    yshift=pos_config['yshift']  # Vertical offset to avoid overlap
                                )
                            )

                    # Add Stop Loss (Standard 2 ATR)
                    stop_losses = enhanced.get('stop_losses', {})
                    if 'standard_2atr' in stop_losses:
                        sl_price = stop_losses['standard_2atr']['price']
                        fig.add_hline(
                            y=sl_price,
                            line_dash="dash",
                            line_color="red",
                            line_width=3,
                            annotation_text=f"SL: ${sl_price:.5f}",
                            annotation_position="bottom left",
                            annotation=dict(
                                bgcolor="rgba(220, 53, 69, 0.95)",  # Bootstrap danger red
                                font=dict(color="white", size=11, family="Arial Black"),
                                borderpad=4
                            )
                        )

                    # Add Take Profit Targets with smart positioning
                    take_profits = enhanced.get('take_profits', {})

                    # Professional color scheme with good contrast
                    tp_line_colors = {
                        'tp1_scalp': 'lightgreen',
                        'tp2_conservative': 'green',
                        'tp3_moderate': 'darkgreen',
                        'tp4_aggressive': 'lime'
                    }

                    # Dark, solid backgrounds for better text visibility
                    tp_bg_colors = {
                        'tp1_scalp': 'rgba(34, 139, 34, 0.95)',      # Forest green
                        'tp2_conservative': 'rgba(0, 128, 0, 0.95)', # Green
                        'tp3_moderate': 'rgba(0, 100, 0, 0.95)',     # Dark green
                        'tp4_aggressive': 'rgba(50, 205, 50, 0.95)' # Lime green
                    }

                    # Staggered positioning to prevent overlap
                    # Larger yshift values and side alternation for maximum separation
                    tp_position_config = [
                        {'position': 'top right', 'yshift': 15},      # TP1: far up on right
                        {'position': 'bottom left', 'yshift': -15},   # TP2: far down on left (opposite!)
                        {'position': 'top left', 'yshift': 0},        # TP3: centered on left
                        {'position': 'bottom right', 'yshift': 0}     # TP4: centered on right
                    ]

                    for idx, (tp_name, tp_data) in enumerate(take_profits.items()):
                        tp_price = tp_data['price']
                        tp_label = f"TP{idx+1}"
                        line_color = tp_line_colors.get(tp_name, 'green')
                        bg_color = tp_bg_colors.get(tp_name, 'rgba(0, 128, 0, 0.95)')

                        # Get position config for this TP
                        pos_config = tp_position_config[idx % len(tp_position_config)]

                        fig.add_hline(
                            y=tp_price,
                            line_dash="dot",
                            line_color=line_color,
                            line_width=2,
                            annotation_text=f"{tp_label}: ${tp_price:.5f}",
                            annotation_position=pos_config['position'],
                            annotation=dict(
                                bgcolor=bg_color,
                                font=dict(color="white", size=11, family="Arial Black"),
                                borderpad=4,
                                yshift=pos_config['yshift']  # Vertical offset to avoid overlap
                            )
                        )

                    fig.update_layout(
                        height=600,
                        title=f"{st.session_state.current_symbol} - {selected_tf.upper()} with Trading Levels",
                        xaxis_title="Date",
                        yaxis_title="Price",
                        xaxis_rangeslider_visible=False,
                        hovermode='x unified',
                        showlegend=True,
                        margin=dict(l=80, r=120, t=80, b=60)  # Add margins to prevent clipping
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Display detailed levels
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("#### 📍 Entry Points")
                        if entry_points:
                            for i, (entry_name, entry_data) in enumerate(entry_points.items(), 1):
                                urgency_icon = "🔵" if entry_data['urgency'] == 'NOW' else "🟡"
                                st.markdown(f"{urgency_icon} **Entry {i}**: ${entry_data['price']:.5f}")
                                st.caption(f"{entry_data['description']}")
                                st.caption(f"Urgency: {entry_data['urgency']}")
                                st.divider()

                    with col2:
                        st.markdown("#### 🛑 Stop Loss Levels")
                        if stop_losses:
                            if 'tight_1atr' in stop_losses:
                                sl = stop_losses['tight_1atr']
                                st.markdown(f"**Tight (1 ATR)**: ${sl['price']:.5f}")
                                st.caption(f"Risk: {sl['risk_pct']:.2f}%")

                            if 'standard_2atr' in stop_losses:
                                sl = stop_losses['standard_2atr']
                                st.markdown(f"⭐ **Standard (2 ATR)**: ${sl['price']:.5f}")
                                st.caption(f"Risk: {sl['risk_pct']:.2f}% (Recommended)")

                            if 'wide_3atr' in stop_losses:
                                sl = stop_losses['wide_3atr']
                                st.markdown(f"**Wide (3 ATR)**: ${sl['price']:.5f}")
                                st.caption(f"Risk: {sl['risk_pct']:.2f}%")

                            st.markdown("**Percentage-Based:**")
                            if 'percentage_2pct' in stop_losses:
                                st.caption(f"2%: ${stop_losses['percentage_2pct']['price']:.5f}")
                            if 'percentage_3pct' in stop_losses:
                                st.caption(f"3%: ${stop_losses['percentage_3pct']['price']:.5f}")
                            if 'percentage_5pct' in stop_losses:
                                st.caption(f"5%: ${stop_losses['percentage_5pct']['price']:.5f}")

                    with col3:
                        st.markdown("#### 🎯 Take Profit Targets")
                        risk_reward_ratios = enhanced.get('risk_reward_ratios', {})

                        if take_profits:
                            for tp_name, tp_data in take_profits.items():
                                tp_label = tp_name.replace('_', ' ').replace('tp', 'TP').upper()
                                rr = risk_reward_ratios.get(tp_name, 'N/A')
                                st.markdown(f"**{tp_label}**: ${tp_data['price']:.5f}")
                                st.caption(f"Gain: {tp_data['gain_pct']:.2f}% | R:R = 1:{rr}")
                                st.divider()

                        st.info("💰 Close 25% at each TP level")

                    # Buy/Sell Zones
                    st.markdown("#### 💵 Price Zones")

                    if rec in ["BUY", "STRONG BUY"]:
                        buy_range = enhanced.get('buy_range', {})
                        if buy_range:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("🟢 Strong Buy Zone", f"${buy_range.get('strong_buy', 0):.5f}")
                                st.caption("BB Lower Band")
                            with col2:
                                st.metric("🟡 Buy Zone Low", f"${buy_range.get('buy_zone_low', 0):.5f}")
                            with col3:
                                st.metric("🟡 Buy Zone High", f"${buy_range.get('buy_zone_high', 0):.5f}")

                    elif rec in ["SELL", "STRONG SELL"]:
                        sell_range = enhanced.get('sell_range', {})
                        if sell_range:
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("🟡 Sell Zone Low", f"${sell_range.get('sell_zone_low', 0):.5f}")
                            with col2:
                                st.metric("🟡 Sell Zone High", f"${sell_range.get('sell_zone_high', 0):.5f}")
                            with col3:
                                st.metric("🔴 Strong Sell Zone", f"${sell_range.get('strong_sell', 0):.5f}")
                                st.caption("BB Upper Band")

                    # Technical Indicators
                    st.markdown("#### 📈 Key Indicators")
                    indicators = enhanced.get('indicators', {})

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if indicators.get('RSI') is not None:
                            rsi_val = indicators['RSI']
                            rsi_color = "🔴" if rsi_val > 70 else ("🟢" if rsi_val < 30 else "🟡")
                            st.metric(f"{rsi_color} RSI", f"{rsi_val:.2f}")

                    with col2:
                        if indicators.get('MACD') is not None:
                            macd_val = indicators['MACD']
                            macd_color = "🟢" if macd_val > 0 else "🔴"
                            st.metric(f"{macd_color} MACD", f"{macd_val:.5f}")

                    with col3:
                        if indicators.get('Stoch_K') is not None:
                            stoch_val = indicators['Stoch_K']
                            stoch_color = "🔴" if stoch_val > 80 else ("🟢" if stoch_val < 20 else "🟡")
                            st.metric(f"{stoch_color} Stochastic K", f"{stoch_val:.2f}")

                    with col4:
                        if indicators.get('ATR') is not None:
                            st.metric("ATR", f"{indicators['ATR']:.5f}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if indicators.get('MA_20') is not None:
                            st.metric("MA 20", f"${indicators['MA_20']:.5f}")
                    with col2:
                        if indicators.get('MA_50') is not None:
                            st.metric("MA 50", f"${indicators['MA_50']:.5f}")

                    # Add trading plan option for this timeframe
                    st.divider()
                    st.markdown("#### 💼 Generate Trading Plan for This Timeframe")

                    if rec in ["BUY", "SELL", "STRONG BUY", "STRONG SELL"]:
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.info(f"💡 This timeframe shows a **{rec}** signal. You can generate a trading plan based on this specific timeframe.")

                        with col2:
                            if st.button(f"📋 Create Plan", key=f"plan_{selected_tf}"):
                                # Generate trading plan for this timeframe
                                from src.risk.risk_manager import RiskManager
                                risk_manager = RiskManager(st.session_state.analyzer.config)

                                signal = "BUY" if "BUY" in rec else "SELL"

                                # Use standard 2 ATR stop loss
                                sl_data = stop_losses.get('standard_2atr', {})
                                entry_price = current_price
                                stop_loss = sl_data.get('price', current_price)

                                # Calculate TP based on 2:1 R:R
                                risk = abs(entry_price - stop_loss)
                                if signal == "BUY":
                                    take_profit = entry_price + (risk * 2)
                                else:
                                    take_profit = entry_price - (risk * 2)

                                # Get ATR from dataframe
                                atr = df['ATR'].iloc[-1] if 'ATR' in df.columns else risk

                                # Create trade plan
                                tf_trade_plan = risk_manager.create_trade_plan(
                                    signal=signal,
                                    entry_price=entry_price,
                                    confidence=abs(score) / 5.0,  # Normalize score to 0-1
                                    account_balance=account_balance,
                                    df=df
                                )

                                st.session_state[f'tf_plan_{selected_tf}'] = tf_trade_plan

                        # Display the generated plan
                        if f'tf_plan_{selected_tf}' in st.session_state:
                            tf_plan = st.session_state[f'tf_plan_{selected_tf}']

                            if tf_plan.get('approved'):
                                st.success(f"✅ Trading Plan Generated for {selected_tf.upper()}")

                                col1, col2, col3 = st.columns(3)

                                with col1:
                                    st.metric("📍 Entry", f"${tf_plan['entry_price']:.2f}")
                                    st.metric("🛑 Stop Loss", f"${tf_plan['stop_loss']:.2f}")

                                with col2:
                                    st.metric("🎯 Take Profit", f"${tf_plan['take_profit']:.2f}")
                                    st.metric("⚖️ R:R Ratio", f"1:{tf_plan['risk_reward_ratio']:.2f}")

                                with col3:
                                    st.metric("📦 Position Size", f"{tf_plan['position_size_lots']:.2f} lots")
                                    st.metric("💰 Risk Amount", f"${tf_plan['risk_amount']:.2f}")

                                st.info(f"💡 This plan is based on the **{selected_tf.upper()}** timeframe signal only.")
                            else:
                                st.warning("⚠️ Trade not recommended by risk manager")
                                for reason in tf_plan.get('reasons', []):
                                    st.caption(f"- {reason}")
                    else:
                        st.warning(f"⚠️ No clear signal on {selected_tf.upper()} timeframe (HOLD). Try a different timeframe.")

        with tab2:
            st.subheader("Price Charts & Indicators")

            # Add combined multi-timeframe support/resistance chart
            st.markdown("### 🎯 Combined Multi-Timeframe Support & Resistance Levels")

            # Create legend columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**🟢 15-Minute Timeframe**")
                st.caption("Dotted lines: Support (S1-S4)")
                st.caption("Dashed lines: Resistance (R1-R4)")
            with col2:
                st.markdown("**🔵 1-Hour Timeframe**")
                st.caption("Dotted lines: Support (S1-S4)")
                st.caption("Dashed lines: Resistance (R1-R4)")
            with col3:
                st.markdown("**🟣 4-Hour Timeframe**")
                st.caption("Dotted lines: Support (S1-S4)")
                st.caption("Dashed lines: Resistance (R1-R4)")

            combined_fig = create_combined_sr_chart(analysis, st.session_state.current_symbol)
            st.plotly_chart(combined_fig, use_container_width=True)

            # Add summary table
            st.markdown("### 📋 Support & Resistance Levels Summary")
            st.caption("All levels sorted by price (highest to lowest)")
            sr_table = create_sr_summary_table(analysis)

            # Style the table with colors
            def highlight_type(row):
                if row['Type'] == 'Resistance':
                    return ['background-color: rgba(255, 100, 100, 0.2)'] * len(row)
                else:
                    return ['background-color: rgba(100, 255, 100, 0.2)'] * len(row)

            styled_table = sr_table.style.apply(highlight_type, axis=1)
            st.dataframe(styled_table, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("### 📊 Individual Timeframe Charts")

            # Show charts for each timeframe
            timeframes = ['1d', '4h']  # Show main timeframes

            for tf in timeframes:
                if tf in analysis['timeframe_analyses']:
                    tf_data = analysis['timeframe_analyses'][tf]
                    df = tf_data['dataframe']

                    st.markdown(f"### {tf.upper()} Timeframe")
                    fig = create_candlestick_chart(df.tail(100), st.session_state.current_symbol, tf)
                    st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.subheader("💼 Multi-Timeframe Trade Plans")

            # Check if multi-timeframe plans are available
            if analysis.get('multi_tf_trade_plans'):
                mtf_plans = analysis['multi_tf_trade_plans']

                if mtf_plans.get('approved'):
                    # Summary at the top
                    st.markdown("### 📊 Trade Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Signal", mtf_plans['signal'])
                    with col2:
                        st.metric("Confidence", f"{mtf_plans['confidence']:.1%}")
                    with col3:
                        st.metric("Entry Price", f"${mtf_plans['entry_price']:.5f}")
                    with col4:
                        st.metric("Timeframes", len(mtf_plans['timeframe_plans']))

                    st.markdown("---")

                    # Timeframe selector
                    tf_plans = mtf_plans['timeframe_plans']

                    # Create tabs for each timeframe
                    if tf_plans:
                        tf_tabs = st.tabs([f"⏰ {tf.upper()}" for tf in tf_plans.keys()])

                        for idx, (tf, plan) in enumerate(tf_plans.items()):
                            with tf_tabs[idx]:
                                # Strategy info
                                strategy = plan['trading_strategy']
                                st.markdown(f"### {strategy['style']}")

                                col1, col2 = st.columns(2)
                                with col1:
                                    st.info(f"**Holding Period:** {strategy['holding_period']}")
                                    st.info(f"**Monitoring:** {strategy['monitoring']}")
                                with col2:
                                    st.info(f"**Suitable For:** {strategy['suitable_for']}")
                                    execution = plan['expected_execution']
                                    st.success(f"**Expected Duration:** {execution['duration_readable']}")

                                st.markdown("---")

                                # Entry points
                                st.markdown("#### 🎯 Entry Points")
                                entry_cols = st.columns(3)
                                for i, (entry_name, entry_data) in enumerate(plan['entry_points'].items()):
                                    with entry_cols[i]:
                                        urgency_emoji = "⚡" if entry_data['urgency'] == 'IMMEDIATE' else "📝"
                                        st.metric(
                                            f"{urgency_emoji} {entry_name.replace('_', ' ').title()}",
                                            f"${entry_data['price']:.5f}",
                                            help=entry_data['description']
                                        )

                                # Stop Losses
                                st.markdown("#### 🛑 Stop Loss Options")
                                sl_options = []
                                for sl_name, sl_data in plan['stop_losses'].items():
                                    recommended = "⭐ " if sl_data.get('recommended') else ""
                                    sl_options.append({
                                        'Option': f"{recommended}{sl_name.replace('_', ' ').title()}",
                                        'Price': f"${sl_data['price']:.5f}",
                                        'Risk %': f"{sl_data['risk_pct']:.2f}%",
                                        'Description': sl_data['description']
                                    })
                                st.dataframe(pd.DataFrame(sl_options), use_container_width=True, hide_index=True)

                                # Take Profit Targets
                                st.markdown("#### 💰 Take Profit Targets")
                                tp_options = []
                                for tp_name, tp_data in plan['take_profits'].items():
                                    recommended = "⭐ " if tp_data.get('recommended') else ""
                                    rr = plan['risk_reward_ratios'].get(tp_name, 'N/A')
                                    tp_options.append({
                                        'Target': f"{recommended}{tp_name.replace('_', ' ').title()}",
                                        'Price': f"${tp_data['price']:.5f}",
                                        'Gain %': f"{tp_data['gain_pct']:.2f}%",
                                        'R:R': f"1:{rr}",
                                        'Close %': f"{tp_data['position_close_pct']}%",
                                        'Description': tp_data['description']
                                    })
                                st.dataframe(pd.DataFrame(tp_options), use_container_width=True, hide_index=True)

                                # Position Sizing
                                st.markdown("#### 💵 Position Sizing")
                                pos = plan['position_sizing']
                                pos_col1, pos_col2, pos_col3 = st.columns(3)
                                with pos_col1:
                                    st.metric("Position Size", f"{pos['position_size_lots']:.4f} lots")
                                with pos_col2:
                                    st.metric("Risk Amount", f"${pos['risk_amount']:.2f}")
                                with pos_col3:
                                    st.metric("Risk %", f"{pos['risk_percentage']:.2f}%")

                                # Current Indicators
                                if plan.get('current_indicators'):
                                    with st.expander("📈 Current Technical Indicators"):
                                        indicators = plan['current_indicators']
                                        ind_cols = st.columns(4)
                                        col_idx = 0
                                        for ind_name, ind_value in indicators.items():
                                            with ind_cols[col_idx % 4]:
                                                st.metric(ind_name, f"{ind_value:.5f}" if isinstance(ind_value, float) else ind_value)
                                            col_idx += 1

                else:
                    st.warning("❌ Trade Not Recommended")
                    st.markdown("**Reasons:**")
                    for reason in mtf_plans.get('reasons', []):
                        st.markdown(f"- {reason}")

            # Fallback to simple trade plan if multi-TF not available
            elif analysis.get('trade_plan'):
                st.warning("⚠️ Multi-timeframe plans not available. Showing simple trade plan.")
                tp = analysis['trade_plan']

                if tp.get('approved'):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### Entry & Exit")
                        st.metric("Entry Price", f"${tp['entry_price']:.5f}")
                        st.metric("Stop Loss", f"${tp['stop_loss']:.5f}",
                                delta=f"-{abs(tp['entry_price'] - tp['stop_loss']):.5f}")
                        st.metric("Take Profit", f"${tp['take_profit']:.5f}",
                                delta=f"+{abs(tp['take_profit'] - tp['entry_price']):.5f}")

                    with col2:
                        st.markdown("#### Position & Risk")
                        st.metric("Position Size", f"{tp['position_size_lots']:.2f} lots")
                        st.metric("Risk Amount", f"${tp['risk_amount']:.2f}",
                                delta=f"{tp['risk_percentage']:.2f}%")
                        st.metric("Potential Profit", f"${tp['potential_profit']:.2f}")
                        st.metric("Potential Loss", f"${tp['potential_loss']:.2f}")
                else:
                    st.warning("❌ Trade Not Recommended")
                    st.markdown("**Reasons:**")
                    for reason in tp.get('reasons', []):
                        st.markdown(f"- {reason}")
            else:
                st.info("No trade plan available for HOLD signal")

        with tab4:
            st.subheader("🎯 Multi-Timeframe Analysis")

            # Consensus summary
            consensus = analysis['multi_timeframe_consensus']

            # NEW: Show global reversal warnings
            if consensus.get('has_reversal_warning', False):
                st.error("⚠️ **REVERSAL ALERTS DETECTED** - Multiple timeframes showing trend reversals!")
                for rev in consensus.get('reversals_detected', []):
                    st.warning(f"🔔 **{rev['timeframe'].upper()}**: {rev['type'].replace('_', ' ').title()} (Strength: {rev['strength']:.1%}, Warning: {rev['warning_level']})")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BUY Signals", consensus['buy_timeframes'])
            with col2:
                st.metric("SELL Signals", consensus['sell_timeframes'])
            with col3:
                st.metric("HOLD Signals", consensus['hold_timeframes'])

            # Detailed breakdown
            st.markdown("#### Timeframe Breakdown")

            for tf in ['1d', '4h', '1h', '15m']:
                if tf not in analysis['timeframe_analyses']:
                    continue

                tf_data = analysis['timeframe_analyses'][tf]

                with st.expander(f"📊 {tf.upper()} Timeframe", expanded=True):
                    # NEW: Check for reversal warning
                    if tf_data.get('reversal_detection', {}).get('is_reversal', False):
                        reversal = tf_data['reversal_detection']
                        warning_emoji = '🚨' if reversal['warning_level'] == 'HIGH' else ('⚠️' if reversal['warning_level'] == 'MEDIUM' else '⚡')
                        st.warning(f"{warning_emoji} **REVERSAL DETECTED**: {reversal['reversal_type'].replace('_', ' ').title()} (Strength: {reversal['reversal_strength']:.1%})")

                    # NEW: Show enhanced signal vs original
                    if tf_data.get('signal_changed', False):
                        st.info(f"📊 **Enhanced Signal**: {tf_data.get('enhanced_signal', 'N/A')} (Confidence: {tf_data.get('signal_confidence', 0):.1%}) | Original: {tf_data.get('current_consensus', 'N/A')}")
                        st.caption(tf_data.get('signal_reasoning', 'No reasoning available'))

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Trend Strength", f"{tf_data['trend_strength']:.1%}")
                        st.metric("Momentum", tf_data['momentum'])

                        # NEW: Show historical momentum
                        if 'trend_momentum' in tf_data:
                            tm = tf_data['trend_momentum']
                            st.metric("Historical Momentum", f"{tm['direction']} ({tm['momentum_score']:.1%})")

                    with col2:
                        st.markdown("**Individual Signals:**")
                        signals = tf_data['signals']
                        for sig_name, sig_value in signals.items():
                            color = '🟢' if sig_value == 'BUY' else ('🔴' if sig_value == 'SELL' else '🟡')
                            st.markdown(f"{color} {sig_name}: **{sig_value}**")

                    with col3:
                        st.markdown("**Key Levels:**")
                        if tf_data['support_levels']:
                            st.markdown(f"Support: ${tf_data['support_levels'][0]:.5f}")
                        if tf_data['resistance_levels']:
                            st.markdown(f"Resistance: ${tf_data['resistance_levels'][0]:.5f}")

        with tab5:
            st.subheader("📊 Technical Indicator Details")

            # Get 1d data for detailed view
            if '1d' in analysis['timeframe_analyses']:
                df = analysis['timeframe_analyses']['1d']['dataframe']
                current = analysis['timeframe_analyses']['1d']['current_data']

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Momentum Indicators")
                    if current.get('rsi'):
                        st.metric("RSI", f"{current['rsi']:.2f}")
                    if current.get('macd'):
                        st.metric("MACD", f"{current['macd']:.5f}")

                with col2:
                    st.markdown("#### Volatility")
                    if current.get('atr'):
                        st.metric("ATR", f"{current['atr']:.5f}")

                # Show recent data table
                st.markdown("#### Recent Price Action")
                recent_df = df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(10)
                st.dataframe(recent_df.style.format({
                    'Open': '{:.5f}',
                    'High': '{:.5f}',
                    'Low': '{:.5f}',
                    'Close': '{:.5f}',
                    'Volume': '{:,.0f}'
                }))

    else:
        # Welcome screen
        st.info("👈 Select a symbol and click **Analyze** to get started!")

        st.markdown("""
        ### Welcome to Forex Analyzer Pro

        This professional trading analysis tool provides:

        - ✅ **Multi-Timeframe Analysis** - Analyze 1D, 4H, 1H, and 15M timeframes simultaneously
        - ✅ **Machine Learning Predictions** - AI-powered BUY/SELL/HOLD signals
        - ✅ **Technical Indicators** - MA, EMA, RSI, MACD, Stochastic, ATR, and more
        - ✅ **Risk Management** - Automated position sizing and stop loss calculation
        - ✅ **Signal Confluence** - Weighted voting across timeframes
        - ✅ **Support/Resistance** - Automatic level detection

        **Supported Assets:**
        - Forex pairs (EURUSD, GBPUSD, etc.)
        - Gold & Silver Spot (XAU_USD, XAG_USD via Oanda)
        - Other commodities (via yfinance)
        """)

if __name__ == "__main__":
    main()
