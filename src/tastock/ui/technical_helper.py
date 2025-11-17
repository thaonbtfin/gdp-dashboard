"""
Technical Analysis Helper Module

This module provides additional helper functions for technical analysis calculations
and display formatting similar to CafeF's interface.
"""

import pandas as pd
import numpy as np
import streamlit as st


class TechnicalHelper:
    """Helper class for technical analysis calculations and formatting."""
    
    @staticmethod
    def load_custom_css():
        """Load custom CSS for technical analysis interface."""
        css_content = """
        <style>
        .technical-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            color: white;
        }
        
        .price-display {
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
        }
        
        .price-positive { color: #4CAF50; }
        .price-negative { color: #f44336; }
        .price-neutral { color: #ff9800; }
        
        .signal-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid;
        }
        
        .signal-buy { border-left-color: #4CAF50; }
        .signal-sell { border-left-color: #f44336; }
        .signal-neutral { border-left-color: #ff9800; }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-top: 4px solid #2196F3;
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .summary-recommendation {
            background: linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        
        .indicator-table {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        @media (max-width: 768px) {
            .price-display { font-size: 1.8em; }
            .metric-grid { grid-template-columns: 1fr; }
            .technical-container { padding: 15px; }
        }
        </style>
        """
        st.markdown(css_content, unsafe_allow_html=True)
    
    @staticmethod
    def format_price_display(current_price, price_change, price_change_pct):
        """Format price display with styling."""
        if price_change >= 0:
            color_class = "price-positive"
            arrow = "↗"
        else:
            color_class = "price-negative"
            arrow = "↘"
        
        return f"""
        <div class="price-display {color_class}">
            {current_price:,.2f} VND
            <br>
            <small>{arrow} {price_change:+,.2f} ({price_change_pct:+.2f}%)</small>
        </div>
        """
    
    @staticmethod
    def create_signal_summary_card(signal_type, count, description):
        """Create a styled signal summary card."""
        if signal_type == "BUY":
            color = "#4CAF50"
            icon = "📈"
        elif signal_type == "SELL":
            color = "#f44336"
            icon = "📉"
        else:
            color = "#ff9800"
            icon = "⚖️"
        
        return f"""
        <div class="metric-card" style="border-top-color: {color};">
            <div class="metric-label">{icon} {description}</div>
            <div class="metric-value" style="color: {color};">{count}</div>
        </div>
        """
    
    @staticmethod
    def create_recommendation_card(recommendation, buy_count, sell_count, confidence):
        """Create overall recommendation card."""
        if recommendation == "MUA":
            bg_color = "linear-gradient(45deg, #4CAF50 30%, #45a049 90%)"
            icon = "🚀"
        elif recommendation == "BÁN":
            bg_color = "linear-gradient(45deg, #f44336 30%, #d32f2f 90%)"
            icon = "⚠️"
        else:
            bg_color = "linear-gradient(45deg, #ff9800 30%, #f57c00 90%)"
            icon = "⚖️"
        
        return f"""
        <div class="summary-recommendation" style="background: {bg_color};">
            <h2>{icon} KHUYẾN NGHỊ: {recommendation}</h2>
            <p style="font-size: 1.2em; margin: 15px 0;">
                {buy_count} tín hiệu mua • {sell_count} tín hiệu bán
            </p>
            <p style="font-size: 1em; opacity: 0.9;">
                Độ tin cậy: {confidence:.0f}%
            </p>
        </div>
        """
    
    @staticmethod
    def calculate_support_resistance(df, window=20):
        """Calculate support and resistance levels."""
        if len(df) < window:
            return None, None
        
        # Calculate rolling min/max
        rolling_min = df['price'].rolling(window=window).min()
        rolling_max = df['price'].rolling(window=window).max()
        
        # Find recent support/resistance
        recent_support = rolling_min.tail(5).min()
        recent_resistance = rolling_max.tail(5).max()
        
        return recent_support, recent_resistance
    
    @staticmethod
    def calculate_trend_strength(df):
        """Calculate trend strength based on moving averages alignment."""
        if len(df) < 50:
            return "Không đủ dữ liệu"
        
        latest = df.iloc[-1]
        
        # Check MA alignment
        mas = ['MA5', 'MA10', 'MA20', 'MA50']
        available_mas = [ma for ma in mas if ma in df.columns and not pd.isna(latest[ma])]
        
        if len(available_mas) < 3:
            return "Yếu"
        
        # Check if MAs are in ascending order (bullish) or descending (bearish)
        ma_values = [latest[ma] for ma in available_mas]
        
        if all(ma_values[i] >= ma_values[i+1] for i in range(len(ma_values)-1)):
            return "Tăng mạnh"
        elif all(ma_values[i] <= ma_values[i+1] for i in range(len(ma_values)-1)):
            return "Giảm mạnh"
        else:
            return "Trung tính"
    
    @staticmethod
    def format_indicator_table(indicators_data):
        """Format indicator table with enhanced styling."""
        if not indicators_data:
            return None
        
        df = pd.DataFrame(indicators_data)
        
        # Apply styling
        def style_signals(val):
            if 'MUA' in str(val):
                return 'background-color: #e8f5e8; color: #2e7d32; font-weight: bold; padding: 8px;'
            elif 'BÁN' in str(val):
                return 'background-color: #ffebee; color: #c62828; font-weight: bold; padding: 8px;'
            elif 'TRUNG TÍNH' in str(val):
                return 'background-color: #fff3e0; color: #ef6c00; font-weight: bold; padding: 8px;'
            return 'padding: 8px;'
        
        def style_values(val):
            return 'text-align: center; padding: 8px; font-family: monospace;'
        
        styled_df = df.style.map(style_signals, subset=['Tín hiệu'])
        styled_df = styled_df.map(style_values, subset=['Giá trị'])
        
        return styled_df
    
    @staticmethod
    def calculate_volatility_rating(df, period=20):
        """Calculate volatility rating."""
        if len(df) < period:
            return "N/A", 0
        
        returns = df['price'].pct_change().dropna()
        volatility = returns.tail(period).std() * np.sqrt(252) * 100  # Annualized
        
        if volatility < 15:
            return "Thấp", volatility
        elif volatility < 30:
            return "Trung bình", volatility
        elif volatility < 50:
            return "Cao", volatility
        else:
            return "Rất cao", volatility
    
    @staticmethod
    def get_market_sentiment(rsi, macd_histogram, bb_position):
        """Calculate overall market sentiment."""
        sentiment_score = 0
        
        # RSI contribution
        if rsi < 30:
            sentiment_score += 2  # Oversold, bullish
        elif rsi > 70:
            sentiment_score -= 2  # Overbought, bearish
        
        # MACD contribution
        if macd_histogram > 0:
            sentiment_score += 1
        else:
            sentiment_score -= 1
        
        # Bollinger Bands contribution
        if bb_position < 0.2:  # Near lower band
            sentiment_score += 1
        elif bb_position > 0.8:  # Near upper band
            sentiment_score -= 1
        
        if sentiment_score >= 2:
            return "Tích cực", "🟢"
        elif sentiment_score <= -2:
            return "Tiêu cực", "🔴"
        else:
            return "Trung tính", "🟡"
    
    @staticmethod
    def create_technical_summary_metrics(df, symbol):
        """Create comprehensive technical summary metrics."""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        
        # Calculate additional metrics
        support, resistance = TechnicalHelper.calculate_support_resistance(df)
        trend_strength = TechnicalHelper.calculate_trend_strength(df)
        volatility_rating, volatility_value = TechnicalHelper.calculate_volatility_rating(df)
        
        # Calculate Bollinger Band position
        if all(col in df.columns for col in ['BB_Upper', 'BB_Lower']):
            bb_range = latest['BB_Upper'] - latest['BB_Lower']
            bb_position = (latest['price'] - latest['BB_Lower']) / bb_range if bb_range > 0 else 0.5
        else:
            bb_position = 0.5
        
        # Market sentiment
        rsi = latest.get('RSI', 50)
        macd_hist = latest.get('MACD_Histogram', 0)
        sentiment, sentiment_icon = TechnicalHelper.get_market_sentiment(rsi, macd_hist, bb_position)
        
        return {
            'symbol': symbol,
            'current_price': latest['price'],
            'support_level': support,
            'resistance_level': resistance,
            'trend_strength': trend_strength,
            'volatility_rating': volatility_rating,
            'volatility_value': volatility_value,
            'market_sentiment': sentiment,
            'sentiment_icon': sentiment_icon,
            'bb_position': bb_position * 100  # Convert to percentage
        }