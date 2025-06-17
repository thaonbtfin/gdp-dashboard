"""
DataManager Module

This module provides a centralized way to manage data for both portfolios and symbols
in the tastock application. It coordinates between fetching, calculating, and storing data.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from functools import lru_cache

from .data_fetcher import DataFetcher
from .data_calculator import DataCalculator
from .data_storage import DataStorage
from ..core.portfolio import Portfolio
from src.constants import DEFAULT_SOURCE, DEFAULT_OUTPUT_DIR

class DataManager:
    """
    DataManager coordinates between fetching, calculating, and storing data for stocks and portfolios.
    """
    
    def __init__(
        self,
        base_output_dir: str = DEFAULT_OUTPUT_DIR,
        source: str = DEFAULT_SOURCE
    ):
        """
        Initialize the DataManager.
        
        Args:
            base_output_dir (str): Base directory for data storage
            source (str): Data source for stock information
        """
        self.base_output_dir = base_output_dir
        self.source = source
        
        # Initialize components
        self.fetcher = DataFetcher(source=source)
        self.calculator = DataCalculator()
        self.storage = DataStorage(base_output_dir=base_output_dir)
        
    def fetch_stock_data(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str,
        force_refresh: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for the given symbols.
        
        Args:
            symbols (List[str]): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            force_refresh (bool): If True, ignore cache and fetch fresh data
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of {symbol: dataframe}
        """
        return self.fetcher.fetch_stock_data(symbols, start_date, end_date, force_refresh)
    
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
            data (pd.DataFrame): Stock data DataFrame (if None, must be in cache)
            force_recalculate (bool): If True, recalculate even if in cache
            
        Returns:
            Dict: Performance metrics dictionary
        """
        return self.calculator.calculate_performance_metrics(symbol, data, force_recalculate)
    
    def calculate_intrinsic_value(
        self, 
        symbol: str,
        force_recalculate: bool = False
    ) -> Optional[float]:
        """
        Calculate intrinsic value for a symbol.
        
        Args:
            symbol (str): Stock symbol
            force_recalculate (bool): If True, recalculate even if in cache
            
        Returns:
            Optional[float]: Intrinsic value or None if calculation fails
        """
        # Fetch financial data first
        financial_data = self.fetcher.fetch_financial_data(symbol)
        
        # Calculate intrinsic value
        return self.calculator.calculate_intrinsic_value(
            symbol, 
            financial_data=financial_data,
            source=self.source,
            force_recalculate=force_recalculate
        )
    
    def save_stock_data(
        self, 
        symbol: str, 
        data: pd.DataFrame,
        portfolio_name: Optional[str] = None
    ) -> str:
        """
        Save stock data to CSV file.
        
        Args:
            symbol (str): Stock symbol
            data (pd.DataFrame): Stock data DataFrame
            portfolio_name (str): Portfolio name (if part of a portfolio)
            
        Returns:
            str: Path to saved file
        """
        return self.storage.save_stock_data(symbol, data, portfolio_name)
    
    def save_portfolio_history(
        self, 
        portfolio_name: str, 
        data: Dict[str, pd.DataFrame]
    ) -> Tuple[str, str]:
        """
        Save portfolio history data to CSV files.
        
        Args:
            portfolio_name (str): Portfolio name
            data (Dict[str, pd.DataFrame]): Dictionary of {symbol: dataframe}
            
        Returns:
            Tuple[str, str]: Paths to portfolio history file and merged history file
        """
        return self.storage.save_portfolio_history(portfolio_name, data)
    
    def save_performance_metrics(
        self, 
        metrics_data: Dict[str, Dict],
        portfolio_name: Optional[str] = None
    ) -> str:
        """
        Save performance metrics to CSV file.
        
        Args:
            metrics_data (Dict[str, Dict]): Dictionary of {symbol: metrics_dict}
            portfolio_name (str): Portfolio name (if for a specific portfolio)
            
        Returns:
            str: Path to saved file
        """
        return self.storage.save_performance_metrics(metrics_data, portfolio_name)
    
    def save_intrinsic_values(
        self, 
        intrinsic_values: Dict[str, float]
    ) -> str:
        """
        Save intrinsic values to CSV file.
        
        Args:
            intrinsic_values (Dict[str, float]): Dictionary of {symbol: intrinsic_value}
            
        Returns:
            str: Path to saved file
        """
        return self.storage.save_intrinsic_values(intrinsic_values)
    
    def save_financial_data(
        self, 
        financial_data: Dict[str, pd.DataFrame]
    ) -> str:
        """
        Save financial data to CSV file.
        
        Args:
            financial_data (Dict[str, pd.DataFrame]): Dictionary of {symbol: financial_df}
            
        Returns:
            str: Path to saved file
        """
        return self.storage.save_financial_data(financial_data)
    
    def process_portfolio(
        self, 
        portfolio_name: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        weights: List[float] = None,
        save_data: bool = True
    ) -> Dict:
        """
        Process a portfolio: fetch data, calculate metrics, and optionally save to files.
        
        Args:
            portfolio_name (str): Portfolio name
            symbols (List[str]): List of stock symbols in the portfolio
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            weights (List[float]): List of weights for each symbol (optional)
            save_data (bool): Whether to save data to files
            
        Returns:
            Dict: Dictionary with portfolio data and metrics
        """
        # Fetch data for all symbols
        stock_data = self.fetch_stock_data(symbols, start_date, end_date)
        
        # Calculate performance metrics for each symbol
        performance_metrics = {}
        for symbol, data in stock_data.items():
            metrics = self.calculate_performance_metrics(symbol, data)
            performance_metrics[symbol] = metrics
        
        # Create portfolio object
        portfolio = Portfolio(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            source=self.source,
            weights=weights,
            name=portfolio_name,
            fetched_data=stock_data
        )
        
        portfolio_metrics = portfolio.get_performance_metrics()
        portfolio_value_series = portfolio.get_portfolio_value_series()
        
        result = {
            'portfolio_name': portfolio_name,
            'stock_data': stock_data,
            'performance_metrics': performance_metrics,
            'portfolio_metrics': portfolio_metrics,
            'portfolio_value_series': portfolio_value_series
        }
        
        # Save data if requested
        if save_data:
            # Save individual stock data and portfolio history
            self.save_portfolio_history(portfolio_name, stock_data)
            
            # Save performance metrics
            self.save_performance_metrics(performance_metrics, portfolio_name)
            
            # Save portfolio metrics
            portfolio_metrics_dict = {portfolio_name: portfolio_metrics}
            self.save_performance_metrics(portfolio_metrics_dict, f"{portfolio_name}_portfolio")
        
        return result
    
    def process_all_symbols(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        calculate_intrinsic: bool = True,
        save_data: bool = True
    ) -> Dict:
        """
        Process all symbols: fetch data, calculate metrics and intrinsic values.
        
        Args:
            symbols (List[str]): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            calculate_intrinsic (bool): Whether to calculate intrinsic values
            save_data (bool): Whether to save data to files
            
        Returns:
            Dict: Dictionary with all processed data
        """
        # Fetch data for all symbols
        stock_data = self.fetch_stock_data(symbols, start_date, end_date)
        
        # Calculate performance metrics for each symbol
        performance_metrics = {}
        for symbol, data in stock_data.items():
            metrics = self.calculate_performance_metrics(symbol, data)
            performance_metrics[symbol] = metrics
        
        result = {
            'stock_data': stock_data,
            'performance_metrics': performance_metrics
        }
        
        # Calculate intrinsic values if requested
        if calculate_intrinsic:
            intrinsic_values = {}
            financial_data = {}
            
            for symbol in symbols:
                # Fetch financial data
                fin_data = self.fetcher.fetch_financial_data(symbol)
                if fin_data is not None:
                    financial_data[symbol] = fin_data
                
                # Calculate intrinsic value
                iv = self.calculate_intrinsic_value(symbol)
                intrinsic_values[symbol] = iv
            
            result['intrinsic_values'] = intrinsic_values
            result['financial_data'] = financial_data
        
        # Save data if requested
        if save_data:
            # Save merged history data
            dfs = []
            for symbol, df in stock_data.items():
                if 'time' in df.columns and 'close' in df.columns:
                    temp_df = df[['time', 'close']].copy()
                    temp_df['time'] = temp_df['time'].astype(str)
                    temp_df = temp_df.rename(columns={'close': symbol})
                    dfs.append(temp_df.set_index('time'))
            
            if dfs:
                merged_df = pd.concat(dfs, axis=1, join='outer').reset_index()
                
                # Save to dated folder
                dated_folder = self.storage._create_dated_folder()
                merged_file_path = os.path.join(
                    dated_folder, 
                    f"history_data_all_symbols_{self.storage._get_dated_folder_name()}.csv"
                )
                merged_df.to_csv(merged_file_path, index=False)
                
                # Copy to root data folder
                root_all_symbols_path = os.path.join(self.base_output_dir, "history_data_all_symbols.csv")
                merged_df.to_csv(root_all_symbols_path, index=False)
            
            # Save performance metrics
            self.save_performance_metrics(performance_metrics)
            
            # Save intrinsic values if calculated
            if calculate_intrinsic and intrinsic_values:
                self.save_intrinsic_values(intrinsic_values)
                
                # Save financial data if available
                if financial_data:
                    self.save_financial_data(financial_data)
        
        return result
    
    def load_latest_data(self, data_type: str = 'history') -> pd.DataFrame:
        """
        Load the latest data from the root data folder.
        
        Args:
            data_type (str): Type of data to load ('history', 'perf', 'intrinsic', 'fin')
            
        Returns:
            pd.DataFrame: Loaded DataFrame or empty DataFrame if file not found
        """
        return self.storage.load_latest_data(data_type)
    
    def clear_caches(self):
        """Clear all caches."""
        self.fetcher.clear_cache()
        self.calculator.clear_cache()