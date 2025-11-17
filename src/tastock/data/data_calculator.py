"""
DataCalculator Module

This module provides the DataCalculator class for calculating metrics from stock data.
"""

import pandas as pd
from typing import Dict, Optional

import numpy as np
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
        self._history_data_cache = None  # Cache for history_data.csv
        
    def calculate_performance_metrics(
        self, 
        symbol: str, 
        data: pd.DataFrame = None,
        force_recalculate: bool = False
    ) -> Dict:
        """
        Calculate comprehensive performance metrics for a symbol.
        
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
        
        # Basic performance metrics
        metrics = self._calculate_series_performance_metrics(data, price_column='close')
        
        # Technical indicators
        technical = self.calculate_technical_indicators(data, symbol)
        metrics.update(technical)
        
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
        
        # If no financial data is provided, return None (vnstock dependency removed)
        print(f"No financial data provided for {symbol}. Use generate_intrinsic_values.py script instead.")
        return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame, symbol: str = None) -> Dict:
        """Calculate technical indicators from historical data."""
        if df.empty or 'close' not in df.columns:
            return {}
        
        prices = df['close'].replace(0, np.nan).dropna()
        if len(prices) < 20:
            return {}
        
        # RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Moving averages
        sma_20 = prices.rolling(window=20).mean()
        sma_50 = prices.rolling(window=50).mean() if len(prices) >= 50 else np.nan
        
        # Volatility
        returns = prices.pct_change().dropna()
        volatility = returns.std() * np.sqrt(250) * 100
        
        return {
            'rsi_current': round(rsi.iloc[-1], 2) if not rsi.empty else np.nan,
            'sma_20_current': round(sma_20.iloc[-1], 2) if not sma_20.empty else np.nan,
            'sma_50_current': round(sma_50.iloc[-1], 2) if len(prices) >= 50 and not sma_50.empty else np.nan,
            'volatility_annual_pct': round(volatility, 2) if not np.isnan(volatility) else np.nan,
            'price_vs_sma20_pct': round((prices.iloc[-1] / sma_20.iloc[-1] - 1) * 100, 2) if not sma_20.empty else np.nan
        }
    
    def _calculate_series_performance_metrics(
        self,
        df: pd.DataFrame, 
        price_column: str = 'close', 
        trading_days_per_year: int = 250
    ) -> dict:
        """Calculates performance metrics from a historical price series."""
        if price_column not in df.columns or len(df) < 2:
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        prices = df[price_column].replace(0, np.nan).dropna()
        if len(prices) < 2:
            return {metric: np.nan for metric in ['geom_mean_daily_return_pct', 'annualized_return_pct', 'daily_std_dev_pct', 'annual_std_dev_pct']}

        first_price, last_price = prices.iloc[0], prices.iloc[-1]
        num_periods = len(prices) - 1

        geom_mean_daily_return = (last_price / first_price)**(1 / num_periods) - 1 if first_price > 0 and num_periods > 0 else np.nan
        annualized_return = (1 + geom_mean_daily_return)**trading_days_per_year - 1 if not np.isnan(geom_mean_daily_return) else np.nan
        
        daily_returns = prices.pct_change().dropna()
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
    
    def load_history_data(self, file_path: str = None) -> pd.DataFrame:
        """Load and cache history_data.csv for efficient calculations."""
        if self._history_data_cache is not None:
            return self._history_data_cache
        
        if file_path is None:
            from src.constants import DATA_HISTORY
            file_path = DATA_HISTORY
        
        try:
            df = pd.read_csv(file_path)
            df['time'] = pd.to_datetime(df['time'])
            self._history_data_cache = df
            return df
        except Exception as e:
            print(f"Error loading history data: {e}")
            return pd.DataFrame()
    
    def get_symbol_data_from_history(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Extract symbol data from cached history_data.csv."""
        history_df = self.load_history_data()
        if history_df.empty or symbol not in history_df.columns:
            return pd.DataFrame()
        
        result_df = history_df[['time', symbol]].copy()
        result_df = result_df.rename(columns={symbol: 'close'})
        result_df = result_df[result_df['close'] > 0]  # Filter out zero values
        
        if start_date:
            result_df = result_df[result_df['time'] >= start_date]
        if end_date:
            result_df = result_df[result_df['time'] <= end_date]
        
        return result_df.reset_index(drop=True)
    
    def calculate_metrics_from_history(self, symbols: list, start_date: str = None, end_date: str = None) -> Dict:
        """Calculate metrics for multiple symbols from history_data.csv."""
        results = {}
        for symbol in symbols:
            data = self.get_symbol_data_from_history(symbol, start_date, end_date)
            if not data.empty:
                results[symbol] = self.calculate_performance_metrics(symbol, data, force_recalculate=True)
        return results
    
    def clear_cache(self):
        """Clear all cached calculations."""
        self._performance_metrics_cache.clear()
        self._intrinsic_value_cache.clear()
        self._history_data_cache = None