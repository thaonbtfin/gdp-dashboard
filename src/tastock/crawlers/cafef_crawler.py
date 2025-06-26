"""
CafeF Crawler for fetching financial data from cafef.vn
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
from typing import Dict, List, Optional
import re
from datetime import datetime

class CafeFCrawler:
    def __init__(self):
        self.base_url = "https://cafef.vn/du-lieu"
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def get_stock_data(self, symbol: str) -> Dict:
        """Get comprehensive stock data from CafeF for investment analysis"""
        symbol = symbol.upper()
        
        # Determine exchange
        exchange = await self._get_exchange(symbol)
        url = f"{self.base_url}/{exchange.lower()}/{symbol.lower()}-cong-ty-co-phan-{symbol.lower()}.chn"
        
        await self.page.goto(url)
        await self.page.wait_for_load_state('networkidle')
        
        data = {
            'symbol': symbol,
            'exchange': exchange,
            'basic_info': await self._get_basic_info(),
            'financial_ratios': await self._get_financial_ratios(),
            'price_data': await self._get_price_data(),
            'financial_statements': await self._get_financial_statements(),
            # For Value Investing
            'value_metrics': await self._get_value_metrics(),
            # For CANSLIM
            'growth_metrics': await self._get_growth_metrics(),
            # For Technical Analysis
            'technical_indicators': await self._calculate_technical_indicators()
        }
        
        return data
    
    async def _get_exchange(self, symbol: str) -> str:
        """Determine exchange (HOSE/HNX/UPCOM) for symbol"""
        # Try HOSE first (most common)
        exchanges = ['hose', 'hnx', 'upcom']
        
        for exchange in exchanges:
            try:
                url = f"{self.base_url}/{exchange}/{symbol.lower()}-cong-ty-co-phan-{symbol.lower()}.chn"
                response = await self.page.goto(url)
                if response.status == 200:
                    return exchange.upper()
            except:
                continue
        
        return 'HOSE'  # Default
    
    async def _get_basic_info(self) -> Dict:
        """Get basic stock information"""
        try:
            # Current price
            price_element = await self.page.query_selector('.price')
            current_price = await price_element.inner_text() if price_element else "0"
            current_price = float(re.sub(r'[^\d.]', '', current_price))
            
            # Market cap, volume, etc.
            info = {
                'current_price': current_price,
                'market_cap': await self._extract_value('.market-cap'),
                'volume': await self._extract_value('.volume'),
                'pe_ratio': await self._extract_value('.pe'),
                'pb_ratio': await self._extract_value('.pb')
            }
            
            return info
        except Exception as e:
            print(f"Error getting basic info: {e}")
            return {}
    
    async def _get_financial_ratios(self) -> Dict:
        """Get financial ratios from the ratios table"""
        try:
            ratios = {}
            
            # Navigate to financial ratios section
            ratios_tab = await self.page.query_selector('a[href*="chi-so"]')
            if ratios_tab:
                await ratios_tab.click()
                await self.page.wait_for_timeout(2000)
            
            # Extract ratios table
            table = await self.page.query_selector('.financial-ratios-table')
            if table:
                rows = await table.query_selector_all('tr')
                for row in rows:
                    cells = await row.query_selector_all('td')
                    if len(cells) >= 2:
                        key = await cells[0].inner_text()
                        value = await cells[1].inner_text()
                        ratios[key.strip()] = self._parse_number(value)
            
            return ratios
        except Exception as e:
            print(f"Error getting financial ratios: {e}")
            return {}
    
    async def _get_price_data(self) -> List[Dict]:
        """Get historical price data"""
        try:
            price_data = []
            
            # Navigate to price history
            history_tab = await self.page.query_selector('a[href*="lich-su"]')
            if history_tab:
                await history_tab.click()
                await self.page.wait_for_timeout(2000)
            
            # Extract price table
            table = await self.page.query_selector('.price-history-table')
            if table:
                rows = await table.query_selector_all('tr')[1:]  # Skip header
                for row in rows[:50]:  # Get last 50 days
                    cells = await row.query_selector_all('td')
                    if len(cells) >= 6:
                        price_data.append({
                            'date': await cells[0].inner_text(),
                            'open': self._parse_number(await cells[1].inner_text()),
                            'high': self._parse_number(await cells[2].inner_text()),
                            'low': self._parse_number(await cells[3].inner_text()),
                            'close': self._parse_number(await cells[4].inner_text()),
                            'volume': self._parse_number(await cells[5].inner_text())
                        })
            
            return price_data
        except Exception as e:
            print(f"Error getting price data: {e}")
            return []
    
    async def _get_financial_statements(self) -> Dict:
        """Get financial statements data"""
        try:
            statements = {}
            
            # Navigate to financial statements
            finance_tab = await self.page.query_selector('a[href*="tai-chinh"]')
            if finance_tab:
                await finance_tab.click()
                await self.page.wait_for_timeout(2000)
            
            # Get Income Statement
            statements['income_statement'] = await self._extract_financial_table('.income-statement')
            
            # Get Balance Sheet
            statements['balance_sheet'] = await self._extract_financial_table('.balance-sheet')
            
            # Get Cash Flow
            statements['cash_flow'] = await self._extract_financial_table('.cash-flow')
            
            return statements
        except Exception as e:
            print(f"Error getting financial statements: {e}")
            return {}
    
    async def _extract_financial_table(self, selector: str) -> List[Dict]:
        """Extract data from financial table"""
        try:
            data = []
            table = await self.page.query_selector(selector)
            if table:
                rows = await table.query_selector_all('tr')
                headers = []
                
                # Get headers
                if rows:
                    header_cells = await rows[0].query_selector_all('th')
                    headers = [await cell.inner_text() for cell in header_cells]
                
                # Get data rows
                for row in rows[1:]:
                    cells = await row.query_selector_all('td')
                    if len(cells) == len(headers):
                        row_data = {}
                        for i, cell in enumerate(cells):
                            value = await cell.inner_text()
                            row_data[headers[i]] = self._parse_number(value) if i > 0 else value
                        data.append(row_data)
            
            return data
        except Exception as e:
            print(f"Error extracting financial table: {e}")
            return []
    
    async def _extract_value(self, selector: str) -> float:
        """Extract numeric value from element"""
        try:
            element = await self.page.query_selector(selector)
            if element:
                text = await element.inner_text()
                return self._parse_number(text)
            return 0.0
        except:
            return 0.0
    
    def _parse_number(self, text: str) -> float:
        """Parse number from text, handling Vietnamese format"""
        if not text or text.strip() == '-':
            return 0.0
        
        # Remove non-numeric characters except dots and commas
        cleaned = re.sub(r'[^\d.,\-]', '', text.strip())
        
        # Handle Vietnamese number format (comma as thousand separator, dot as decimal)
        if ',' in cleaned and '.' in cleaned:
            # Format: 1,234.56
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Could be either thousand separator or decimal
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Decimal separator
                cleaned = cleaned.replace(',', '.')
            else:
                # Thousand separator
                cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except:
            return 0.0
    
    async def _get_value_metrics(self) -> Dict:
        """Get metrics for Value Investing analysis"""
        try:
            metrics = {}
            
            # Get ROE from financial ratios
            roe_element = await self.page.query_selector('text=ROE')
            if roe_element:
                parent = roe_element.locator('..')
                roe_value = await parent.locator('td').nth(1).inner_text()
                metrics['roe'] = self._parse_number(roe_value)
            
            # Get Debt/Equity from balance sheet
            debt_element = await self.page.query_selector('text=Nợ phải trả')
            equity_element = await self.page.query_selector('text=Vốn chủ sở hữu')
            
            if debt_element and equity_element:
                debt_parent = debt_element.locator('..')
                equity_parent = equity_element.locator('..')
                
                debt_value = await debt_parent.locator('td').nth(-1).inner_text()
                equity_value = await equity_parent.locator('td').nth(-1).inner_text()
                
                debt = self._parse_number(debt_value)
                equity = self._parse_number(equity_value)
                
                if equity > 0:
                    metrics['debt_to_equity'] = debt / equity
            
            # Get FCF from cash flow statement
            fcf_element = await self.page.query_selector('text=Dòng tiền tự do')
            if fcf_element:
                parent = fcf_element.locator('..')
                fcf_value = await parent.locator('td').nth(-1).inner_text()
                metrics['free_cash_flow'] = self._parse_number(fcf_value)
            
            return metrics
        except Exception as e:
            print(f"Error getting value metrics: {e}")
            return {}
    
    async def _get_growth_metrics(self) -> Dict:
        """Get metrics for CANSLIM analysis"""
        try:
            metrics = {}
            
            # Get quarterly EPS growth
            eps_elements = await self.page.query_selector_all('text=EPS')
            if eps_elements:
                # Extract EPS data for growth calculation
                eps_data = []
                for element in eps_elements[:4]:  # Last 4 quarters
                    parent = element.locator('..')
                    value = await parent.locator('td').nth(-1).inner_text()
                    eps_data.append(self._parse_number(value))
                
                if len(eps_data) >= 2:
                    current_eps = eps_data[0]
                    previous_eps = eps_data[1]
                    if previous_eps > 0:
                        metrics['eps_growth_quarterly'] = ((current_eps - previous_eps) / previous_eps) * 100
            
            # Get revenue growth
            revenue_elements = await self.page.query_selector_all('text=Doanh thu')
            if revenue_elements:
                revenue_data = []
                for element in revenue_elements[:4]:  # Last 4 quarters
                    parent = element.locator('..')
                    value = await parent.locator('td').nth(-1).inner_text()
                    revenue_data.append(self._parse_number(value))
                
                if len(revenue_data) >= 2:
                    current_revenue = revenue_data[0]
                    previous_revenue = revenue_data[1]
                    if previous_revenue > 0:
                        metrics['revenue_growth'] = ((current_revenue - previous_revenue) / previous_revenue) * 100
            
            return metrics
        except Exception as e:
            print(f"Error getting growth metrics: {e}")
            return {}
    
    async def _calculate_technical_indicators(self) -> Dict:
        """Calculate technical indicators from price data"""
        try:
            # Get price data first
            price_data = await self._get_price_data()
            if len(price_data) < 26:  # Need at least 26 days for MACD
                return {}
            
            closes = [item['close'] for item in price_data]
            volumes = [item['volume'] for item in price_data]
            
            indicators = {}
            
            # Calculate MACD
            if len(closes) >= 26:
                ema12 = self._calculate_ema(closes, 12)
                ema26 = self._calculate_ema(closes, 26)
                macd_line = [ema12[i] - ema26[i] for i in range(len(ema26))]
                signal_line = self._calculate_ema(macd_line, 9)
                
                indicators['macd'] = {
                    'macd_line': macd_line[-1] if macd_line else 0,
                    'signal_line': signal_line[-1] if signal_line else 0,
                    'histogram': (macd_line[-1] - signal_line[-1]) if macd_line and signal_line else 0
                }
            
            # Volume analysis
            if len(volumes) >= 20:
                avg_volume_20 = sum(volumes[-20:]) / 20
                current_volume = volumes[-1]
                indicators['volume_ratio'] = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
            
            return indicators
        except Exception as e:
            print(f"Error calculating technical indicators: {e}")
            return {}
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]  # First EMA is SMA
        
        for i in range(period, len(prices)):
            ema.append((prices[i] * multiplier) + (ema[-1] * (1 - multiplier)))
        
        return ema

# Usage example
async def crawl_stock_example():
    async with CafeFCrawler() as crawler:
        data = await crawler.get_stock_data('FPT')
        return data

if __name__ == "__main__":
    # Test the crawler
    data = asyncio.run(crawl_stock_example())
    print(f"Crawled data for FPT: {data}")