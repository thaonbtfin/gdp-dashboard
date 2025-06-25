"""
Data Workflow Script

This script provides a complete workflow for:
1. Downloading CafeF data
2. Processing stock data for portfolios
3. Copying latest files to root data folder
4. Scheduling the workflow
"""

import os
import sys
import shutil
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("Warning: 'schedule' module not available. Install with: pip install schedule")
import time
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional, Tuple
import requests
import zipfile
from urllib.parse import urlparse
from email.message import Message

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from src.constants import *
from src.tastock.workflows.wf_components import StructuredDataProcessor, FileCopier

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
        """Download and extract CafeF data"""
        effective_date = self._get_effective_date(target_date)
        
        date_yyyymmdd = effective_date.strftime("%Y%m%d")
        date_ddmmyyyy = effective_date.strftime("%d%m%Y")
        
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
                self._ensure_directory_exists(extract_dir, clean_if_exists=True)
                
                with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                print(f"Extracted to: {extract_dir}")
                return True, extract_dir
            
            return True, None
            
        except Exception as e:
            print(f"Download failed: {e}")
            return False, None

# Classes are now imported from workflow_components

class DataWorkflowDownload:
    """Main workflow orchestrator"""
    
    def __init__(self, download_dir: str = None, data_dir: str = 'data'):
        if download_dir is None:
            script_dir = Path(__file__).resolve().parent
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
    
    def schedule_workflow(self, time_str: str = "09:00", symbols: list = None):
        """Schedule the workflow to run daily"""
        if not SCHEDULE_AVAILABLE:
            print("Schedule module not available. Install with: pip install schedule")
            print("Alternative: Use cron job or task scheduler to run this script daily")
            return
        
        print(f"Scheduling workflow to run daily at {time_str}")
        
        schedule.every().day.at(time_str).do(
            lambda: self.run_full_workflow(symbols=symbols)
        )
        
        print("Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nScheduler stopped")

def main():
    """Main function"""
    workflow = DataWorkflowDownload()
    
    # Run workflow once
    workflow.run_full_workflow(symbols=SYMBOLS_VN100, portfolio_name='VN100')
    
    # Uncomment to schedule daily runs
    # workflow.schedule_workflow("09:00", symbols=SYMBOLS_VN30)

if __name__ == "__main__":
    main()