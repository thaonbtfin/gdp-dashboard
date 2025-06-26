"""
Data Downloader Module

This module provides classes for downloading CafeF data and orchestrating download workflows.
"""

import shutil
import requests
import zipfile
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
from email.message import Message

from ..workflows.wf_components import StructuredDataProcessor, FileCopier, DataFileManager

class DataDownloader:
    """Handles downloading and extracting CafeF data"""
    
    CAFEF_URL_TEMPLATE = "https://cafef1.mediacdn.vn/data/ami_data/{date_yyyymmdd}/CafeF.SolieuGD.Upto{date_ddmmyyyy}.zip"
    DEFAULT_CHUNK_SIZE = 8192
    
    def __init__(self, download_dir: str):
        self.download_dir = Path(download_dir)
        self._ensure_directory_exists(self.download_dir)
    
    def _ensure_directory_exists(self, directory_path: Path, clean_if_exists: bool = False):
        if not directory_path.exists():
            directory_path.mkdir(parents=True, exist_ok=True)
        elif clean_if_exists:
            shutil.rmtree(directory_path)
            directory_path.mkdir(parents=True, exist_ok=True)
    
    def _get_effective_date(self, target_date: Optional[date] = None) -> date:
        if target_date:
            return target_date
        
        today = date.today()
        effective_date = today - timedelta(days=1)
        
        # Adjust if yesterday was a weekend
        if effective_date.weekday() == 5:  # Saturday
            effective_date -= timedelta(days=1)
        elif effective_date.weekday() == 6:  # Sunday
            effective_date -= timedelta(days=2)
        
        return effective_date
    
    def _get_filename_from_response(self, response: requests.Response, url: str) -> str:
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            msg = Message()
            msg['content-disposition'] = content_disposition
            filename = msg.get_filename()
            if filename:
                return filename
        
        parsed_url = urlparse(url)
        filename_from_url = Path(parsed_url.path).name
        return filename_from_url if filename_from_url else "downloaded_file"
    
    def download_and_extract(self, target_date: Optional[date] = None) -> Tuple[bool, Optional[Path]]:
        """Download and extract CafeF data, skip if already exists"""
        effective_date = self._get_effective_date(target_date)
        
        date_yyyymmdd = effective_date.strftime("%Y%m%d")
        date_ddmmyyyy = effective_date.strftime("%d%m%Y")
        
        # Check if data is already extracted
        expected_extract_dir = self.download_dir / f"CafeF.SolieuGD.Upto{date_ddmmyyyy}"
        if self._is_data_already_available(expected_extract_dir):
            print(f"Data already available at: {expected_extract_dir}")
            return True, expected_extract_dir
        
        # Check if zip file already exists
        expected_zip_file = self.download_dir / f"CafeF.SolieuGD.Upto{date_ddmmyyyy}.zip"
        if expected_zip_file.exists():
            print(f"Zip file already exists: {expected_zip_file}")
            return self._extract_existing_zip(expected_zip_file, expected_extract_dir)
        
        # Download if not exists
        url = self.CAFEF_URL_TEMPLATE.format(
            date_yyyymmdd=date_yyyymmdd,
            date_ddmmyyyy=date_ddmmyyyy
        )
        
        try:
            print(f"Downloading from: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            filename = self._get_filename_from_response(response, url)
            downloaded_file = self.download_dir / filename
            
            with open(downloaded_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.DEFAULT_CHUNK_SIZE):
                    f.write(chunk)
            
            print(f"Downloaded: {downloaded_file}")
            
            # Extract if zip file
            if filename.lower().endswith('.zip'):
                extract_dir = self.download_dir / Path(filename).stem
                return self._extract_existing_zip(downloaded_file, extract_dir)
            
            return True, None
            
        except Exception as e:
            print(f"Download failed: {e}")
            return False, None
    
    def _is_data_already_available(self, extract_dir: Path) -> bool:
        """Check if extracted data is already available and valid"""
        if not extract_dir.exists():
            return False
        
        # Check if directory contains CSV files
        csv_files = list(extract_dir.glob("*.csv"))
        if len(csv_files) >= 3:  # Expect at least HSX, HNX, UPCOM files
            print(f"Found {len(csv_files)} CSV files in {extract_dir}")
            return True
        
        return False
    
    def _extract_existing_zip(self, zip_file: Path, extract_dir: Path) -> Tuple[bool, Optional[Path]]:
        """Extract existing zip file"""
        try:
            self._ensure_directory_exists(extract_dir, clean_if_exists=True)
            
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            print(f"Extracted to: {extract_dir}")
            return True, extract_dir
            
        except Exception as e:
            print(f"Extraction failed: {e}")
            return False, None

class DataWorkflowDownload:
    """Main workflow orchestrator for download-based data processing"""
    
    def __init__(self, download_dir: str = None, data_dir: str = 'data'):
        if download_dir is None:
            from pathlib import Path
            script_dir = Path(__file__).resolve().parent.parent / "scripts"
            download_dir = str(script_dir / ".temp")
        
        self.downloader = DataDownloader(download_dir)
        self.processor = StructuredDataProcessor(data_dir)
        self.copier = FileCopier(data_dir, data_dir)
    
    def run_full_workflow(self, target_date: Optional[date] = None, symbols: list = None, portfolio_name: str = 'VN30') -> bool:
        """Run the complete workflow"""
        print(f"=== Starting Data Workflow for {portfolio_name} ===")
        
        # Step 1: Download data
        print("\n1. Downloading CafeF data...")
        success, extract_dir = self.downloader.download_and_extract(target_date)
        if not success or not extract_dir:
            print("Download failed")
            return False
        
        # Step 2: Process data with portfolio structure
        print(f"\n2. Processing portfolio data for {portfolio_name}...")
        success = self.processor.process_from_local_files(extract_dir, portfolio_name, symbols)
        if not success:
            print("Data processing failed")
            return False
        
        # Step 3: Copy latest files
        print("\n3. Copying latest files to root...")
        success = self.copier.copy_latest_files()
        if not success:
            print("File copying failed")
            return False
        
        print(f"\n=== Workflow completed successfully for {portfolio_name} ===")
        return True
    
    def schedule_workflow(self, time_str: str = "09:00", symbols: list = None, portfolio_name: str = 'VN30'):
        """Schedule the workflow to run daily"""
        try:
            import schedule
            print(f"Scheduling workflow to run daily at {time_str}")
            
            schedule.every().day.at(time_str).do(
                lambda: self.run_full_workflow(symbols=symbols, portfolio_name=portfolio_name)
            )
            
            print("Scheduler started. Press Ctrl+C to stop.")
            import time
            while True:
                schedule.run_pending()
                time.sleep(60)
        except ImportError:
            print("Schedule module not available. Install with: pip install schedule")
        except KeyboardInterrupt:
            print("\nScheduler stopped")
    
    def merge_all_portfolios_to_root(self) -> bool:
        """Merge all portfolios data from latest date folder to root history file"""
        try:
            base_dir = Path(self.processor.base_output_dir)
            
            # Find latest date folder
            date_folders = [d for d in base_dir.iterdir() if d.is_dir() and d.name.isdigit() and len(d.name) == 8]
            if not date_folders:
                print("No date folders found")
                return False
            
            latest_date_folder = max(date_folders, key=lambda x: x.name)
            print(f"Using latest date folder: {latest_date_folder.name}")
            
            # Find all portfolio folders
            portfolio_folders = [d for d in latest_date_folder.iterdir() if d.is_dir()]
            if not portfolio_folders:
                print("No portfolio folders found")
                return False
            
            all_symbols_data = {}
            
            # Collect data from all portfolios
            for portfolio_folder in portfolio_folders:
                history_file = portfolio_folder / 'history_data_all_symbols.csv'
                if history_file.exists():
                    try:
                        df = pd.read_csv(history_file)
                        if 'time' in df.columns:
                            df = df.set_index('time')
                            # Add all symbol columns to combined data
                            for col in df.columns:
                                if col not in all_symbols_data:
                                    all_symbols_data[col] = df[col]
                        print(f"Added data from {portfolio_folder.name}: {len(df.columns)} symbols")
                    except Exception as e:
                        print(f"Error reading {history_file}: {e}")
            
            if not all_symbols_data:
                print("No valid data found to merge")
                return False
            
            # Create merged DataFrame
            merged_df = pd.DataFrame(all_symbols_data)
            merged_df = merged_df.fillna(0)
            merged_df = merged_df.reset_index()
            
            # Save to root
            root_file = base_dir / 'history_data_all_symbols.csv'
            merged_df.to_csv(root_file, index=False)
            
            print(f"Merged {len(merged_df.columns)-1} symbols to {root_file}")
            return True
            
        except Exception as e:
            print(f"Merge failed: {e}")
            return False
    
    def merge_all_portfolios_perf_to_root(self) -> bool:
        """Merge all portfolios performance metrics from latest date folder to root perf file"""
        try:
            base_dir = Path(self.processor.base_output_dir)
            
            # Find latest date folder
            date_folders = [d for d in base_dir.iterdir() if d.is_dir() and d.name.isdigit() and len(d.name) == 8]
            if not date_folders:
                print("No date folders found")
                return False
            
            latest_date_folder = max(date_folders, key=lambda x: x.name)
            print(f"Using latest date folder for perf: {latest_date_folder.name}")
            
            # Find all portfolio folders
            portfolio_folders = [d for d in latest_date_folder.iterdir() if d.is_dir()]
            if not portfolio_folders:
                print("No portfolio folders found")
                return False
            
            all_perf_data = []
            
            # Collect performance data from all portfolios
            for portfolio_folder in portfolio_folders:
                perf_file = portfolio_folder / 'perf_all_symbols.csv'
                if perf_file.exists():
                    try:
                        df = pd.read_csv(perf_file)
                        if not df.empty:
                            all_perf_data.append(df)
                        print(f"Added perf data from {portfolio_folder.name}: {len(df)} symbols")
                    except Exception as e:
                        print(f"Error reading {perf_file}: {e}")
            
            if not all_perf_data:
                print("No valid performance data found to merge")
                return False
            
            # Combine all performance data
            merged_perf_df = pd.concat(all_perf_data, ignore_index=True)
            
            # Remove duplicates (keep first occurrence)
            merged_perf_df = merged_perf_df.drop_duplicates(subset=['symbol'], keep='first')
            
            # Save to root
            root_perf_file = base_dir / 'perf_all_symbols.csv'
            merged_perf_df.to_csv(root_perf_file, index=False)
            
            print(f"Merged {len(merged_perf_df)} symbols performance to {root_perf_file}")
            return True
            
        except Exception as e:
            print(f"Performance merge failed: {e}")
            return False
    
    def copy_history_to_root(self) -> bool:
        """Copy history_data_all_symbols.csv to history_data.csv"""
        return DataFileManager.copy_history_to_root(str(self.processor.base_output_dir))
    
    def cleanup_old_date_folders(self, keep_count: int = 3) -> bool:
        """Remove old date folders, keeping only the latest ones"""
        return DataFileManager.cleanup_old_date_folders(str(self.processor.base_output_dir), keep_count)
    
    def _fix_vnindex_symbol(self, stock_data: dict) -> dict:
        """Rename VNAll-INDEX to VNINDEX in stock data"""
        if 'VNAll-INDEX' in stock_data:
            stock_data['VNINDEX'] = stock_data.pop('VNAll-INDEX')
            print("Renamed VNAll-INDEX to VNINDEX")
        return stock_data
    
    def _add_vnindex_data(self, stock_data: dict, start_date: str, end_date: str) -> dict:
        """Add VNINDEX data to existing stock data"""
        try:
            from vnstock import Vnstock
            print("Fetching VNINDEX data...")
            
            # Fetch VNINDEX data
            vnstock_obj = Vnstock().stock(symbol='VNINDEX', source='VCI')
            vnindex_data = vnstock_obj.quote.history(start=start_date, end=end_date)
            
            if not vnindex_data.empty:
                # Rename columns to match expected format
                if 'time' not in vnindex_data.columns and vnindex_data.index.name:
                    vnindex_data = vnindex_data.reset_index()
                    vnindex_data = vnindex_data.rename(columns={vnindex_data.columns[0]: 'time'})
                
                # Add VNINDEX to stock_data
                stock_data['VNINDEX'] = vnindex_data
                print(f"Added VNINDEX data: {len(vnindex_data)} records")
            else:
                print("No VNINDEX data available")
                
        except Exception as e:
            print(f"Failed to fetch VNINDEX data: {e}")
            
        return stock_data