#!/usr/bin/env python3
"""
Generate Intrinsic Values

Creates intrinsic value estimates for stocks based on performance data.
"""

import pandas as pd
import os
from datetime import datetime

def calculate_intrinsic_value(row):
    """Calculate simple intrinsic value based on performance metrics"""
    try:
        # Simple DCF-like calculation using available metrics
        annual_return = row.get('annualized_return_pct', 0)
        current_price = row.get('sma_20_current', 0)
        volatility = row.get('annual_std_dev_pct', 30)
        
        # Risk adjustment factor (lower volatility = higher multiplier)
        risk_factor = max(0.5, 1 - (volatility / 100))
        
        # Growth factor based on returns
        if annual_return > 20:
            growth_factor = 1.2
        elif annual_return > 10:
            growth_factor = 1.1
        elif annual_return > 0:
            growth_factor = 1.0
        else:
            growth_factor = 0.9
        
        # Simple intrinsic value calculation
        intrinsic_value = current_price * risk_factor * growth_factor
        
        return round(intrinsic_value, 2)
    
    except Exception:
        return 0.0

def main():
    """Generate intrinsic values from performance data"""
    
    # Get script directory and project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '../../..')
    
    # Read performance data
    perf_file = os.path.join(project_root, 'data/perf_all_symbols.csv')
    
    if not os.path.exists(perf_file):
        print(f"❌ Performance file not found: {perf_file}")
        print("Please run calculate_from_history.py first")
        return
    
    df = pd.read_csv(perf_file)
    print(f"📊 Loaded {len(df)} symbols from performance data")
    
    # Calculate intrinsic values
    intrinsic_data = []
    
    for idx, row in df.iterrows():
        symbol = row['symbol']
        intrinsic_value = calculate_intrinsic_value(row)
        
        intrinsic_data.append({
            'symbol': symbol,
            'intrinsic_value': intrinsic_value,
            'current_price': row.get('sma_20_current', 0),
            'calculation_date': datetime.now().strftime('%Y-%m-%d')
        })
    
    # Create DataFrame and save
    intrinsic_df = pd.DataFrame(intrinsic_data)
    
    # Save to data directory
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    output_file = os.path.join(data_dir, 'intrinsic_value_all_symbols.csv')
    
    intrinsic_df.to_csv(output_file, index=False)
    
    print(f"✅ Generated intrinsic values for {len(intrinsic_df)} symbols")
    print(f"💾 Saved to: {output_file}")
    
    # Show summary
    avg_intrinsic = intrinsic_df['intrinsic_value'].mean()
    print(f"📈 Average intrinsic value: {avg_intrinsic:.2f}")

if __name__ == "__main__":
    main()