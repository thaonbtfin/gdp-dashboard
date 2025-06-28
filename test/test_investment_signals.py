"""
Test script for investment signal calculation
"""
import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tastock.crawlers.cafef_crawler import CafeFCrawler
from tastock.analysis.data_processor import DataProcessor
from tastock.analysis.investment_signals import InvestmentSignalCalculator

async def test_investment_signals():
    """Test the complete investment signal system"""
    
    # Test symbols
    test_symbols = ['FPT', 'VCB', 'HPG']
    
    async with CafeFCrawler() as crawler:
        # Initialize processor and signal calculator
        processor = DataProcessor(crawler)
        
        # Get VN-Index data for market direction
        print("Getting VN-Index data...")
        vnindex_data = await processor.get_vnindex_data()
        
        signal_calculator = InvestmentSignalCalculator(vnindex_data)
        
        # Test market direction
        market_direction = signal_calculator.calculate_market_direction()
        print(f"\n=== MARKET DIRECTION ===")
        print(f"Direction: {market_direction['direction']}")
        print(f"Strength: {market_direction['strength']}%")
        print(f"VN-Index: {market_direction['current_price']}")
        print(f"MA50: {market_direction['ma50']}")
        print(f"MA200: {market_direction['ma200']}")
        
        # Process each stock
        for symbol in test_symbols:
            print(f"\n{'='*50}")
            print(f"ANALYZING {symbol}")
            print(f"{'='*50}")
            
            try:
                # Get enhanced stock data
                enhanced_data = await processor.enhance_stock_data(symbol)
                
                # Calculate Relative Strength
                rs_rating = enhanced_data.get('relative_strength_rating', 50)
                print(f"Relative Strength Rating: {rs_rating}/99")
                
                # Get institutional ownership
                institutional = enhanced_data.get('institutional_ownership', {})
                print(f"Institutional Ownership: {institutional.get('institutional_percentage', 0):.1f}%")
                
                # Generate investment signals
                combined_signals = signal_calculator.generate_combined_signals(enhanced_data)
                
                print(f"\n--- FINAL RECOMMENDATION ---")
                print(f"Signal: {combined_signals['final_signal']}")
                print(f"Total Score: {combined_signals['total_score']}")
                
                print(f"\n--- INDIVIDUAL SIGNALS ---")
                for method, signals in combined_signals['individual_signals'].items():
                    print(f"{method.upper()}: {signals['signal']} (Score: {signals['score']})")
                    for reason in signals['reasons']:
                        print(f"  • {reason}")
                
                print(f"\n--- KEY METRICS ---")
                basic_info = enhanced_data.get('basic_info', {})
                value_metrics = enhanced_data.get('value_metrics', {})
                growth_metrics = enhanced_data.get('growth_metrics', {})
                
                print(f"Current Price: {basic_info.get('current_price', 0):,.0f}")
                print(f"P/E: {basic_info.get('pe_ratio', 0):.1f}")
                print(f"P/B: {basic_info.get('pb_ratio', 0):.1f}")
                print(f"ROE: {value_metrics.get('roe', 0):.1f}%")
                print(f"Debt/Equity: {value_metrics.get('debt_to_equity', 0):.2f}")
                print(f"EPS Growth: {growth_metrics.get('eps_growth_quarterly', 0):.1f}%")
                print(f"Revenue Growth: {growth_metrics.get('revenue_growth', 0):.1f}%")
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
        
        # Export summary data
        print(f"\n{'='*50}")
        print("EXPORTING DATA...")
        print(f"{'='*50}")
        
        all_data = await processor.process_multiple_stocks(test_symbols)
        df = processor.export_to_csv(all_data, 'investment_analysis_results.csv')
        
        print(f"\nSummary exported to investment_analysis_results.csv")
        print(f"Processed {len(df)} stocks successfully")

if __name__ == "__main__":
    asyncio.run(test_investment_signals())