"""
Value Analysis module for Benjamin Graham & Warren Buffett style investing.
"""

import pandas as pd
import numpy as np
from typing import Dict

class ValueAnalysis:
    def __init__(self):
        pass
    
    def analyze(self, data: Dict) -> Dict:
        """Analyze using value investing principles"""
        basic_info = data.get('basic_info', {})
        financial_ratios = data.get('financial_ratios', {})
        financial_statements = data.get('financial_statements', {})
        
        # Calculate value metrics
        metrics = self._calculate_value_metrics(basic_info, financial_ratios, financial_statements)
        
        # Generate signal
        signal = self._generate_signal(metrics)
        
        return {
            'signal': signal['signal'],
            'reason': signal['reason'],
            'metrics': metrics
        }
    
    def _calculate_value_metrics(self, basic_info: Dict, ratios: Dict, statements: Dict) -> Dict:
        """Calculate value investing metrics"""
        metrics = {}
        
        # Basic ratios
        metrics['pe_ratio'] = basic_info.get('pe_ratio', 0)
        metrics['pb_ratio'] = basic_info.get('pb_ratio', 0)
        metrics['current_price'] = basic_info.get('current_price', 0)
        
        # ROE calculation (from financial statements)
        metrics['roe'] = self._calculate_roe(statements)
        
        # Debt/Equity ratio
        metrics['debt_equity'] = self._calculate_debt_equity(statements)
        
        # Free Cash Flow Yield
        metrics['fcf_yield'] = self._calculate_fcf_yield(statements, basic_info)
        
        # Graham Intrinsic Value
        metrics['intrinsic_value'] = self._calculate_graham_value(ratios)
        
        # Margin of Safety
        if metrics['intrinsic_value'] and metrics['current_price']:
            metrics['margin_of_safety'] = (metrics['intrinsic_value'] - metrics['current_price']) / metrics['intrinsic_value'] * 100
        else:
            metrics['margin_of_safety'] = None
        
        return metrics
    
    def _calculate_roe(self, statements: Dict) -> float:
        """Calculate ROE from financial statements"""
        try:
            income_statement = statements.get('income_statement', [])
            balance_sheet = statements.get('balance_sheet', [])
            
            if not income_statement or not balance_sheet:
                return None
            
            # Get latest year data
            latest_income = income_statement[0] if income_statement else {}
            latest_balance = balance_sheet[0] if balance_sheet else {}
            
            net_income = latest_income.get('Lợi nhuận sau thuế', 0)
            shareholders_equity = latest_balance.get('Vốn chủ sở hữu', 0)
            
            if shareholders_equity and shareholders_equity != 0:
                return (net_income / shareholders_equity) * 100
            
            return None
        except:
            return None
    
    def _calculate_debt_equity(self, statements: Dict) -> float:
        """Calculate Debt/Equity ratio"""
        try:
            balance_sheet = statements.get('balance_sheet', [])
            
            if not balance_sheet:
                return None
            
            latest_balance = balance_sheet[0]
            total_debt = latest_balance.get('Tổng nợ', 0)
            shareholders_equity = latest_balance.get('Vốn chủ sở hữu', 0)
            
            if shareholders_equity and shareholders_equity != 0:
                return total_debt / shareholders_equity
            
            return None
        except:
            return None
    
    def _calculate_fcf_yield(self, statements: Dict, basic_info: Dict) -> float:
        """Calculate Free Cash Flow Yield"""
        try:
            cash_flow = statements.get('cash_flow', [])
            
            if not cash_flow:
                return None
            
            latest_cf = cash_flow[0]
            operating_cf = latest_cf.get('Lưu chuyển tiền từ hoạt động kinh doanh', 0)
            capex = latest_cf.get('Đầu tư tài sản cố định', 0)
            
            free_cash_flow = operating_cf - abs(capex)
            market_cap = basic_info.get('market_cap', 0)
            
            if market_cap and market_cap != 0:
                return (free_cash_flow / market_cap) * 100
            
            return None
        except:
            return None
    
    def _calculate_graham_value(self, ratios: Dict) -> float:
        """Calculate Graham Intrinsic Value: sqrt(22.5 * EPS * BVPS)"""
        try:
            eps = ratios.get('EPS', 0)
            bvps = ratios.get('BVPS', 0)
            
            if eps and bvps and eps > 0 and bvps > 0:
                return np.sqrt(22.5 * eps * bvps)
            
            return None
        except:
            return None
    
    def _generate_signal(self, metrics: Dict) -> Dict:
        """Generate BUY/SELL/HOLD signal based on value metrics"""
        buy_signals = 0
        sell_signals = 0
        reasons = []
        
        pe_ratio = metrics.get('pe_ratio', 0)
        pb_ratio = metrics.get('pb_ratio', 0)
        roe = metrics.get('roe', 0)
        debt_equity = metrics.get('debt_equity', 0)
        fcf_yield = metrics.get('fcf_yield', 0)
        margin_of_safety = metrics.get('margin_of_safety', 0)
        
        # P/E ratio check
        if pe_ratio and 0 < pe_ratio < 15:
            buy_signals += 1
            reasons.append(f"Low P/E ratio ({pe_ratio:.1f})")
        elif pe_ratio > 25:
            sell_signals += 1
            reasons.append(f"High P/E ratio ({pe_ratio:.1f})")
        
        # P/B ratio check
        if pb_ratio and 0 < pb_ratio < 1.5:
            buy_signals += 1
            reasons.append(f"Low P/B ratio ({pb_ratio:.1f})")
        elif pb_ratio > 3:
            sell_signals += 1
            reasons.append(f"High P/B ratio ({pb_ratio:.1f})")
        
        # ROE check
        if roe and roe > 15:
            buy_signals += 1
            reasons.append(f"Good ROE ({roe:.1f}%)")
        elif roe and roe < 10:
            sell_signals += 1
            reasons.append(f"Low ROE ({roe:.1f}%)")
        
        # Debt/Equity check
        if debt_equity is not None:
            if debt_equity < 0.5:
                buy_signals += 1
                reasons.append(f"Low debt/equity ({debt_equity:.2f})")
            elif debt_equity > 1.0:
                sell_signals += 1
                reasons.append(f"High debt/equity ({debt_equity:.2f})")
        
        # FCF Yield check
        if fcf_yield and fcf_yield > 5:
            buy_signals += 1
            reasons.append(f"Good FCF yield ({fcf_yield:.1f}%)")
        
        # Margin of Safety check (most important)
        if margin_of_safety is not None:
            if margin_of_safety > 30:
                buy_signals += 2  # Double weight
                reasons.append(f"High margin of safety ({margin_of_safety:.1f}%)")
            elif margin_of_safety < -20:
                sell_signals += 2  # Double weight
                reasons.append(f"Overvalued ({margin_of_safety:.1f}%)")
        
        # Decision logic
        if buy_signals > sell_signals:
            return {'signal': 'BUY', 'reason': '; '.join(reasons)}
        elif sell_signals > buy_signals:
            return {'signal': 'SELL', 'reason': '; '.join(reasons)}
        else:
            return {'signal': 'HOLD', 'reason': 'Mixed value signals'}