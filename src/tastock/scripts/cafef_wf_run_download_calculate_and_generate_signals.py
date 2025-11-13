#!/usr/bin/env python3
"""
Download and Update Workflow Runner

Runs the complete data processing workflow in sequence:
1. Download data from CafeF
2. Calculate metrics from history
3. Generate investment signals
"""

import os
import sys
import subprocess
from datetime import datetime

def run_script(script_path, script_name):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {script_name}")
    print(f"{'='*60}")
    print(f"Script: {script_path}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run the script
        result = subprocess.run([sys.executable, script_path], 
                              cwd=os.path.dirname(script_path))
        
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            return True
        else:
            print(f"❌ {script_name} failed with return code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Run the complete workflow"""
    print("🎯 TASTOCK DOWNLOAD & UPDATE WORKFLOW")
    print("=" * 60)
    print("This will run the complete data processing pipeline:")
    print("1. Download data from CafeF")
    print("2. Calculate performance metrics")
    print("3. Generate investment signals")
    print("=" * 60)
    
    # Get scripts directory (current directory)
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define scripts to run in sequence
    scripts = [
        (os.path.join(scripts_dir, 'cafef_crawl_data_and_save_portfolios_to_root_folder.py'), 
         "1. Data Download (CafeF)"),
        (os.path.join(scripts_dir, 'wf_calculate_from_history.py'), 
         "2. Calculate Metrics"),
        (os.path.join(scripts_dir, 'generate_investment_signals.py'), 
         "3. Generate Investment Signals")
    ]
    
    # Track results
    results = []
    start_time = datetime.now()
    
    # Run each script in sequence
    for script_path, script_name in scripts:
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script_path}")
            results.append((script_name, False))
            continue
        
        success = run_script(script_path, script_name)
        results.append((script_name, success))
        
        # Stop if any script fails
        if not success:
            print(f"\n❌ Workflow stopped due to failure in: {script_name}")
            break
    
    # Print final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("📊 WORKFLOW SUMMARY")
    print(f"{'='*60}")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Ended: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print("\nResults:")
    
    all_success = True
    for script_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {status}: {script_name}")
        if not success:
            all_success = False
    
    if all_success:
        print("\n🎉 ALL WORKFLOWS COMPLETED SUCCESSFULLY!")
        print("📁 Check the 'data' folder for results:")
        print("   - history_data_all_symbols.csv")
        print("   - perf_all_symbols.csv") 
        print("   - investment_signals_complete.csv")
    else:
        print("\n⚠️  WORKFLOW COMPLETED WITH ERRORS")
        print("Please check the error messages above and fix issues before retrying.")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)