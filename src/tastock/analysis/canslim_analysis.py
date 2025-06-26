"""
CANSLIM Analysis module based on William O'Neil's methodology.
"""

import pandas as pd
import numpy as np
from typing import Dict, List

class CANSLIMAnalysis:
    def __init__(self):
        pass
    
    def analyze(self, data: Dict) -> Dict:
        """Analyze using CANSLIM methodology"""
        basic_info = data.get('basic_info', {})
        financial_statements = data.get('financial_statements', {})
        price_data = data.get('price_data', [])
        
        # Calculate CANSLIM metrics
        metrics = self._calculate_canslim_metrics(basic_info, financial_statements, price_data)
        
        # Generate signal
        signal = self._generate_signal(metrics)
        
        return {
            'signal': signal['signal'],
            'reason': signal['reason'],
            'metrics': metrics
        }
    
    def _calculate_canslim_metrics(self, basic_info: Dict, statements: Dict, price_data: List) -> Dict:
        """Calculate CANSLIM metrics"""
        metrics = {}
        
        # C - Current Earnings Growth
        metrics['current_earnings_growth'] = self._calculate_current_earnings_growth(statements)
        
        # A - Annual Earnings Growth
        metrics['annual_earnings_growth'] = self._calculate_annual_earnings_growth(statements)
        
        # N - New Product/Service (qualitative - set to neutral)
        metrics['new_products'] = True  # Assume positive for now
        
        # S - Supply and Demand (Volume analysis)
        metrics['volume_analysis'] = self._analyze_volume(price_data)
        
        # L - Leader or Laggard (Relative Strength)
        metrics['relative_strength'] = self._calculate_relative_strength(price_data)
        
        # I - Institutional Sponsorship (not available from CafeF)
        metrics['institutional_sponsorship'] = None
        
        # M - Market Direction (simplified)
        metrics['market_direction'] = self._analyze_market_direction(price_data)
        
        return metrics
    
    def _calculate_current_earnings_growth(self, statements: Dict) -> float:
        """Calculate current quarter EPS growth vs same quarter last year"""
        try:
            income_statement = statements.get('income_statement', [])
            
            if len(income_statement) < 2:
                return None
            
            # Get latest and previous year data
            current_earnings = income_statement[0].get('Lợi nhuận sau thuế', 0)
            previous_earnings = income_statement[1].get('Lợi nhuận sau thuế', 0)
            
            if previous_earnings and previous_earnings != 0:
                growth = ((current_earnings - previous_earnings) / abs(previous_earnings)) * 100
                return growth
            
            return None
        except:
            return None
    
    def _calculate_annual_earnings_growth(self, statements: Dict) -> float:
        """Calculate 3-year CAGR of annual earnings"""
        try:
            income_statement = statements.get('income_statement', [])
            
            if len(income_statement) < 3:
                return None
            
            # Get earnings for last 3 years
            earnings = []
            for i in range(3):
                earning = income_statement[i].get('Lợi nhuận sau thuế', 0)
                earnings.append(earning)
            
            # Calculate CAGR
            if earnings[2] > 0 and earnings[0] > 0:
                cagr = ((earnings[0] / earnings[2]) ** (1/2)) - 1
                return cagr * 100
            
            return None
        except:
            return None
    
    def _analyze_volume(self, price_data: List) -> Dict:
        """Analyze volume patterns"""
        try:
            if not price_data or len(price_data) < 20:
                return {'volume_trend': None, 'volume_breakout': False}
            
            df = pd.DataFrame(price_data)
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            # Calculate volume moving average
            df['volume_ma'] = df['volume'].rolling(20).mean()
            
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume_ma'].iloc[-1]
            
            volume_breakout = current_volume > (avg_volume * 1.4) if avg_volume else False
            
            # Volume trend
            recent_avg = df['volume'].tail(5).mean()
            older_avg = df['volume'].head(5).mean()
            
            if recent_avg > older_avg * 1.2:
                volume_trend = 'increasing'
            elif recent_avg < older_avg * 0.8:
                volume_trend = 'decreasing'
            else:
                volume_trend = 'stable'
            
            return {
                'volume_trend': volume_trend,
                'volume_breakout': volume_breakout,
                'current_vs_avg': current_volume / avg_volume if avg_volume else None
            }
        except:
            return {'volume_trend': None, 'volume_breakout': False}
    
    def _calculate_relative_strength(self, price_data: List) -> float:
        """Calculate relative strength (simplified version)"""
        try:
            if not price_data or len(price_data) < 50:
                return None
            
            df = pd.DataFrame(price_data)
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            
            # Calculate price performance over different periods
            current_price = df['close'].iloc[-1]
            
            # 3-month performance
            price_3m = df['close'].iloc[-60] if len(df) >= 60 else df['close'].iloc[0]
            perf_3m = ((current_price - price_3m) / price_3m) * 100
            
            # 6-month performance  
            price_6m = df['close'].iloc[-120] if len(df) >= 120 else df['close'].iloc[0]
            perf_6m = ((current_price - price_6m) / price_6m) * 100
            
            # Simple RS rating (0-100 scale)
            # This is simplified - real RS rating compares to market
            avg_perf = (perf_3m + perf_6m) / 2
            
            # Convert to 0-100 scale (rough approximation)
            if avg_perf > 50:
                rs_rating = 90
            elif avg_perf > 25:
                rs_rating = 80
            elif avg_perf > 10:
                rs_rating = 70
            elif avg_perf > 0:
                rs_rating = 60
            elif avg_perf > -10:
                rs_rating = 50
            elif avg_perf > -25:
                rs_rating = 40
            else:
                rs_rating = 30
            
            return rs_rating
        except:
            return None
    
    def _analyze_market_direction(self, price_data: List) -> str:
        """Analyze overall market direction (simplified)"""
        try:
            if not price_data or len(price_data) < 20:
                return 'neutral'
            
            df = pd.DataFrame(price_data)
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            
            # Calculate moving averages
            df['ma_20'] = df['close'].rolling(20).mean()
            df['ma_50'] = df['close'].rolling(50).mean() if len(df) >= 50 else df['close'].rolling(20).mean()
            
            current_price = df['close'].iloc[-1]
            ma_20 = df['ma_20'].iloc[-1]
            ma_50 = df['ma_50'].iloc[-1]
            
            if current_price > ma_20 > ma_50:
                return 'uptrend'
            elif current_price < ma_20 < ma_50:
                return 'downtrend'
            else:
                return 'sideways'
        except:
            return 'neutral'
    
    def _generate_signal(self, metrics: Dict) -> Dict:
        """Generate BUY/SELL/HOLD signal based on CANSLIM criteria"""
        buy_signals = 0
        sell_signals = 0
        reasons = []
        
        # C - Current Earnings Growth
        current_growth = metrics.get('current_earnings_growth')
        if current_growth and current_growth > 25:
            buy_signals += 1
            reasons.append(f"Strong current earnings growth ({current_growth:.1f}%)")
        elif current_growth and current_growth < -10:
            sell_signals += 1
            reasons.append(f"Declining current earnings ({current_growth:.1f}%)")
        
        # A - Annual Earnings Growth
        annual_growth = metrics.get('annual_earnings_growth')
        if annual_growth and annual_growth > 25:
            buy_signals += 1
            reasons.append(f"Strong annual earnings growth ({annual_growth:.1f}%)")
        elif annual_growth and annual_growth < 10:
            sell_signals += 1
            reasons.append(f"Weak annual earnings growth ({annual_growth:.1f}%)")
        
        # S - Supply and Demand
        volume_analysis = metrics.get('volume_analysis', {})
        if volume_analysis.get('volume_breakout'):
            buy_signals += 1
            reasons.append("Volume breakout detected")
        
        volume_trend = volume_analysis.get('volume_trend')
        if volume_trend == 'increasing':
            buy_signals += 1
            reasons.append("Increasing volume trend")
        elif volume_trend == 'decreasing':
            sell_signals += 1
            reasons.append("Decreasing volume trend")
        
        # L - Leader or Laggard
        rs_rating = metrics.get('relative_strength')
        if rs_rating and rs_rating >= 80:
            buy_signals += 1
            reasons.append(f"Strong relative strength ({rs_rating})")
        elif rs_rating and rs_rating < 50:
            sell_signals += 1
            reasons.append(f"Weak relative strength ({rs_rating})")
        
        # M - Market Direction
        market_direction = metrics.get('market_direction')
        if market_direction == 'uptrend':
            buy_signals += 1
            reasons.append("Market in uptrend")
        elif market_direction == 'downtrend':
            sell_signals += 1
            reasons.append("Market in downtrend")
        
        # Decision logic
        if buy_signals >= 3:
            return {'signal': 'BUY', 'reason': '; '.join(reasons)}
        elif sell_signals >= 2:
            return {'signal': 'SELL', 'reason': '; '.join(reasons)}
        else:
            return {'signal': 'HOLD', 'reason': 'Mixed CANSLIM signals'}