"""
Technical Analysis module for trend-based trading signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, List

class TechnicalAnalysis:
    def __init__(self):
        pass
    
    def analyze(self, data: Dict) -> Dict:
        """Analyze using technical indicators"""
        price_data = pd.DataFrame(data.get('price_data', []))
        
        if price_data.empty:
            return {'signal': 'HOLD', 'reason': 'No price data', 'indicators': {}}
        
        # Calculate indicators
        indicators = self._calculate_indicators(price_data)
        
        # Generate signal
        signal = self._generate_signal(indicators)
        
        return {
            'signal': signal['signal'],
            'reason': signal['reason'],
            'indicators': indicators
        }
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        df = df.copy()
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        indicators = {}
        
        # Moving Averages
        indicators['ma_20'] = df['close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else None
        indicators['ma_50'] = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
        indicators['ma_200'] = df['close'].rolling(200).mean().iloc[-1] if len(df) >= 200 else None
        
        # MACD
        macd_data = self._calculate_macd(df['close'])
        indicators.update(macd_data)
        
        # RSI
        indicators['rsi'] = self._calculate_rsi(df['close'])
        
        # Volume
        indicators['volume_sma_20'] = df['volume'].rolling(20).mean().iloc[-1] if len(df) >= 20 else None
        indicators['current_volume'] = df['volume'].iloc[-1] if not df.empty else None
        
        # Current price
        indicators['current_price'] = df['close'].iloc[-1] if not df.empty else None
        
        return indicators
    
    def _calculate_macd(self, prices: pd.Series, fast=12, slow=26, signal=9) -> Dict:
        """Calculate MACD indicator"""
        if len(prices) < slow:
            return {'macd_line': None, 'macd_signal': None, 'macd_histogram': None}
        
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        macd_histogram = macd_line - macd_signal
        
        return {
            'macd_line': macd_line.iloc[-1],
            'macd_signal': macd_signal.iloc[-1],
            'macd_histogram': macd_histogram.iloc[-1]
        }
    
    def _calculate_rsi(self, prices: pd.Series, period=14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return None
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def _generate_signal(self, indicators: Dict) -> Dict:
        """Generate BUY/SELL/HOLD signal based on technical indicators"""
        buy_signals = 0
        sell_signals = 0
        reasons = []
        
        current_price = indicators.get('current_price')
        ma_20 = indicators.get('ma_20')
        ma_50 = indicators.get('ma_50')
        macd_line = indicators.get('macd_line')
        macd_signal = indicators.get('macd_signal')
        rsi = indicators.get('rsi')
        
        # MA signals
        if current_price and ma_20:
            if current_price > ma_20:
                buy_signals += 1
                reasons.append("Price above MA20")
            else:
                sell_signals += 1
                reasons.append("Price below MA20")
        
        if current_price and ma_50:
            if current_price > ma_50:
                buy_signals += 1
                reasons.append("Price above MA50")
            else:
                sell_signals += 1
                reasons.append("Price below MA50")
        
        # MACD signals
        if macd_line and macd_signal:
            if macd_line > macd_signal:
                buy_signals += 1
                reasons.append("MACD bullish crossover")
            else:
                sell_signals += 1
                reasons.append("MACD bearish crossover")
        
        # RSI signals
        if rsi:
            if rsi < 30:
                buy_signals += 1
                reasons.append("RSI oversold")
            elif rsi > 70:
                sell_signals += 1
                reasons.append("RSI overbought")
        
        # Decision logic
        if buy_signals > sell_signals:
            return {'signal': 'BUY', 'reason': '; '.join(reasons)}
        elif sell_signals > buy_signals:
            return {'signal': 'SELL', 'reason': '; '.join(reasons)}
        else:
            return {'signal': 'HOLD', 'reason': 'Mixed signals'}