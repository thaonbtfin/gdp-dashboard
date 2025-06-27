#!/usr/bin/env python3
"""
Test script for Technical Analysis functionality
Run this to test the new technical analysis features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tastock.ui.technical_helper import TechnicalHelper

def generate_sample_data():
    """Generate sample stock data for testing."""
    
    # Generate 200 days of sample data
    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    
    # Simulate stock price with trend and volatility
    np.random.seed(42)
    base_price = 100
    trend = 0.001  # Small upward trend
    volatility = 0.02
    
    prices = [base_price]
    for i in range(1, len(dates)):
        # Random walk with trend
        change = np.random.normal(trend, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 1))  # Ensure price doesn't go negative
    
    # Create DataFrame
    df = pd.DataFrame({
        'time': dates,
        'VNINDEX': prices,
        'VCB': [p * 1.2 + np.random.normal(0, 5) for p in prices],
        'FPT': [p * 0.8 + np.random.normal(0, 3) for p in prices],
        'ACB': [p * 0.6 + np.random.normal(0, 2) for p in prices]
    })
    
    return df

def test_technical_calculations():
    """Test technical indicator calculations."""
    
    print("🧪 Testing Technical Analysis Calculations...")
    
    # Generate sample data
    df = generate_sample_data()
    print(f"✅ Generated {len(df)} days of sample data")
    
    # Test with VNINDEX data
    symbol_data = df[['time', 'VNINDEX']].copy()
    symbol_data = symbol_data.rename(columns={'VNINDEX': 'price'})
    
    # Test moving averages
    symbol_data['MA5'] = symbol_data['price'].rolling(window=5).mean()
    symbol_data['MA20'] = symbol_data['price'].rolling(window=20).mean()
    symbol_data['MA50'] = symbol_data['price'].rolling(window=50).mean()
    
    print(f"✅ Calculated moving averages")
    print(f"   - MA5: {symbol_data['MA5'].iloc[-1]:.2f}")
    print(f"   - MA20: {symbol_data['MA20'].iloc[-1]:.2f}")
    print(f"   - MA50: {symbol_data['MA50'].iloc[-1]:.2f}")
    
    # Test RSI calculation
    def calculate_rsi(prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    symbol_data['RSI'] = calculate_rsi(symbol_data['price'])
    print(f"✅ Calculated RSI: {symbol_data['RSI'].iloc[-1]:.2f}")
    
    # Test MACD
    symbol_data['EMA12'] = symbol_data['price'].ewm(span=12).mean()
    symbol_data['EMA26'] = symbol_data['price'].ewm(span=26).mean()
    symbol_data['MACD'] = symbol_data['EMA12'] - symbol_data['EMA26']
    symbol_data['MACD_Signal'] = symbol_data['MACD'].ewm(span=9).mean()
    
    print(f"✅ Calculated MACD: {symbol_data['MACD'].iloc[-1]:.4f}")
    print(f"   - Signal: {symbol_data['MACD_Signal'].iloc[-1]:.4f}")
    
    # Test Bollinger Bands
    symbol_data['BB_Middle'] = symbol_data['price'].rolling(window=20).mean()
    bb_std = symbol_data['price'].rolling(window=20).std()
    symbol_data['BB_Upper'] = symbol_data['BB_Middle'] + (bb_std * 2)
    symbol_data['BB_Lower'] = symbol_data['BB_Middle'] - (bb_std * 2)
    
    print(f"✅ Calculated Bollinger Bands:")
    print(f"   - Upper: {symbol_data['BB_Upper'].iloc[-1]:.2f}")
    print(f"   - Middle: {symbol_data['BB_Middle'].iloc[-1]:.2f}")
    print(f"   - Lower: {symbol_data['BB_Lower'].iloc[-1]:.2f}")
    
    return symbol_data

def test_technical_helper():
    """Test TechnicalHelper functions."""
    
    print("\n🧪 Testing TechnicalHelper Functions...")
    
    # Generate test data
    df = generate_sample_data()
    symbol_data = df[['time', 'VNINDEX']].copy()
    symbol_data = symbol_data.rename(columns={'VNINDEX': 'price'})
    
    # Add some indicators for testing
    symbol_data['MA20'] = symbol_data['price'].rolling(window=20).mean()
    symbol_data['RSI'] = 65.5  # Sample RSI value
    
    # Test support/resistance calculation
    support, resistance = TechnicalHelper.calculate_support_resistance(symbol_data)
    print(f"✅ Support/Resistance calculation:")
    print(f"   - Support: {support:.2f}" if support else "   - Support: N/A")
    print(f"   - Resistance: {resistance:.2f}" if resistance else "   - Resistance: N/A")
    
    # Test trend strength
    symbol_data['MA5'] = symbol_data['price'].rolling(window=5).mean()
    symbol_data['MA10'] = symbol_data['price'].rolling(window=10).mean()
    symbol_data['MA50'] = symbol_data['price'].rolling(window=50).mean()
    
    trend_strength = TechnicalHelper.calculate_trend_strength(symbol_data)
    print(f"✅ Trend strength: {trend_strength}")
    
    # Test volatility rating
    volatility_rating, volatility_value = TechnicalHelper.calculate_volatility_rating(symbol_data)
    print(f"✅ Volatility: {volatility_rating} ({volatility_value:.2f}%)")
    
    # Test market sentiment
    sentiment, sentiment_icon = TechnicalHelper.get_market_sentiment(65.5, 0.1, 0.6)
    print(f"✅ Market sentiment: {sentiment_icon} {sentiment}")
    
    # Test technical summary
    tech_summary = TechnicalHelper.create_technical_summary_metrics(symbol_data, 'VNINDEX')
    print(f"✅ Technical summary created for {tech_summary['symbol']}")
    print(f"   - Current price: {tech_summary['current_price']:.2f}")
    print(f"   - Trend: {tech_summary['trend_strength']}")
    print(f"   - Sentiment: {tech_summary['sentiment_icon']} {tech_summary['market_sentiment']}")
    
    return True

def test_signal_generation():
    """Test signal generation logic."""
    
    print("\n🧪 Testing Signal Generation...")
    
    # Create sample indicators data
    indicators_data = [
        {'Chỉ báo': 'MA(20)', 'Giá trị': '105.50', 'Tín hiệu': '🟢 MUA', 'Loại': 'Đường trung bình'},
        {'Chỉ báo': 'RSI(14)', 'Giá trị': '35.20', 'Tín hiệu': '🟢 MUA', 'Loại': 'Dao động'},
        {'Chỉ báo': 'MACD', 'Giá trị': '0.0150', 'Tín hiệu': '🔴 BÁN', 'Loại': 'Momentum'},
        {'Chỉ báo': 'Bollinger Bands', 'Giá trị': '110.00/100.00', 'Tín hiệu': '🟡 TRUNG TÍNH', 'Loại': 'Volatility'}
    ]
    
    # Count signals
    buy_signals = sum(1 for item in indicators_data if "MUA" in item['Tín hiệu'])
    sell_signals = sum(1 for item in indicators_data if "BÁN" in item['Tín hiệu'])
    neutral_signals = len(indicators_data) - buy_signals - sell_signals
    
    print(f"✅ Signal counting:")
    print(f"   - Buy signals: {buy_signals}")
    print(f"   - Sell signals: {sell_signals}")
    print(f"   - Neutral signals: {neutral_signals}")
    
    # Determine overall recommendation
    if buy_signals > sell_signals:
        recommendation = "MUA"
    elif sell_signals > buy_signals:
        recommendation = "BÁN"
    else:
        recommendation = "TRUNG TÍNH"
    
    confidence = max(buy_signals, sell_signals) / len(indicators_data) * 100
    
    print(f"✅ Overall recommendation: {recommendation}")
    print(f"✅ Confidence level: {confidence:.0f}%")
    
    return True

def main():
    """Run all tests."""
    
    print("🚀 Starting Technical Analysis Tests...\n")
    
    try:
        # Test 1: Technical calculations
        symbol_data = test_technical_calculations()
        
        # Test 2: Helper functions
        test_technical_helper()
        
        # Test 3: Signal generation
        test_signal_generation()
        
        print("\n✅ All tests completed successfully!")
        print("\n📊 Sample data summary:")
        print(f"   - Data points: {len(symbol_data)}")
        print(f"   - Date range: {symbol_data['time'].min().date()} to {symbol_data['time'].max().date()}")
        print(f"   - Price range: {symbol_data['price'].min():.2f} - {symbol_data['price'].max():.2f}")
        
        # Save sample data for manual testing
        output_file = "sample_technical_data.csv"
        sample_df = pd.DataFrame({
            'time': symbol_data['time'].dt.strftime('%Y%m%d').astype(int),
            'VNINDEX': symbol_data['price'],
            'VCB': symbol_data['price'] * 1.1,
            'FPT': symbol_data['price'] * 0.9
        })
        sample_df.to_csv(output_file, index=False)
        print(f"\n💾 Sample data saved to: {output_file}")
        print("   You can use this file to test the Streamlit app manually")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)