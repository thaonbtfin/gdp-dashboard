#!/usr/bin/env python3
"""
Git Data Committer
Commits and pushes CSV data files to main branch after successful workflow execution
"""
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

def run_git_command(command, cwd=None):
    """Execute git command and return result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def commit_and_push_data():
    """Commit and push CSV data files to main branch"""
    
    # Get project root directory
    project_root = Path(__file__).parent.parent.parent.parent
    data_dir = project_root / "data"
    
    # List of CSV files to commit
    csv_files = [
        "bizuni_cpgt.csv",
        "history_data_all_symbols.csv", 
        "history_data.csv",
        "intrinsic_value_all_symbols.csv",
        "investment_signals_complete.csv",
        "investment_signals_enhanced.csv",
        "perf_all_symbols.csv"
    ]
    
    # Check if files exist
    existing_files = []
    for file in csv_files:
        file_path = data_dir / file
        if file_path.exists():
            existing_files.append(f"data/{file}")
    
    if not existing_files:
        print("❌ No CSV files found to commit")
        return False
    
    print(f"📁 Found {len(existing_files)} CSV files to commit")
    
    # Change to project root
    os.chdir(project_root)
    
    # Add files to git
    for file in existing_files:
        success, output = run_git_command(f"git add {file}")
        if not success:
            print(f"❌ Failed to add {file}: {output}")
            return False
        print(f"✅ Added {file}")
    
    # Create commit message with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Update stock data files - {timestamp}"
    
    # Commit changes
    success, output = run_git_command(f'git commit -m "{commit_message}"')
    if not success:
        if "nothing to commit" in output:
            print("ℹ️ No changes to commit")
            return True
        else:
            print(f"❌ Failed to commit: {output}")
            return False
    
    print(f"✅ Committed changes: {commit_message}")
    
    # Push to main branch
    success, output = run_git_command("git push origin main")
    if not success:
        print(f"❌ Failed to push: {output}")
        return False
    
    print("✅ Successfully pushed to main branch")
    return True

def main():
    """Main function"""
    print("🚀 Starting Git data commit process...")
    
    if commit_and_push_data():
        print("✅ Git commit and push completed successfully!")
        return 0
    else:
        print("❌ Git commit and push failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())