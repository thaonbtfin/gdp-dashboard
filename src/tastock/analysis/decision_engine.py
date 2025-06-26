"""
Decision Engine for generating BUY/SELL/HOLD signals based on 3 investment methods.
"""

from typing import Dict, List
from .technical_analysis import TechnicalAnalysis
from .value_analysis import ValueAnalysis
from .canslim_analysis import CANSLIMAnalysis

class DecisionEngine:
    def __init__(self):
        self.technical = TechnicalAnalysis()
        self.value = ValueAnalysis()
        self.canslim = CANSLIMAnalysis()
    
    def analyze_all_methods(self, symbol: str, data: Dict) -> Dict:
        """Analyze using all 3 methods and return signals"""
        
        results = {
            'symbol': symbol,
            'value_investing': self.value.analyze(data),
            'canslim': self.canslim.analyze(data),
            'technical': self.technical.analyze(data),
            'final_recommendation': None
        }
        
        # Generate final recommendation based on consensus
        signals = [
            results['value_investing']['signal'],
            results['canslim']['signal'], 
            results['technical']['signal']
        ]
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        
        if buy_count >= 2:
            results['final_recommendation'] = 'BUY'
        elif sell_count >= 2:
            results['final_recommendation'] = 'SELL'
        else:
            results['final_recommendation'] = 'HOLD'
        
        return results
    
    def get_analysis_summary(self, analysis_result: Dict) -> str:
        """Generate human-readable summary"""
        summary = f"Analysis for {analysis_result['symbol']}:\n"
        summary += f"Value Investing: {analysis_result['value_investing']['signal']}\n"
        summary += f"CANSLIM: {analysis_result['canslim']['signal']}\n"
        summary += f"Technical: {analysis_result['technical']['signal']}\n"
        summary += f"Final Recommendation: {analysis_result['final_recommendation']}"
        
        return summary