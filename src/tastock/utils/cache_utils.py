"""
Cache utilities for the tastock application.

This module provides functions for caching data in memory to improve performance.
"""

import os
import pandas as pd
from functools import lru_cache
from datetime import datetime, timedelta

from src.constants import DATA_DIR

# Dictionary to store cached dataframes with timestamps
_dataframe_cache = {}
_cache_expiry = 3600  # Cache expiry in seconds (1 hour)

def get_cached_dataframe(file_path, max_age_seconds=_cache_expiry):
    """
    Get a dataframe from cache if available and not expired.
    
    Args:
        file_path (str): Path to the file
        max_age_seconds (int): Maximum age of cache in seconds
        
    Returns:
        pd.DataFrame: Cached dataframe or None if not available
    """
    now = datetime.now()
    
    if file_path in _dataframe_cache:
        timestamp, df = _dataframe_cache[file_path]
        age = (now - timestamp).total_seconds()
        
        if age <= max_age_seconds:
            return df
    
    return None

def cache_dataframe(file_path, df):
    """
    Cache a dataframe in memory.
    
    Args:
        file_path (str): Path to the file
        df (pd.DataFrame): Dataframe to cache
        
    Returns:
        pd.DataFrame: The cached dataframe
    """
    _dataframe_cache[file_path] = (datetime.now(), df)
    return df

def read_csv_cached(file_path, max_age_seconds=_cache_expiry, **kwargs):
    """
    Read a CSV file with caching.
    
    Args:
        file_path (str): Path to the CSV file
        max_age_seconds (int): Maximum age of cache in seconds
        **kwargs: Additional arguments to pass to pd.read_csv
        
    Returns:
        pd.DataFrame: The dataframe from the CSV file
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    # Check if we have a cached version
    cached_df = get_cached_dataframe(file_path, max_age_seconds)
    if cached_df is not None:
        return cached_df
    
    # Read the file and cache it
    try:
        df = pd.read_csv(file_path, **kwargs)
        return cache_dataframe(file_path, df)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=32)
def get_latest_file_path(data_type):
    """
    Get the path to the latest data file of a specific type.
    
    Args:
        data_type (str): Type of data ('history', 'perf', 'intrinsic', 'fin')
        
    Returns:
        str: Path to the latest file or None if not found
    """
    file_map = {
        'history': "history_data_all_symbols.csv",
        'perf': "perf_all_symbols.csv",
        'intrinsic': "intrinsic_value_all_symbols.csv",
        'fin': "fin_all_symbols.csv"
    }
    
    if data_type not in file_map:
        return None
    
    file_path = os.path.join(DATA_DIR, file_map[data_type])
    
    if os.path.exists(file_path):
        return file_path
    
    return None