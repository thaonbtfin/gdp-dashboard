"""
DataManager Module

This module provides a centralized way to fetch, calculate, and manage data for both
portfolios and symbols in the tastock application. It optimizes data fetching by avoiding
duplicate requests and organizes data storage in a logical folder structure.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from .fetcher import Fetcher
from .calculator import Calculator
from .stock import Stock
from .portfolio import Portfolio
from .helpers import Helpers
from src.constants import DEFAULT_SOURCE, DEFAULT_OUTPUT_DIR

class DataManager:
    """
    DataManager handles fetching, calculating, and storing data for stocks and portfolios.
    It optimizes data fetching by avoiding duplicate requests and organizes data storage.
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
        self.fetcher = Fetcher(source=source, output_dir=base_output_dir)
        
        # Cache to store fetched data
        self._stock_data_cache = {}  # {symbol: dataframe}
        self._performance_metrics_cache = {}  # {symbol: metrics_dict}
        self._intrinsic_value_cache = {}  # {symbol: value}
        self._financial_data_cache = {}  # {symbol: financial_df}
        
        # Create data directory structure if it doesn't exist
        self._ensure_data_directories()
        
    def _ensure_data_directories(self):
        """Create the necessary directory structure for data storage."""
        os.makedirs(self.base_output_dir, exist_ok=True)
        
    def _get_dated_folder_name(self) -> str:
        """Get a folder name based on current date."""
        return datetime.now().strftime('%Y%m%d')
    
    def _create_dated_folder(self) -> str:
        """Create and return a dated folder path."""
        dated_folder = os.path.join(self.base_output_dir, self._get_dated_folder_name())
        os.makedirs(dated_folder, exist_ok=True)
        return dated_folder
    
    def _create_portfolio_folder(self, portfolio_name: str, dated_folder: str = None) -> str:
        """Create and return a portfolio folder path within the dated folder."""
        if dated_folder is None:
            dated_folder = self._create_dated_folder()
        portfolio_folder = os.path.join(dated_folder, portfolio_name)
        os.makedirs(portfolio_folder, exist_ok=True)
        
        # Create symbols subfolder
        symbols_folder = os.path.join(portfolio_folder, "symbols")
        os.makedirs(symbols_folder, exist_ok=True)
        
        return portfolio_folder
    
    def fetch_stock_data(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str,
        force_refresh: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for the given symbols, using cache when available.
        
        Args:
            symbols (List[str]): List of stock symbols
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            force_refresh (bool): If True, ignore cache and fetch fresh data
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of {symbol: dataframe}
        """
        result = {}
        symbols_to_fetch = []
        
        # Check cache first
        for symbol in symbols:
            cache_key = f"{symbol}_{start_date}_{end_date}"
            if not force_refresh and cache_key in self._stock_data_cache:
                result[symbol] = self._stock_data_cache[cache_key]
            else:
                symbols_to_fetch.append(symbol)
        
        # Fetch only what's not in cache
        if symbols_to_fetch:
            fetched_data = self.fetcher.fetch_history_to_dataframe_from_start_end_date(
                symbols=symbols_to_fetch,
                start_date=start_date,
                end_date=end_date
            )
            
            # Update cache and result
            for symbol, data in fetched_data.items():
                cache_key = f"{symbol}_{start_date}_{end_date}"
                self._stock_data_cache[cache_key] = data
                result[symbol] = data
        
        return result
    
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
        if not force_recalculate and symbol in self._performance_metrics_cache:
            return self._performance_metrics_cache[symbol]
        
        if data is None:
            # Try to get from cache
            for cache_key, df in self._stock_data_cache.items():
                if cache_key.startswith(f"{symbol}_"):
                    data = df
                    break
            
            if data is None:
                raise ValueError(f"No data available for {symbol}. Fetch data first.")
        
        metrics = Calculator.calculate_series_performance_metrics(data, price_column='close')
        self._performance_metrics_cache[symbol] = metrics
        return metrics
    
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
        if not force_recalculate and symbol in self._intrinsic_value_cache:
            return self._intrinsic_value_cache[symbol]
        
        # Create a temporary Stock object to calculate intrinsic value
        # This is not ideal but reuses existing code
        try:
            stock = Stock(
                symbol=symbol,
                start_date=datetime.now().strftime('%Y-%m-%d'),  # Just need today for financial data
                end_date=datetime.now().strftime('%Y-%m-%d'),
                source=self.source
            )
            intrinsic_value = stock.get_intrinsic_value_graham()
            self._intrinsic_value_cache[symbol] = intrinsic_value
            
            # Also cache the financial data if available
            if stock.financial_ratios_df is not None:
                self._financial_data_cache[symbol] = stock.financial_ratios_df
                
            return intrinsic_value
        except Exception as e:
            print(f"Error calculating intrinsic value for {symbol}: {e}")
            return None
    
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
        dated_folder = self._create_dated_folder()
        
        if portfolio_name:
            portfolio_folder = self._create_portfolio_folder(portfolio_name, dated_folder)
            symbols_folder = os.path.join(portfolio_folder, "symbols")
            file_path = os.path.join(symbols_folder, f"{symbol}_history_{self._get_dated_folder_name()}.csv")
        else:
            file_path = os.path.join(dated_folder, f"{symbol}_history_{self._get_dated_folder_name()}.csv")
        
        data.to_csv(file_path, index=False)
        return file_path
    
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
        dated_folder = self._create_dated_folder()
        portfolio_folder = self._create_portfolio_folder(portfolio_name, dated_folder)
        
        # Save individual symbol data
        symbols_folder = os.path.join(portfolio_folder, "symbols")
        for symbol, df in data.items():
            file_path = os.path.join(symbols_folder, f"{symbol}_history_{self._get_dated_folder_name()}.csv")
            df.to_csv(file_path, index=False)
        
        # Create merged history file
        merged_file_path = os.path.join(
            portfolio_folder, 
            f"history_{portfolio_name}_{self._get_dated_folder_name()}.csv"
        )
        
        # Merge on 'time' column
        dfs = []
        for symbol, df in data.items():
            if 'time' in df.columns and 'close' in df.columns:
                temp_df = df[['time', 'close']].copy()
                temp_df['time'] = temp_df['time'].astype(str)
                temp_df = temp_df.rename(columns={'close': symbol})
                dfs.append(temp_df.set_index('time'))
        
        if dfs:
            merged_df = pd.concat(dfs, axis=1, join='outer').reset_index()
            merged_df.to_csv(merged_file_path, index=False)
        
        # Also save to all symbols history
        all_symbols_file_path = os.path.join(
            dated_folder, 
            f"history_data_all_symbols_{self._get_dated_folder_name()}.csv"
        )
        
        if dfs:
            merged_df.to_csv(all_symbols_file_path, index=False)
            
            # Copy to root data folder
            root_all_symbols_path = os.path.join(self.base_output_dir, "history_data_all_symbols.csv")
            merged_df.to_csv(root_all_symbols_path, index=False)
        
        return merged_file_path, all_symbols_file_path
    
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
        dated_folder = self._create_dated_folder()
        
        # Convert metrics to DataFrame
        metrics_list = []
        for symbol, metrics in metrics_data.items():
            metrics_entry = {'symbol': symbol, **metrics}
            metrics_list.append(metrics_entry)
        
        metrics_df = pd.DataFrame(metrics_list)
        
        if portfolio_name:
            portfolio_folder = self._create_portfolio_folder(portfolio_name, dated_folder)
            file_path = os.path.join(
                portfolio_folder, 
                f"perf_{portfolio_name}_{self._get_dated_folder_name()}.csv"
            )
        else:
            file_path = os.path.join(
                dated_folder, 
                f"perf_all_symbols_{self._get_dated_folder_name()}.csv"
            )
        
        metrics_df.to_csv(file_path, index=False)
        
        # Copy to root data folder if it's the all symbols metrics
        if not portfolio_name:
            root_metrics_path = os.path.join(self.base_output_dir, "perf_all_symbols.csv")
            metrics_df.to_csv(root_metrics_path, index=False)
        
        return file_path
    
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
        dated_folder = self._create_dated_folder()
        
        # Convert to DataFrame
        iv_list = []
        for symbol, value in intrinsic_values.items():
            iv_entry = {'symbol': symbol, 'intrinsic_value': value}
            iv_list.append(iv_entry)
        
        iv_df = pd.DataFrame(iv_list)
        
        file_path = os.path.join(
            dated_folder, 
            f"intrinsic_value_all_symbols_{self._get_dated_folder_name()}.csv"
        )
        
        iv_df.to_csv(file_path, index=False)
        
        # Copy to root data folder
        root_iv_path = os.path.join(self.base_output_dir, "intrinsic_value_all_symbols.csv")
        iv_df.to_csv(root_iv_path, index=False)
        
        return file_path
    
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
        dated_folder = self._create_dated_folder()
        
        # Process and combine financial data
        processed_data = {}
        for symbol, df in financial_data.items():
            if df is not None and not df.empty:
                # Add symbol column
                df_copy = df.copy()
                df_copy['symbol'] = symbol
                processed_data[symbol] = df_copy
        
        if processed_data:
            # Combine all financial data
            combined_df = pd.concat(processed_data.values(), ignore_index=True)
            
            file_path = os.path.join(
                dated_folder, 
                f"fin_all_symbols_{self._get_dated_folder_name()}.csv"
            )
            
            combined_df.to_csv(file_path, index=False)
            
            # Copy to root data folder
            root_fin_path = os.path.join(self.base_output_dir, "fin_all_symbols.csv")
            combined_df.to_csv(root_fin_path, index=False)
            
            return file_path
        
        return None
    
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
                iv = self.calculate_intrinsic_value(symbol)
                intrinsic_values[symbol] = iv
                
                # Get financial data from cache if available
                if symbol in self._financial_data_cache:
                    financial_data[symbol] = self._financial_data_cache[symbol]
            
            result['intrinsic_values'] = intrinsic_values
            result['financial_data'] = financial_data
        
        # Save data if requested
        if save_data:
            # Save merged history data
            dated_folder = self._create_dated_folder()
            merged_file_path = os.path.join(
                dated_folder, 
                f"history_data_all_symbols_{self._get_dated_folder_name()}.csv"
            )
            
            # Merge on 'time' column
            dfs = []
            for symbol, df in stock_data.items():
                if 'time' in df.columns and 'close' in df.columns:
                    temp_df = df[['time', 'close']].copy()
                    temp_df['time'] = temp_df['time'].astype(str)
                    temp_df = temp_df.rename(columns={'close': symbol})
                    dfs.append(temp_df.set_index('time'))
            
            if dfs:
                merged_df = pd.concat(dfs, axis=1, join='outer').reset_index()
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
        file_map = {
            'history': "history_data_all_symbols.csv",
            'perf': "perf_all_symbols.csv",
            'intrinsic': "intrinsic_value_all_symbols.csv",
            'fin': "fin_all_symbols.csv"
        }
        
        if data_type not in file_map:
            raise ValueError(f"Invalid data type: {data_type}. Must be one of {list(file_map.keys())}")
        
        file_path = os.path.join(self.base_output_dir, file_map[data_type])
        
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            print(f"Warning: File not found: {file_path}")
            return pd.DataFrame()