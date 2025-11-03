"""
Recommendation Formatter
Format and display enhanced recommendations in a readable format
"""

from typing import Dict


class RecommendationFormatter:
    """Format enhanced recommendations for display"""

    @staticmethod
    def format_enhanced_recommendation(enhanced_rec: Dict, symbol: str) -> str:
        """
        Format enhanced recommendation for CLI display

        Args:
            enhanced_rec: Enhanced recommendation dictionary
            symbol: Trading symbol

        Returns:
            Formatted string
        """
        output = []
        output.append("=" * 90)
        output.append(f"📊 {enhanced_rec['timeframe'].upper()} TIMEFRAME - ENHANCED ANALYSIS")
        output.append("=" * 90)

        # Current price and recommendation
        rec = enhanced_rec['recommendation']
        rec_symbol = "🟢" if "BUY" in rec else "🔴" if "SELL" in rec else "🟡"
        output.append(f"\n{rec_symbol} RECOMMENDATION: {rec}")
        output.append(f"   Signal Score: {enhanced_rec['score']}")

        # OHLC data
        ohlc = enhanced_rec['ohlc']
        output.append(f"\n💰 CURRENT PRICE LEVELS:")
        output.append(f"   Open:  ${ohlc['open']:.5f}")
        output.append(f"   High:  ${ohlc['high']:.5f}")
        output.append(f"   Low:   ${ohlc['low']:.5f}")
        output.append(f"   Close: ${ohlc['close']:.5f}")

        # Entry points
        entry_points = enhanced_rec.get('entry_points', {})
        if entry_points:
            output.append(f"\n📍 ENTRY POINTS:")
            for i, (entry_name, entry_data) in enumerate(entry_points.items(), 1):
                urgency_icon = "🔵" if entry_data['urgency'] == 'NOW' else "🟡" if entry_data['urgency'] == 'LIMIT ORDER' else "⚪"
                output.append(f"   {urgency_icon} Entry {i}: ${entry_data['price']:.5f}")
                output.append(f"      {entry_data['description']}")
                output.append(f"      Urgency: {entry_data['urgency']}")

        # Stop losses
        stop_losses = enhanced_rec.get('stop_losses', {})
        if stop_losses:
            output.append(f"\n🛑 STOP LOSS LEVELS:")
            if 'tight_1atr' in stop_losses:
                sl = stop_losses['tight_1atr']
                output.append(f"   Tight (1 ATR):       ${sl['price']:.5f} - {sl['description']}")
                output.append(f"                        Risk: {sl['risk_pct']:.2f}%")

            if 'standard_2atr' in stop_losses:
                sl = stop_losses['standard_2atr']
                output.append(f"   📍 Standard (2 ATR):  ${sl['price']:.5f} - {sl['description']} ⭐")
                output.append(f"                        Risk: {sl['risk_pct']:.2f}%")

            if 'wide_3atr' in stop_losses:
                sl = stop_losses['wide_3atr']
                output.append(f"   Wide (3 ATR):        ${sl['price']:.5f} - {sl['description']}")
                output.append(f"                        Risk: {sl['risk_pct']:.2f}%")

            output.append(f"\n   💯 Percentage-Based Stop Loss:")
            if 'percentage_2pct' in stop_losses:
                output.append(f"      2% Stop Loss:     ${stop_losses['percentage_2pct']['price']:.5f}")
            if 'percentage_3pct' in stop_losses:
                output.append(f"      3% Stop Loss:     ${stop_losses['percentage_3pct']['price']:.5f}")
            if 'percentage_5pct' in stop_losses:
                output.append(f"      5% Stop Loss:     ${stop_losses['percentage_5pct']['price']:.5f}")

        # Take profits
        take_profits = enhanced_rec.get('take_profits', {})
        risk_reward_ratios = enhanced_rec.get('risk_reward_ratios', {})

        if take_profits:
            output.append(f"\n🎯 TAKE PROFIT TARGETS:")

            if 'tp1_scalp' in take_profits:
                tp = take_profits['tp1_scalp']
                rr = risk_reward_ratios.get('tp1_scalp', 'N/A')
                output.append(f"   TP1 (1 ATR):         ${tp['price']:.5f} - {tp['description']}")
                output.append(f"                        Gain: {tp['gain_pct']:.2f}% | R:R = 1:{rr}")

            if 'tp2_conservative' in take_profits:
                tp = take_profits['tp2_conservative']
                rr = risk_reward_ratios.get('tp2_conservative', 'N/A')
                output.append(f"   TP2 (2 ATR):         ${tp['price']:.5f} - {tp['description']}")
                output.append(f"                        Gain: {tp['gain_pct']:.2f}% | R:R = 1:{rr}")

            if 'tp3_moderate' in take_profits:
                tp = take_profits['tp3_moderate']
                rr = risk_reward_ratios.get('tp3_moderate', 'N/A')
                output.append(f"   TP3 (3 ATR):         ${tp['price']:.5f} - {tp['description']}")
                output.append(f"                        Gain: {tp['gain_pct']:.2f}% | R:R = 1:{rr}")

            if 'tp4_aggressive' in take_profits:
                tp = take_profits['tp4_aggressive']
                rr = risk_reward_ratios.get('tp4_aggressive', 'N/A')
                output.append(f"   TP4 (5 ATR):         ${tp['price']:.5f} - {tp['description']}")
                output.append(f"                        Gain: {tp['gain_pct']:.2f}% | R:R = 1:{rr}")

            output.append(f"\n   💰 POSITION SIZING STRATEGY:")
            output.append(f"      • Close 25% at TP1 (secure quick profit)")
            output.append(f"      • Close 25% at TP2 (lock in gains)")
            output.append(f"      • Close 25% at TP3 (take moderate profit)")
            output.append(f"      • Let 25% run to TP4 (maximize potential)")

        # Buy/Sell ranges
        if rec in ["BUY", "STRONG BUY"]:
            buy_range = enhanced_rec.get('buy_range', {})
            output.append(f"\n💵 BUY PRICE ZONES:")
            output.append(f"   🟢 Strong Buy Zone:  ${buy_range.get('strong_buy', 0):.5f} (BB Lower)")
            output.append(f"   🟡 Buy Zone Low:     ${buy_range.get('buy_zone_low', 0):.5f}")
            output.append(f"   🟡 Buy Zone High:    ${buy_range.get('buy_zone_high', 0):.5f}")

        elif rec in ["SELL", "STRONG SELL"]:
            sell_range = enhanced_rec.get('sell_range', {})
            output.append(f"\n💵 SELL PRICE ZONES:")
            output.append(f"   🟡 Sell Zone Low:    ${sell_range.get('sell_zone_low', 0):.5f}")
            output.append(f"   🟡 Sell Zone High:   ${sell_range.get('sell_zone_high', 0):.5f}")
            output.append(f"   🔴 Strong Sell Zone: ${sell_range.get('strong_sell', 0):.5f} (BB Upper)")

        # Technical indicators
        indicators = enhanced_rec.get('indicators', {})
        output.append(f"\n📈 KEY INDICATORS:")
        if indicators.get('RSI') is not None:
            output.append(f"   RSI: {indicators['RSI']:.2f}")
        if indicators.get('MACD') is not None:
            output.append(f"   MACD: {indicators['MACD']:.5f}")
        if indicators.get('Stoch_K') is not None:
            output.append(f"   Stochastic K: {indicators['Stoch_K']:.2f}")
        if indicators.get('ATR') is not None:
            output.append(f"   ATR: {indicators['ATR']:.5f}")
        if indicators.get('MA_20') is not None:
            output.append(f"   MA 20: ${indicators['MA_20']:.5f}")
        if indicators.get('MA_50') is not None:
            output.append(f"   MA 50: ${indicators['MA_50']:.5f}")

        output.append("")
        return "\n".join(output)

    @staticmethod
    def format_multi_timeframe_summary(timeframe_analyses: Dict, symbol: str) -> str:
        """
        Format summary table of all timeframes

        Args:
            timeframe_analyses: Dictionary of timeframe analyses
            symbol: Trading symbol

        Returns:
            Formatted summary string
        """
        output = []
        output.append("\n" + "=" * 120)
        output.append(f"📊 MULTI-TIMEFRAME SUMMARY - {symbol}")
        output.append("=" * 120)

        # Table header
        output.append(f"{'Timeframe':<12} {'Recommendation':<15} {'Score':<7} {'Current Price':<15} {'Stop Loss':<15} {'Target (TP1)':<15}")
        output.append("-" * 120)

        # Table rows
        for tf, analysis in timeframe_analyses.items():
            enhanced = analysis.get('enhanced_recommendation', {})
            if enhanced:
                rec = enhanced.get('recommendation', 'N/A')
                score = enhanced.get('score', 0)
                price = enhanced.get('current_price', 0)

                # Get stop loss
                stop_losses = enhanced.get('stop_losses', {})
                sl_price = stop_losses.get('standard_2atr', {}).get('price', 0)

                # Get TP1
                take_profits = enhanced.get('take_profits', {})
                tp1_price = take_profits.get('tp1_scalp', {}).get('price', 0) if take_profits else 0

                rec_display = f"{rec:<15}"
                output.append(f"{tf.upper():<12} {rec_display} {score:<7} ${price:<14.5f} ${sl_price:<14.5f} ${tp1_price:<14.5f}")

        output.append("=" * 120)
        output.append("")

        return "\n".join(output)
