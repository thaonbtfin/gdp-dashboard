#!/usr/bin/env python3
"""
Test script for Investment Analysis Tab
"""

import streamlit as st
import pandas as pd
import os
import sys

# Add project root to path
sys.path.append('.')

from src.tastock.ui.dashboard import TAstock_st

def main():
    st.title("🧪 Test Investment Analysis Tab")
    
    # Test data loading
    st.header("📊 Data Loading Test")
    
    # Try different path approaches
    paths_to_try = [
        'data/investment_signals_complete.csv',
        './data/investment_signals_complete.csv',
        '/workspaces/gdp-dashboard/data/investment_signals_complete.csv'
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            st.success(f"✅ Found file at: {path}")
            try:
                df = pd.read_csv(path)
                st.info(f"📊 Loaded {len(df)} records")
                
                # Test the investment analysis tab
                st.header("🔬 Investment Analysis Tab Test")
                TAstock_st.investment_analysis_tab(pd.DataFrame())  # Pass empty df to trigger data loading
                break
            except Exception as e:
                st.error(f"❌ Error loading {path}: {e}")
        else:
            st.warning(f"❌ File not found: {path}")

if __name__ == "__main__":
    main()