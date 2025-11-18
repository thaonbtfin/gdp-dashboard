"""
Analyst Ratings Integration - Add TradingView analyst data to signals
"""
import pandas as pd
import requests
from typing import Dict, List
from pathlib import Path

def get_analyst_ratings_mock(symbols: List[str]) -> Dict[str, Dict]:
    """
    Mock analyst ratings - replace with real TradingView API
    """
    ratings_map = {
        'STRONG_BUY': 5, 'BUY': 4, 'HOLD': 3, 'SELL': 2, 'STRONG_SELL': 1
    }
    
    # Mock data - in production, fetch from TradingView
    mock_ratings = {}
    for symbol in symbols[:20]:  # Limit for demo
        if symbol == 'VNINDEX':
            continue
            
        # Simulate analyst ratings
        import random
        rating_text = random.choice(['STRONG_BUY', 'BUY', 'HOLD', 'SELL'])
        rating_score = ratings_map[rating_text]
        
        mock_ratings[symbol] = {
            'rating': rating_text,
            'score': rating_score,
            'analyst_count': random.randint(3, 15),
            'price_target': random.uniform(15000, 50000)
        }
    
    return mock_ratings

def enhance_investment_signals_with_analyst_ratings():
    """
    Enhance existing investment signals with analyst ratings
    """
    try:
        # Load existing signals
        signals_file = Path("data/investment_signals_complete.csv")
        if not signals_file.exists():
            print("❌ Investment signals file not found")
            return False
        
        signals_df = pd.read_csv(signals_file)
        
        # Get all symbols
        symbols = signals_df['symbol'].tolist()
        
        # Get analyst ratings
        analyst_ratings = get_analyst_ratings_mock(symbols)
        
        # Add analyst data to signals
        signals_df['analyst_rating'] = signals_df['symbol'].map(
            lambda x: analyst_ratings.get(x, {}).get('rating', 'N/A')
        )
        signals_df['analyst_score'] = signals_df['symbol'].map(
            lambda x: analyst_ratings.get(x, {}).get('score', 0)
        )
        signals_df['analyst_count'] = signals_df['symbol'].map(
            lambda x: analyst_ratings.get(x, {}).get('analyst_count', 0)
        )
        
        # Calculate enhanced final signal (combine our signal + analyst rating)
        def calculate_enhanced_signal(row):
            our_score = row['total_score']
            analyst_score = row['analyst_score']
            
            if analyst_score == 0:  # No analyst data
                return row['final_signal']
            
            # Weight: 70% our analysis, 30% analyst rating
            # Convert analyst score (1-5) to our scale (-2 to +2)
            analyst_weighted = (analyst_score - 3) * 0.67  # Scale to -1.33 to +1.33
            enhanced_score = our_score * 0.7 + analyst_weighted * 0.3
            
            if enhanced_score >= 1.5:
                return 'BUY'
            elif enhanced_score <= -1.5:
                return 'SELL'
            else:
                return 'HOLD'
        
        signals_df['enhanced_signal'] = signals_df.apply(calculate_enhanced_signal, axis=1)
        
        # Calculate enhanced confidence
        def calculate_enhanced_confidence(row):
            base_confidence = row.get('confidence_pct', 50)
            analyst_score = row['analyst_score']
            
            if analyst_score == 0:
                return base_confidence
            
            # Boost confidence if analyst agrees with our signal
            our_signal = row['final_signal']
            analyst_signal = 'BUY' if analyst_score >= 4 else 'SELL' if analyst_score <= 2 else 'HOLD'
            
            if our_signal == analyst_signal:
                return min(95, base_confidence + 15)  # Boost confidence
            else:
                return max(25, base_confidence - 10)  # Reduce confidence
        
        signals_df['enhanced_confidence'] = signals_df.apply(calculate_enhanced_confidence, axis=1)
        
        # Save enhanced signals
        enhanced_file = Path("data/investment_signals_enhanced.csv")
        signals_df.to_csv(enhanced_file, index=False)
        
        print(f"✅ Enhanced {len(signals_df)} signals with analyst ratings")
        print(f"💾 Saved to {enhanced_file}")
        
        # Show summary
        enhanced_counts = signals_df['enhanced_signal'].value_counts()
        print(f"\n📊 Enhanced Signal Distribution:")
        for signal, count in enhanced_counts.items():
            print(f"  {signal}: {count} stocks")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to enhance signals: {e}")
        return False

if __name__ == "__main__":
    enhance_investment_signals_with_analyst_ratings()