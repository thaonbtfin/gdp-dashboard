"""
Data Fetcher Module

This module provides classes for fetching stock data via API and orchestrating fetch workflows.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from vnstock import Vnstock
from src.constants import DEFAULT_SOURCE

class DataFetcher:
    """
    DataFetcher handles fetching stock data and caching it to avoid duplicate requests.
    """
    
    def __init__(self, source: str = DEFAULT_SOURCE):
        """
        Initialize the DataFetcher.
        
        Args:
            source (str): Data source for stock information
        """
        self.source = source
        
        # Cache to store fetched data
        self._stock_data_cache = {}  # {symbol_start_date_end_date: dataframe}
        self._financial_data_cache = {}  # {symbol: financial_df}
        
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
            for symbol in symbols_to_fetch:
                try:
                    stock_obj = Vnstock().stock(symbol=symbol, source=self.source)
                    data = stock_obj.quote.history(start=start_date, end=end_date)
                    
                    cache_key = f"{symbol}_{start_date}_{end_date}"
                    self._stock_data_cache[cache_key] = data
                    result[symbol] = data
                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")
                    result[symbol] = pd.DataFrame()
        
        return result
    
    def fetch_financial_data(self, symbol: str, force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Fetch financial data for a symbol.
        
        Args:
            symbol (str): Stock symbol
            force_refresh (bool): If True, ignore cache and fetch fresh data
            
        Returns:
            Optional[pd.DataFrame]: Financial data DataFrame or None if fetch fails
        """
        if not force_refresh and symbol in self._financial_data_cache:
            return self._financial_data_cache[symbol]
        
        # Fetch financial data directly using vnstock
        try:
            financial_data = Vnstock().stock(symbol=symbol, source=self.source).finance.ratio(period='year', lang='vi', dropna=True)
            
            if not financial_data.empty:
                self._financial_data_cache[symbol] = financial_data
                return financial_data
            
            return None
        except Exception as e:
            print(f"Error fetching financial data for {symbol}: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached data."""
        self._stock_data_cache.clear()
        self._financial_data_cache.clear()

# Workflow classes are in workflow_fetcher.py to avoid circular imports