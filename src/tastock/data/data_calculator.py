"""
DataCalculator Module

This module provides the DataCalculator class for calculating metrics from stock data.
"""

import pandas as pd
from typing import Dict, Optional

from .calculator import Calculator
from ..core.stock import Stock
from src.constants import DEFAULT_SOURCE

class DataCalculator:
    """
    DataCalculator handles calculating metrics from stock data.
    """
    
    def __init__(self):
        """Initialize the DataCalculator."""
        # Cache to store calculated metrics
        self._performance_metrics_cache = {}  # {symbol: metrics_dict}
        self._intrinsic_value_cache = {}  # {symbol: value}
        
    def calculate_performance_metrics(
        self, 
        symbol: str, 
        data: pd.DataFrame = None,
        force_recalculate: bool = False
    ) -> Dict:
        """
        Calculate performance metrics for a symbol.
        
        Args:
            symbol (str): Stock symbol
            data (pd.DataFrame): Stock data DataFrame
            force_recalculate (bool): If True, recalculate even if in cache
            
        Returns:
            Dict: Performance metrics dictionary
        """
        if not force_recalculate and symbol in self._performance_metrics_cache:
            return self._performance_metrics_cache[symbol]
        
        if data is None or data.empty:
            raise ValueError(f"No data provided for {symbol}. Cannot calculate performance metrics.")
        
        metrics = Calculator.calculate_series_performance_metrics(data, price_column='close')
        self._performance_metrics_cache[symbol] = metrics
        return metrics
    
    def calculate_intrinsic_value(
        self, 
        symbol: str,
        financial_data: pd.DataFrame = None,
        source: str = DEFAULT_SOURCE,
        force_recalculate: bool = False
    ) -> Optional[float]:
        """
        Calculate intrinsic value for a symbol.
        
        Args:
            symbol (str): Stock symbol
            financial_data (pd.DataFrame): Financial data DataFrame
            source (str): Data source for stock information
            force_recalculate (bool): If True, recalculate even if in cache
            
        Returns:
            Optional[float]: Intrinsic value or None if calculation fails
        """
        if not force_recalculate and symbol in self._intrinsic_value_cache:
            return self._intrinsic_value_cache[symbol]
        
        # If financial data is provided, use it to calculate intrinsic value
        if financial_data is not None and not financial_data.empty:
            # Create a temporary Stock object to calculate intrinsic value
            try:
                stock = Stock(
                    symbol=symbol,
                    start_date=None,  # Not needed for intrinsic value calculation
                    end_date=None,
                    source=source
                )
                stock.financial_ratios_df = financial_data
                stock._calculate_intrinsic_value_graham()
                intrinsic_value = stock.get_intrinsic_value_graham()
                self._intrinsic_value_cache[symbol] = intrinsic_value
                return intrinsic_value
            except Exception as e:
                print(f"Error calculating intrinsic value for {symbol} with provided financial data: {e}")
                return None
        
        # If no financial data is provided, create a Stock object to fetch and calculate
        try:
            stock = Stock(
                symbol=symbol,
                start_date=None,  # Not needed for intrinsic value calculation
                end_date=None,
                source=source
            )
            stock._fetch_and_calculate_intrinsic_value()
            intrinsic_value = stock.get_intrinsic_value_graham()
            self._intrinsic_value_cache[symbol] = intrinsic_value
            return intrinsic_value
        except Exception as e:
            print(f"Error calculating intrinsic value for {symbol}: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached calculations."""
        self._performance_metrics_cache.clear()
        self._intrinsic_value_cache.clear()