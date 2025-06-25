"""
DataCalculator Module

This module provides the DataCalculator class for calculating metrics from stock data.
"""

import pandas as pd
from typing import Dict, Optional

import numpy as np
from vnstock import Vnstock
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
        
        metrics = self._calculate_series_performance_metrics(data, price_column='close')
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
            try:
                intrinsic_value = self._calculate_graham_intrinsic_value(financial_data)
                self._intrinsic_value_cache[symbol] = intrinsic_value
                return intrinsic_value
            except Exception as e:
                print(f"Error calculating intrinsic value for {symbol} with provided financial data: {e}")
                return None
        
        # If no financial data is provided, fetch it first
        try:
            financial_data = Vnstock().stock(symbol=symbol, source=source).finance.ratio(period='year', lang='vi', dropna=True)
            if financial_data.empty:
                return None
            
            intrinsic_value = self._calculate_graham_intrinsic_value(financial_data)
            self._intrinsic_value_cache[symbol] = intrinsic_value
            return intrinsic_value
        except Exception as e:
            print(f"Error calculating intrinsic value for {symbol}: {e}")
            return None
    
    def _calculate_series_performance_metrics(
        self,
        df: pd.DataFrame, 
        price_column: str = 'close', 
        trading_days_per_year: int = 250
    ) -> dict:
        """
        Calculates performance metrics from a historical price series.
        """
        if price_column not in df.columns:
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        if len(df) < 2:
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        prices = df[price_column].dropna()
        if len(prices) < 2:
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        # Filter out zero prices for meaningful calculations
        non_zero_prices = prices[prices > 0]
        if len(non_zero_prices) < 2:
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        first_price = non_zero_prices.iloc[0]
        last_price = non_zero_prices.iloc[-1]
        num_periods = len(non_zero_prices) - 1

        if first_price == 0 or num_periods == 0:
            geom_mean_daily_return = np.nan
        else:
            geom_mean_daily_return = (last_price / first_price)**(1 / num_periods) - 1
        
        annualized_return = (1 + geom_mean_daily_return)**trading_days_per_year - 1 if not np.isnan(geom_mean_daily_return) else np.nan
        daily_returns = non_zero_prices.pct_change().dropna()
        daily_std_dev = daily_returns.std(ddof=0) if not daily_returns.empty else np.nan
        annual_std_dev = daily_std_dev * np.sqrt(trading_days_per_year) if not np.isnan(daily_std_dev) else np.nan

        return {
            'geom_mean_daily_return_pct': round(geom_mean_daily_return * 100, 4) if not np.isnan(geom_mean_daily_return) else np.nan,
            'annualized_return_pct': round(annualized_return * 100, 4) if not np.isnan(annualized_return) else np.nan,
            'daily_std_dev_pct': round(daily_std_dev * 100, 4) if not np.isnan(daily_std_dev) else np.nan,
            'annual_std_dev_pct': round(annual_std_dev * 100, 4) if not np.isnan(annual_std_dev) else np.nan,
        }
    
    def _calculate_graham_intrinsic_value(self, financial_ratios_df: pd.DataFrame) -> Optional[float]:
        """
        Calculate Graham intrinsic value using the formula: sqrt(22.5 * EPS * BVPS)
        """
        try:
            latest_year_data = financial_ratios_df.iloc[0]
            
            eps_column_key = ('Chỉ tiêu định giá', 'EPS (VND)')
            bvps_column_key = ('Chỉ tiêu định giá', 'BVPS (VND)')
            eps = latest_year_data.get(eps_column_key)
            bvps = latest_year_data.get(bvps_column_key)
            
            if eps is not None and bvps is not None and pd.notna(eps) and pd.notna(bvps):
                if eps > 0 and bvps > 0:
                    return round(np.sqrt(22.5 * float(eps) * float(bvps)), 2)
            
            return None
        except Exception as e:
            print(f"Error in Graham calculation: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached calculations."""
        self._performance_metrics_cache.clear()
        self._intrinsic_value_cache.clear()