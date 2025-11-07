"""
Generate Investment Signals from existing performance data
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os

def calculate_market_direction(vnindex_row):
    """Calculate market direction from VN-Index data"""
    if vnindex_row is None:
        return {
            'direction': 'UNKNOWN',
            'strength': 0,
            'signal': 'NEUTRAL'
        }
    
    # Get VN-Index metrics
    current_price = vnindex_row['sma_20_current']  # Current price proxy
    sma_50 = vnindex_row['sma_50_current']
    annual_return = vnindex_row['annualized_return_pct']
    rsi = vnindex_row['rsi_current']
    
    # Calculate trend direction
    if current_price > sma_50 and annual_return > 5:
        direction = 'UPTREND'
        strength = min(annual_return, 30)  # Cap at 30%
    elif current_price < sma_50 and annual_return < -5:
        direction = 'DOWNTREND'
        strength = min(abs(annual_return), 30)
    else:
        direction = 'SIDEWAYS'
        strength = abs(annual_return)
    
    return {
        'direction': direction,
        'strength': round(strength, 1),
        'signal': 'POSITIVE' if direction == 'UPTREND' else 'NEGATIVE' if direction == 'DOWNTREND' else 'NEUTRAL',
        'vnindex_return': annual_return,
        'vnindex_rsi': rsi
    }

def calculate_relative_strength(annual_return, market_return):
    """Calculate Relative Strength Rating (1-99)"""
    if market_return == 0:
        return 50
    
    # Calculate relative performance vs market
    relative_performance = annual_return / market_return
    
    # Convert to 1-99 scale with proper distribution
    if relative_performance >= 2.0:  # 2x market performance
        rs_rating = 99
    elif relative_performance >= 1.5:  # 1.5x market
        rs_rating = 90 + (relative_performance - 1.5) * 18  # 90-99
    elif relative_performance >= 1.0:  # Equal to market
        rs_rating = 50 + (relative_performance - 1.0) * 80  # 50-90
    elif relative_performance >= 0.5:  # Half market performance
        rs_rating = 20 + (relative_performance - 0.5) * 60  # 20-50
    elif relative_performance >= 0:  # Positive but weak
        rs_rating = 10 + relative_performance * 20  # 10-20
    else:  # Negative performance
        rs_rating = max(1, 10 + relative_performance * 10)  # 1-10
    
    return round(min(99, max(1, rs_rating)), 1)

def generate_value_signals(row):
    """Generate Value Investing signals"""
    # Estimate financial ratios from available data
    annual_return = row['annualized_return_pct']
    volatility = row['annual_std_dev_pct']
    
    # Estimate P/E based on return and volatility (higher return, lower volatility = lower P/E)
    if annual_return > 20:
        pe_ratio = max(8, 20 - annual_return * 0.3)
    elif annual_return > 0:
        pe_ratio = 15 + (20 - annual_return) * 0.5
    else:
        pe_ratio = 25 + abs(annual_return) * 0.5
    
    # Estimate P/B (lower for value stocks)
    pb_ratio = max(0.5, 2.5 - annual_return * 0.05)
    
    # Estimate ROE from returns (conservative estimate)
    roe = max(0, abs(annual_return) * 0.7)
    
    # Estimate Debt/Equity (higher volatility suggests higher leverage)
    debt_equity = min(2.0, 0.3 + volatility * 0.02)
    
    score = 0
    reasons = []
    
    # P/E analysis
    if pe_ratio < 15:
        reasons.append("P/E < 15: Hấp dẫn")
        score += 2
    elif pe_ratio > 25:
        reasons.append("P/E > 25: Đắt")
        score -= 1
    
    # ROE analysis (using annualized return as proxy)
    if roe > 15:
        reasons.append("ROE > 15%: Tốt")
        score += 2
    elif roe < 10:
        reasons.append("ROE < 10%: Yếu")
        score -= 1
    
    # Volatility analysis (lower is better for value)
    if row['annual_std_dev_pct'] < 30:
        reasons.append("Volatility thấp: Ổn định")
        score += 1
    elif row['annual_std_dev_pct'] > 50:
        reasons.append("Volatility cao: Rủi ro")
        score -= 1
    
    # Ensure we always have at least one reason
    if not reasons:
        if score > 0:
            reasons.append("Các chỉ số tài chính tích cực")
        elif score < 0:
            reasons.append("Các chỉ số tài chính tiêu cực")
        else:
            reasons.append("Các chỉ số tài chính trung tính")
    
    if score >= 3:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    return {
        'signal': signal,
        'score': score,
        'reasons': '; '.join(reasons),
        'pe_ratio': pe_ratio,
        'pb_ratio': pb_ratio,
        'roe_estimate': roe
    }

def generate_canslim_signals(row, market_direction):
    """Generate CANSLIM signals"""
    score = 0
    reasons = []
    
    # Current/Annual Earnings (using annualized return)
    if row['annualized_return_pct'] >= 25:
        reasons.append("Return ≥25%: Tốt")
        score += 2
    elif row['annualized_return_pct'] < 0:
        reasons.append("Return âm: Xấu")
        score -= 2
    
    # Supply & Demand (using volatility as proxy for volume activity)
    if row['annual_std_dev_pct'] > 35:  # High volatility = high activity
        reasons.append("Volatility cao: Hoạt động mạnh")
        score += 1
    
    # Leader or Laggard (using relative strength)
    market_return = market_direction.get('vnindex_return', 13.0)
    rs_rating = calculate_relative_strength(row['annualized_return_pct'], market_return)
    if rs_rating >= 80:
        reasons.append("RS ≥80: Dẫn đầu")
        score += 2
    elif rs_rating <= 30:
        reasons.append("RS ≤30: Tụt hậu")
        score -= 1
    
    # Market Direction
    if market_direction['direction'] == 'UPTREND':
        reasons.append("Thị trường tăng: Tốt")
        score += 2
    elif market_direction['direction'] == 'DOWNTREND':
        reasons.append("Thị trường giảm: Xấu")
        score -= 2
    
    # Ensure we always have at least one reason
    if not reasons:
        if score > 0:
            reasons.append("Tín hiệu CANSLIM tích cực")
        elif score < 0:
            reasons.append("Tín hiệu CANSLIM tiêu cực")
        else:
            reasons.append("Tín hiệu CANSLIM trung tính")
    
    if score >= 4:
        signal = "BUY"
    elif score <= -3:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    return {
        'signal': signal,
        'score': score,
        'reasons': '; '.join(reasons),
        'rs_rating': rs_rating
    }

def generate_technical_signals(row, ma_data=None):
    """Generate Technical Analysis signals"""
    score = 0
    reasons = []
    
    # RSI analysis
    rsi = row['rsi_current']
    if rsi < 30:
        reasons.append("RSI < 30: Quá bán")
        score += 2
    elif rsi > 70:
        reasons.append("RSI > 70: Quá mua")
        score -= 2
    elif 40 <= rsi <= 60:
        reasons.append("RSI trung tính: Ổn định")
        score += 1
    
    # Price vs SMA20
    price_vs_sma20 = row['price_vs_sma20_pct']
    if price_vs_sma20 > 5:
        reasons.append("Giá > SMA20 +5%: Mạnh")
        score += 1
    elif price_vs_sma20 < -5:
        reasons.append("Giá < SMA20 -5%: Yếu")
        score -= 1
    
    # Moving Average trend analysis
    if ma_data:
        current_price = ma_data['current_price']
        sma_50 = ma_data['sma_50']
        sma_200 = ma_data['sma_200']
        
        if current_price > sma_50 > sma_200:
            reasons.append("Giá > MA50 > MA200: Xu hướng tăng mạnh")
            score += 2
        elif current_price < sma_50 < sma_200:
            reasons.append("Giá < MA50 < MA200: Xu hướng giảm")
            score -= 2
        elif current_price > sma_50:
            reasons.append("Giá > MA50: Tích cực")
            score += 1
    
    # Volatility (for trend strength)
    if row['annual_std_dev_pct'] < 25:
        reasons.append("Volatility thấp: Xu hướng ổn định")
        score += 1
    elif row['annual_std_dev_pct'] > 60:
        reasons.append("Volatility cao: Không ổn định")
        score -= 1
    
    # Ensure we always have at least one reason
    if not reasons:
        if score > 0:
            reasons.append("Tín hiệu kỹ thuật tích cực")
        elif score < 0:
            reasons.append("Tín hiệu kỹ thuật tiêu cực")
        else:
            reasons.append("Tín hiệu kỹ thuật trung tính")
    
    if score >= 3:
        signal = "BUY"
    elif score <= -3:
        signal = "SELL"
    else:
        signal = "HOLD"
    
    return {
        'signal': signal,
        'score': score,
        'reasons': '; '.join(reasons)
    }

def generate_combined_signal(value_signal, canslim_signal, technical_signal):
    """Generate combined signal with weights"""
    signal_weights = {'BUY': 1, 'HOLD': 0, 'SELL': -1}
    
    total_score = (
        signal_weights[value_signal['signal']] * 2 +      # Value weight: 2
        signal_weights[canslim_signal['signal']] * 1.5 +  # CANSLIM weight: 1.5
        signal_weights[technical_signal['signal']] * 1    # Technical weight: 1
    )
    
    if total_score >= 2:
        final_signal = "BUY"
    elif total_score <= -2:
        final_signal = "SELL"
    else:
        final_signal = "HOLD"
    
    return {
        'final_signal': final_signal,
        'total_score': total_score,
        'confidence': min(100, abs(total_score) * 25)  # Confidence level
    }

def main():
    """Generate investment signals from existing performance data"""
    
    # Get script directory and project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '../../..')
    
    # Read existing performance data
    perf_file = os.path.join(project_root, 'data/perf_all_symbols.csv')
    
    if not os.path.exists(perf_file):
        print(f"❌ File not found: {perf_file}")
        return
    
    df = pd.read_csv(perf_file)
    print(f"📊 Loaded {len(df)} symbols from {perf_file}")
    
    # Get VN-Index data for market direction
    vnindex_row = df[df['symbol'] == 'VNINDEX']
    if not vnindex_row.empty:
        vnindex_data = vnindex_row.iloc[0]
        market_direction = calculate_market_direction(vnindex_data)
    else:
        market_direction = calculate_market_direction(None)
    
    print(f"📈 Market Direction: {market_direction['direction']} ({market_direction['strength']}%)")
    print(f"📊 VN-Index Return: {market_direction.get('vnindex_return', 'N/A')}%")
    
    # Generate signals for each stock
    results = []
    
    for idx, row in df.iterrows():
        symbol = row['symbol']
        
        # Skip VN-Index
        if symbol == 'VNINDEX':
            continue
        
        print(f"🔍 Analyzing {symbol}...")
        
        # Prepare MA data for technical analysis
        current_price = row['sma_20_current']
        sma_50 = row['sma_50_current']
        annual_return = row['annualized_return_pct']
        ma_200 = current_price * (1 - annual_return/100 * 0.67)  # Estimate MA200
        
        ma_data = {
            'current_price': current_price,
            'sma_50': sma_50,
            'sma_200': ma_200
        }
        
        # Generate individual signals
        value_signals = generate_value_signals(row)
        canslim_signals = generate_canslim_signals(row, market_direction)
        technical_signals = generate_technical_signals(row, ma_data)
        
        # Generate combined signal
        combined = generate_combined_signal(value_signals, canslim_signals, technical_signals)
        
        # Calculate MA50 and MA200 from available data
        current_price = row['sma_20_current']
        sma_50 = row['sma_50_current']
        
        # Calculate MA200 (estimate from trend)
        annual_return = row['annualized_return_pct']
        ma_200 = current_price * (1 - annual_return/100 * 0.67)  # Rough estimate
        
        # Calculate price vs MA ratios
        price_vs_ma50_pct = ((current_price - sma_50) / sma_50) * 100 if sma_50 > 0 else 0
        price_vs_ma200_pct = ((current_price - ma_200) / ma_200) * 100 if ma_200 > 0 else 0
        
        # Compile results
        result = {
            'symbol': symbol,
            'current_price': current_price,
            'sma_20': row['sma_20_current'],
            'sma_50': sma_50,
            'sma_200': round(ma_200, 2),
            'price_vs_sma20_pct': row['price_vs_sma20_pct'],
            'price_vs_sma50_pct': round(price_vs_ma50_pct, 2),
            'price_vs_sma200_pct': round(price_vs_ma200_pct, 2),
            'annualized_return_pct': row['annualized_return_pct'],
            'volatility_pct': row['annual_std_dev_pct'],
            'rsi_current': row['rsi_current'],
            
            # Relative Strength (vs VN-Index)
            'relative_strength_rating': calculate_relative_strength(
                row['annualized_return_pct'], 
                market_direction.get('vnindex_return', 13.0)
            ),
            
            # Value Investing
            'value_signal': value_signals['signal'],
            'value_score': value_signals['score'],
            'value_reasons': value_signals['reasons'],
            'pe_estimate': value_signals['pe_ratio'],
            'roe_estimate': value_signals['roe_estimate'],
            
            # CANSLIM
            'canslim_signal': canslim_signals['signal'],
            'canslim_score': canslim_signals['score'],
            'canslim_reasons': canslim_signals['reasons'],
            
            # Technical Analysis
            'technical_signal': technical_signals['signal'],
            'technical_score': technical_signals['score'],
            'technical_reasons': technical_signals['reasons'],
            
            # Combined Signal
            'final_signal': combined['final_signal'],
            'total_score': combined['total_score'],
            'confidence_pct': combined['confidence'],
            
            # Market Context
            'market_direction': market_direction['direction'],
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        results.append(result)
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by total score (best signals first)
    results_df = results_df.sort_values('total_score', ascending=False)
    
    # Save to CSV in data directory
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    output_file = os.path.join(data_dir, 'investment_signals_complete.csv')
    results_df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"📊 INVESTMENT SIGNALS SUMMARY")
    print(f"{'='*60}")
    print(f"Total stocks analyzed: {len(results_df)}")
    print(f"Market direction: {market_direction['direction']}")
    
    # Signal distribution
    signal_counts = results_df['final_signal'].value_counts()
    print(f"\n📈 Signal Distribution:")
    for signal, count in signal_counts.items():
        print(f"  {signal}: {count} stocks ({count/len(results_df)*100:.1f}%)")
    
    # Top recommendations
    print(f"\n🎯 TOP 10 BUY RECOMMENDATIONS:")
    buy_stocks = results_df[results_df['final_signal'] == 'BUY'].head(10)
    for idx, stock in buy_stocks.iterrows():
        print(f"  {stock['symbol']}: Score {stock['total_score']:.1f}, Return {stock['annualized_return_pct']:.1f}%, RS {stock['relative_strength_rating']}")
    
    print(f"\n⚠️  TOP 5 SELL RECOMMENDATIONS:")
    sell_stocks = results_df[results_df['final_signal'] == 'SELL'].head(5)
    for idx, stock in sell_stocks.iterrows():
        print(f"  {stock['symbol']}: Score {stock['total_score']:.1f}, Return {stock['annualized_return_pct']:.1f}%, RS {stock['relative_strength_rating']}")
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📁 File size: {os.path.getsize(output_file)/1024:.1f} KB")

if __name__ == "__main__":
    main()