"""
Portfolio Loader - CSV Based
Reads portfolio symbols directly from CSV files in data folder structure
"""
import pandas as pd
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime

def get_latest_data_folder() -> str:
    """Get the latest data folder (e.g., data/20251118)"""
    data_dir = Path("data")
    if not data_dir.exists():
        return ""
    
    # Find folders with date format YYYYMMDD
    date_folders = []
    for folder in data_dir.iterdir():
        if folder.is_dir() and folder.name.isdigit() and len(folder.name) == 8:
            try:
                datetime.strptime(folder.name, "%Y%m%d")
                date_folders.append(folder.name)
            except ValueError:
                continue
    
    if not date_folders:
        return ""
    
    # Return the latest date folder
    return max(date_folders)

def get_portfolio_symbols_from_csv(portfolio_name: str) -> List[str]:
    """Get symbols for a portfolio by reading CSV column headers"""
    latest_folder = get_latest_data_folder()
    if not latest_folder:
        return []
    
    csv_path = Path(f"data/{latest_folder}/{portfolio_name}/history_data_all_symbols.csv")
    
    if not csv_path.exists():
        return []
    
    try:
        # Read only the first row to get column headers
        df = pd.read_csv(csv_path, nrows=0)
        symbols = [col for col in df.columns if col != 'time']
        return symbols
    except Exception as e:
        print(f"⚠️ Error reading {csv_path}: {e}")
        return []

def get_all_portfolios_from_csv() -> Dict[str, List[str]]:
    """Get all portfolios by reading from CSV files in data folder"""
    latest_folder = get_latest_data_folder()
    if not latest_folder:
        print("⚠️ No data folder found")
        return {}
    
    data_path = Path(f"data/{latest_folder}")
    if not data_path.exists():
        print(f"⚠️ Data path {data_path} does not exist")
        return {}
    
    portfolios = {}
    
    # Scan for portfolio folders
    for portfolio_folder in data_path.iterdir():
        if portfolio_folder.is_dir():
            portfolio_name = portfolio_folder.name
            symbols = get_portfolio_symbols_from_csv(portfolio_name)
            if symbols:
                portfolios[portfolio_name] = symbols
                print(f"📊 Loaded {portfolio_name}: {len(symbols)} symbols")
    
    print(f"✅ Loaded {len(portfolios)} portfolios from CSV files")
    return portfolios

def get_portfolios_csv() -> Dict[str, List[str]]:
    """Main function to get portfolios from CSV files"""
    return get_all_portfolios_from_csv()

# For backward compatibility
def get_portfolios_fast() -> Dict[str, List[str]]:
    """Backward compatibility function"""
    return get_portfolios_csv()