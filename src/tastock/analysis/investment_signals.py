"""
Investment Signal Calculator for 3 methods: Value Investing, CANSLIM, Technical Analysis
"""
import pandas as pd
from typing import Dict, List, Tuple
import numpy as np

class InvestmentSignalCalculator:
    
    def __init__(self, vnindex_data: List[Dict] = None):
        """Initialize with VN-Index data for market direction"""
        self.vnindex_data = vnindex_data or []
    
    def calculate_market_direction(self) -> Dict:
        """Calculate Market Direction from VN-Index data"""
        if len(self.vnindex_data) < 200:
            return {'direction': 'UNKNOWN', 'strength': 0}
        
        # Get recent prices
        prices = [item['close'] for item in self.vnindex_data[-200:]]
        current_price = prices[-1]
        
        # Calculate moving averages
        ma50 = sum(prices[-50:]) / 50
        ma200 = sum(prices[-200:]) / 200
        
        # Determine trend
        if current_price > ma50 > ma200:
            direction = 'UPTREND'
            strength = ((current_price - ma200) / ma200) * 100
        elif current_price < ma50 < ma200:
            direction = 'DOWNTREND' 
            strength = ((ma200 - current_price) / ma200) * 100
        else:
            direction = 'SIDEWAYS'
            strength = abs((current_price - ma50) / ma50) * 100
        
        return {
            'direction': direction,
            'strength': round(strength, 2),
            'current_price': current_price,
            'ma50': round(ma50, 2),
            'ma200': round(ma200, 2)
        }
    
    def calculate_relative_strength(self, stock_data: List[Dict]) -> float:
        """Calculate Relative Strength Rating (1-99 scale)"""
        if len(stock_data) < 252 or len(self.vnindex_data) < 252:
            return 50  # Default neutral
        
        # Calculate 12-month returns
        stock_prices = [item['close'] for item in stock_data[-252:]]
        vnindex_prices = [item['close'] for item in self.vnindex_data[-252:]]
        
        stock_return = (stock_prices[-1] - stock_prices[0]) / stock_prices[0]
        market_return = (vnindex_prices[-1] - vnindex_prices[0]) / vnindex_prices[0]
        
        # Calculate relative strength
        if market_return != 0:
            relative_performance = stock_return / market_return
            # Convert to 1-99 scale
            rs_rating = min(99, max(1, int(relative_performance * 50 + 50)))
        else:
            rs_rating = 50
        
        return rs_rating
    
    def parse_institutional_ownership(self, ownership_text: str) -> float:
        """Parse institutional ownership from text"""
        # Look for patterns like "Quỹ đầu tư: 25.5%" or "Tổ chức: 40%"
        import re
        
        patterns = [
            r'(?:Quỹ|Fund|Institution|Tổ chức).*?(\d+\.?\d*)%',
            r'(\d+\.?\d*)%.*?(?:quỹ|fund|institution|tổ chức)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, ownership_text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    def generate_value_signals(self, stock_data: Dict) -> Dict:
        """Generate Buy/Sell/Hold signals for Value Investing"""
        basic_info = stock_data.get('basic_info', {})
        value_metrics = stock_data.get('value_metrics', {})
        
        pe_ratio = basic_info.get('pe_ratio', 0)
        pb_ratio = basic_info.get('pb_ratio', 0)
        roe = value_metrics.get('roe', 0)
        debt_to_equity = value_metrics.get('debt_to_equity', 0)
        
        signals = []
        score = 0
        
        # P/E analysis
        if 0 < pe_ratio < 15:
            signals.append("P/E < 15: Hấp dẫn")
            score += 2
        elif pe_ratio > 25:
            signals.append("P/E > 25: Đắt")
            score -= 1
        
        # P/B analysis
        if 0 < pb_ratio < 1.5:
            signals.append("P/B < 1.5: Tốt")
            score += 1
        elif pb_ratio > 3:
            signals.append("P/B > 3: Cao")
            score -= 1
        
        # ROE analysis
        if roe > 15:
            signals.append("ROE > 15%: Tốt")
            score += 2
        elif roe < 10:
            signals.append("ROE < 10%: Yếu")
            score -= 1
        
        # Debt analysis
        if debt_to_equity < 0.5:
            signals.append("Debt/Equity < 0.5: An toàn")
            score += 1
        elif debt_to_equity > 1:
            signals.append("Debt/Equity > 1: Rủi ro")
            score -= 2
        
        # Final signal
        if score >= 4:
            final_signal = "BUY"
        elif score <= -2:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
        
        return {
            'signal': final_signal,
            'score': score,
            'reasons': signals,
            'metrics': {
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'roe': roe,
                'debt_to_equity': debt_to_equity
            }
        }
    
    def generate_canslim_signals(self, stock_data: Dict) -> Dict:
        """Generate Buy/Sell/Hold signals for CANSLIM"""
        growth_metrics = stock_data.get('growth_metrics', {})
        basic_info = stock_data.get('basic_info', {})
        technical = stock_data.get('technical_indicators', {})
        
        eps_growth = growth_metrics.get('eps_growth_quarterly', 0)
        revenue_growth = growth_metrics.get('revenue_growth', 0)
        volume_ratio = technical.get('volume_ratio', 1)
        
        # Market direction
        market_dir = self.calculate_market_direction()
        
        signals = []
        score = 0
        
        # Current Earnings (C)
        if eps_growth >= 25:
            signals.append("EPS tăng ≥25%: Tốt")
            score += 2
        elif eps_growth < 0:
            signals.append("EPS giảm: Xấu")
            score -= 2
        
        # Annual Earnings (A) - using revenue as proxy
        if revenue_growth >= 25:
            signals.append("Doanh thu tăng ≥25%: Tốt")
            score += 1
        elif revenue_growth < 0:
            signals.append("Doanh thu giảm: Xấu")
            score -= 1
        
        # Supply & Demand (S) - Volume
        if volume_ratio >= 1.4:
            signals.append("Volume tăng 40%+: Mạnh")
            score += 1
        elif volume_ratio < 0.8:
            signals.append("Volume yếu: Không tốt")
            score -= 1
        
        # Market Direction (M)
        if market_dir['direction'] == 'UPTREND':
            signals.append("Thị trường tăng: Tốt")
            score += 2
        elif market_dir['direction'] == 'DOWNTREND':
            signals.append("Thị trường giảm: Xấu")
            score -= 2
        
        # Final signal
        if score >= 4:
            final_signal = "BUY"
        elif score <= -3:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
        
        return {
            'signal': final_signal,
            'score': score,
            'reasons': signals,
            'metrics': {
                'eps_growth': eps_growth,
                'revenue_growth': revenue_growth,
                'volume_ratio': volume_ratio,
                'market_direction': market_dir['direction']
            }
        }
    
    def generate_technical_signals(self, stock_data: Dict) -> Dict:
        """Generate Buy/Sell/Hold signals for Technical Analysis"""
        basic_info = stock_data.get('basic_info', {})
        technical = stock_data.get('technical_indicators', {})
        price_data = stock_data.get('price_data', [])
        
        if not price_data:
            return {'signal': 'HOLD', 'score': 0, 'reasons': ['Không đủ dữ liệu']}
        
        current_price = basic_info.get('current_price', 0)
        macd_data = technical.get('macd', {})
        
        signals = []
        score = 0
        
        # MACD signals
        macd_line = macd_data.get('macd_line', 0)
        signal_line = macd_data.get('signal_line', 0)
        
        if macd_line > signal_line and macd_data.get('histogram', 0) > 0:
            signals.append("MACD tích cực: Mua")
            score += 2
        elif macd_line < signal_line and macd_data.get('histogram', 0) < 0:
            signals.append("MACD tiêu cực: Bán")
            score -= 2
        
        # Moving Average signals (from existing data)
        if len(price_data) >= 50:
            prices = [item['close'] for item in price_data[-50:]]
            ma20 = sum(prices[-20:]) / 20
            ma50 = sum(prices) / 50
            
            if current_price > ma20 > ma50:
                signals.append("Giá > MA20 > MA50: Tăng")
                score += 1
            elif current_price < ma20 < ma50:
                signals.append("Giá < MA20 < MA50: Giảm")
                score -= 1
        
        # Volume confirmation
        volume_ratio = technical.get('volume_ratio', 1)
        if volume_ratio > 1.2 and score > 0:
            signals.append("Volume xác nhận: Tốt")
            score += 1
        elif volume_ratio > 1.2 and score < 0:
            signals.append("Volume xác nhận: Xấu")
            score -= 1
        
        # Final signal
        if score >= 3:
            final_signal = "BUY"
        elif score <= -3:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"
        
        return {
            'signal': final_signal,
            'score': score,
            'reasons': signals,
            'metrics': {
                'macd_line': macd_line,
                'signal_line': signal_line,
                'volume_ratio': volume_ratio
            }
        }
    
    def generate_combined_signals(self, stock_data: Dict) -> Dict:
        """Generate combined signals from all 3 methods"""
        value_signals = self.generate_value_signals(stock_data)
        canslim_signals = self.generate_canslim_signals(stock_data)
        technical_signals = self.generate_technical_signals(stock_data)
        
        # Weight the signals
        signal_weights = {'BUY': 1, 'HOLD': 0, 'SELL': -1}
        
        total_score = (
            signal_weights[value_signals['signal']] * 2 +  # Value investing weight
            signal_weights[canslim_signals['signal']] * 1.5 +  # CANSLIM weight
            signal_weights[technical_signals['signal']] * 1  # Technical weight
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
            'individual_signals': {
                'value_investing': value_signals,
                'canslim': canslim_signals,
                'technical_analysis': technical_signals
            }
        }