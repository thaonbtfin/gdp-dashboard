#!/usr/bin/env python3
"""
Send Investment Signal Notifications
Automatically sends notifications for high-confidence BUY/SELL signals
"""
import pandas as pd
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from src.tastock.notifications.notification_service import NotificationService
from src.tastock.notifications.config import NotificationConfig
from src.tastock.notifications.gdrive_config import get_gdrive_url

def main():
    """Send notifications for high-confidence investment signals"""
    
    # Load configuration from Google Drive
    config = NotificationConfig(gdrive_url=get_gdrive_url())
    service = NotificationService(config.config)
    
    # Load investment signals
    signals_file = project_root / "data" / "investment_signals_complete.csv"
    
    if not signals_file.exists():
        print("❌ No investment signals file found")
        return
    
    try:
        signals_df = pd.read_csv(signals_file)
        
        # Filter high-confidence signals
        threshold = config.get_threshold()
        high_confidence = signals_df[
            (signals_df['confidence_pct'] >= threshold) & 
            (signals_df['final_signal'].isin(['BUY', 'SELL']))
        ]
        
        if high_confidence.empty:
            print(f"ℹ️ No signals above {threshold}% confidence threshold")
            return
        
        # Send notifications
        sent_count = 0
        for _, row in high_confidence.iterrows():
            notification_data = {
                'stock_code': row['symbol'],
                'signal': row['final_signal'],
                'confidence': int(row['confidence_pct']),
                'price': row['current_price']
            }
            
            results = service.send_notification(notification_data)
            
            # Check if any channel succeeded
            if any(results.values()):
                sent_count += 1
                print(f"✅ Sent notification for {row['symbol']} ({row['final_signal']})")
            else:
                print(f"❌ Failed to send notification for {row['symbol']}")
        
        print(f"\n📊 Summary: {sent_count}/{len(high_confidence)} notifications sent")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())