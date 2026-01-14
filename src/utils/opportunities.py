"""
Opportunities extraction and management utilities
"""
from datetime import datetime


def extract_opportunities_from_analysis(symbol, analysis):
    """Extract trading opportunities from analysis results"""
    opportunities = []

    try:
        if 'error' in analysis or not analysis.get('timeframe_analyses'):
            return opportunities

        # Extract opportunities from each timeframe
        for tf, tf_data in analysis.get('timeframe_analyses', {}).items():
            try:
                # Get signals from the timeframe data
                tf_signal_data = tf_data.get('signals', {})

                # Determine overall signal for this timeframe
                tf_signals = []
                for sig_type, sig_val in tf_signal_data.items():
                    if sig_val in ['BUY', 'SELL', 'HOLD']:
                        tf_signals.append(sig_val)

                # Count signals
                buy_count = tf_signals.count('BUY')
                sell_count = tf_signals.count('SELL')

                # Determine action and confidence
                if buy_count > sell_count:
                    action = 'BUY'
                    confidence = buy_count / len(tf_signals) if tf_signals else 0
                elif sell_count > buy_count:
                    action = 'SELL'
                    confidence = sell_count / len(tf_signals) if tf_signals else 0
                else:
                    action = 'HOLD'
                    confidence = 0.0

                # Only include BUY or SELL signals with reasonable confidence
                if action in ['BUY', 'SELL'] and confidence >= 0.4:
                    # Safely get current data
                    current_data = tf_data.get('current_data', {})

                    # Get dataframe for RSI
                    df = tf_data.get('dataframe')
                    rsi_value = 0
                    if df is not None and not df.empty and 'RSI' in df.columns:
                        rsi_value = float(df['RSI'].iloc[-1]) if len(df) > 0 else 0

                    # Build reasons list from individual signals
                    reasons = []
                    for sig_type, sig_val in tf_signal_data.items():
                        if sig_val == action:
                            reasons.append(f"{sig_type.replace('_', ' ').title()}: {sig_val}")

                    opportunity = {
                        'symbol': symbol,
                        'signal': action,
                        'timeframe': tf.upper(),
                        'confidence': float(confidence),
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'current_price': float(current_data.get('current_price', 0)),
                        'support_levels': tf_data.get('support_levels', [])[:4],  # Limit to 4
                        'resistance_levels': tf_data.get('resistance_levels', [])[:4],  # Limit to 4
                        'rsi': float(rsi_value),
                        'trend': str(tf_signal_data.get('ma_signal', 'Unknown')),
                        'momentum': str(tf_signal_data.get('macd_signal', 'Unknown')),
                        'score': float(buy_count if action == 'BUY' else sell_count),
                        'reasons': reasons
                    }

                    # Add entry price if available
                    try:
                        if 'multi_tf_trade_plans' in analysis:
                            mtf_plans = analysis['multi_tf_trade_plans']
                            if mtf_plans and mtf_plans.get('approved') and tf in mtf_plans.get('timeframe_plans', {}):
                                tf_plan = mtf_plans['timeframe_plans'][tf]
                                opportunity['entry_price'] = float(tf_plan.get('entry_price', opportunity['current_price']))
                    except Exception:
                        pass  # Entry price is optional

                    opportunities.append(opportunity)

            except Exception as e:
                # Skip this timeframe if there's an error
                continue

    except Exception as e:
        # Return empty list if extraction fails
        pass

    return opportunities


def add_opportunities_to_session(st_session_state, symbol, analysis):
    """Add detected opportunities to session state"""
    if 'opportunities' not in st_session_state:
        st_session_state.opportunities = []

    # Extract new opportunities
    new_opps = extract_opportunities_from_analysis(symbol, analysis)

    # Remove old opportunities for the same symbol to avoid duplicates
    st_session_state.opportunities = [
        opp for opp in st_session_state.opportunities
        if opp['symbol'] != symbol
    ]

    # Add new opportunities
    st_session_state.opportunities.extend(new_opps)

    # Limit to last 100 opportunities
    if len(st_session_state.opportunities) > 100:
        st_session_state.opportunities = st_session_state.opportunities[-100:]

    return len(new_opps)
