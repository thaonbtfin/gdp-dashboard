"""
DataStorage Module

This module provides the DataStorage class for storing and loading stock data.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..utils.cache_utils import read_csv_cached, get_latest_file_path

class DataStorage:
    """
    DataStorage handles storing and loading stock data.
    """
    
    def __init__(self, base_output_dir: str):
        """
        Initialize the DataStorage.
        
        Args:
            base_output_dir (str): Base directory for data storage
        """
        self.base_output_dir = base_output_dir
        
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
        
        # Try to get the file path from cache
        cached_path = get_latest_file_path(data_type)
        if cached_path and os.path.exists(cached_path):
            file_path = cached_path
        
        if os.path.exists(file_path):
            # Use cached reading if available
            return read_csv_cached(file_path)
        else:
            print(f"Warning: File not found: {file_path}")
            return pd.DataFrame()