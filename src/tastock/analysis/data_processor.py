"""
Data processor to enhance CafeF crawler data with missing metrics
"""
import asyncio
from typing import Dict, List
import pandas as pd

class DataProcessor:
    
    def __init__(self, cafef_crawler):
        self.crawler = cafef_crawler
    
    async def get_vnindex_data(self) -> List[Dict]:
        """Get VN-Index data for market direction analysis"""
        try:
            vnindex_data = await self.crawler.get_stock_data('VNINDEX')
            return vnindex_data.get('price_data', [])
        except Exception as e:
            print(f"Error getting VN-Index data: {e}")
            return []
    
    async def enhance_stock_data(self, symbol: str) -> Dict:
        """Get and enhance stock data with all required metrics"""
        # Get basic stock data
        stock_data = await self.crawler.get_stock_data(symbol)
        
        # Get VN-Index for market direction
        vnindex_data = await self.get_vnindex_data()
        
        # Calculate Relative Strength Rating
        if stock_data.get('price_data') and vnindex_data:
            rs_rating = self._calculate_relative_strength(
                stock_data['price_data'], 
                vnindex_data
            )
            stock_data['relative_strength_rating'] = rs_rating
        
        # Extract institutional ownership from financial data
        institutional_ownership = await self._get_institutional_ownership(symbol)
        stock_data['institutional_ownership'] = institutional_ownership
        
        # Add market direction data
        stock_data['market_data'] = {
            'vnindex_data': vnindex_data[-200:] if len(vnindex_data) >= 200 else vnindex_data
        }
        
        return stock_data
    
    def _calculate_relative_strength(self, stock_prices: List[Dict], vnindex_prices: List[Dict]) -> float:
        """Calculate Relative Strength Rating (1-99)"""
        if len(stock_prices) < 252 or len(vnindex_prices) < 252:
            return 50.0
        
        # Get 12-month data
        stock_12m = stock_prices[-252:]
        vnindex_12m = vnindex_prices[-252:]
        
        # Calculate returns
        stock_return = (stock_12m[-1]['close'] - stock_12m[0]['close']) / stock_12m[0]['close']
        market_return = (vnindex_12m[-1]['close'] - vnindex_12m[0]['close']) / vnindex_12m[0]['close']
        
        if market_return == 0:
            return 50.0
        
        # Calculate relative performance
        relative_performance = stock_return / market_return
        
        # Convert to 1-99 scale
        rs_rating = min(99, max(1, relative_performance * 50 + 50))
        
        return round(rs_rating, 1)
    
    async def _get_institutional_ownership(self, symbol: str) -> Dict:
        """Get institutional ownership data from CafeF"""
        try:
            # Navigate to shareholder page
            exchange = await self.crawler._get_exchange(symbol)
            url = f"{self.crawler.base_url}/{exchange.lower()}/{symbol.lower()}-cong-ty-co-phan-{symbol.lower()}.chn"
            
            await self.crawler.page.goto(url)
            await self.crawler.page.wait_for_load_state('networkidle')
            
            # Look for shareholder/ownership section
            ownership_data = {
                'institutional_percentage': 0.0,
                'fund_ownership': 0.0,
                'foreign_ownership': 0.0,
                'details': []
            }
            
            # Try to find ownership table
            ownership_selectors = [
                'text=Cổ đông lớn',
                'text=Cấu trúc sở hữu', 
                'text=Sở hữu',
                '.ownership-table',
                '.shareholder-table'
            ]
            
            for selector in ownership_selectors:
                try:
                    element = await self.crawler.page.query_selector(selector)
                    if element:
                        # Click to expand if needed
                        await element.click()
                        await self.crawler.page.wait_for_timeout(1000)
                        
                        # Extract ownership data
                        table = await self.crawler.page.query_selector('table')
                        if table:
                            rows = await table.query_selector_all('tr')
                            for row in rows[1:]:  # Skip header
                                cells = await row.query_selector_all('td')
                                if len(cells) >= 3:
                                    name = await cells[0].inner_text()
                                    percentage_text = await cells[2].inner_text()
                                    
                                    # Parse percentage
                                    percentage = self._parse_percentage(percentage_text)
                                    
                                    # Categorize ownership
                                    if any(keyword in name.lower() for keyword in ['quỹ', 'fund', 'đầu tư']):
                                        ownership_data['fund_ownership'] += percentage
                                    elif any(keyword in name.lower() for keyword in ['nước ngoài', 'foreign']):
                                        ownership_data['foreign_ownership'] += percentage
                                    
                                    ownership_data['details'].append({
                                        'name': name,
                                        'percentage': percentage
                                    })
                        break
                except:
                    continue
            
            # Calculate total institutional ownership
            ownership_data['institutional_percentage'] = (
                ownership_data['fund_ownership'] + 
                ownership_data['foreign_ownership']
            )
            
            return ownership_data
            
        except Exception as e:
            print(f"Error getting institutional ownership for {symbol}: {e}")
            return {
                'institutional_percentage': 0.0,
                'fund_ownership': 0.0,
                'foreign_ownership': 0.0,
                'details': []
            }
    
    def _parse_percentage(self, text: str) -> float:
        """Parse percentage from text"""
        import re
        match = re.search(r'(\d+\.?\d*)%?', text.replace(',', '.'))
        if match:
            return float(match.group(1))
        return 0.0
    
    async def process_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict]:
        """Process multiple stocks and return enhanced data"""
        results = {}
        
        for symbol in symbols:
            try:
                print(f"Processing {symbol}...")
                enhanced_data = await self.enhance_stock_data(symbol)
                results[symbol] = enhanced_data
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                results[symbol] = {'error': str(e)}
        
        return results
    
    def export_to_csv(self, processed_data: Dict[str, Dict], filename: str):
        """Export processed data to CSV for analysis"""
        rows = []
        
        for symbol, data in processed_data.items():
            if 'error' in data:
                continue
                
            basic_info = data.get('basic_info', {})
            value_metrics = data.get('value_metrics', {})
            growth_metrics = data.get('growth_metrics', {})
            technical = data.get('technical_indicators', {})
            
            row = {
                'symbol': symbol,
                'current_price': basic_info.get('current_price', 0),
                'pe_ratio': basic_info.get('pe_ratio', 0),
                'pb_ratio': basic_info.get('pb_ratio', 0),
                'market_cap': basic_info.get('market_cap', 0),
                'roe': value_metrics.get('roe', 0),
                'debt_to_equity': value_metrics.get('debt_to_equity', 0),
                'free_cash_flow': value_metrics.get('free_cash_flow', 0),
                'eps_growth': growth_metrics.get('eps_growth_quarterly', 0),
                'revenue_growth': growth_metrics.get('revenue_growth', 0),
                'relative_strength': data.get('relative_strength_rating', 50),
                'institutional_ownership': data.get('institutional_ownership', {}).get('institutional_percentage', 0),
                'macd_signal': technical.get('macd', {}).get('histogram', 0),
                'volume_ratio': technical.get('volume_ratio', 1)
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")
        
        return df