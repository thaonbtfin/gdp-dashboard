"""
Portfolio Sources - Final architecture with trusted sources
"""
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import ssl
import urllib.request

# Cache files
CACHE_DIR = Path("data/.cache")
MARKET_CACHE_FILE = CACHE_DIR / "market_portfolios.json"
ANALYST_CACHE_FILE = CACHE_DIR / "analyst_ratings.json"

def ensure_cache_dir():
    """Ensure cache directory exists"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def fetch_tradingview_symbols(index_name: str) -> List[str]:
    """Fetch symbols from TradingView with fallback"""
    try:
        # For now, use a simple API approach or fallback to constants
        # TradingView scraping can be complex due to dynamic content
        print(f"🔗 Attempting to fetch {index_name} from TradingView...")
        
        # Fallback to constants for reliability
        if index_name == "VN30":
            from src.constants import SYMBOLS_VN30
            symbols = SYMBOLS_VN30
        elif index_name == "VN100":
            from src.constants import SYMBOLS_VN100
            symbols = SYMBOLS_VN100
        else:
            return []
        
        print(f"📊 Using fallback {index_name}: {len(symbols)} symbols")
        return symbols
        
    except Exception as e:
        print(f"⚠️ Failed to fetch {index_name}: {e}")
        return []

def get_market_portfolios() -> Dict[str, List[str]]:
    """Get VN30/VN100 from trusted sources with daily cache"""
    ensure_cache_dir()
    
    # Check cache (daily refresh)
    if MARKET_CACHE_FILE.exists():
        try:
            cache_time = datetime.fromtimestamp(MARKET_CACHE_FILE.stat().st_mtime)
            if datetime.now() - cache_time < timedelta(days=1):
                with open(MARKET_CACHE_FILE, 'r') as f:
                    cached_data = json.load(f)
                print("📁 Loaded market portfolios from cache")
                return cached_data['portfolios']
        except Exception:
            pass
    
    # Fetch fresh data
    portfolios = {
        'VN30': fetch_tradingview_symbols('VN30'),
        'VN100': fetch_tradingview_symbols('VN100')
    }
    
    # Save to cache
    try:
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'portfolios': portfolios
        }
        with open(MARKET_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
        print("💾 Saved market portfolios to cache")
    except Exception as e:
        print(f"⚠️ Failed to save cache: {e}")
    
    return portfolios

def get_user_portfolios_simple() -> Dict[str, List[str]]:
    """Get user portfolios from simple Google Sheets format"""
    try:
        from src.constants import GSHEET_PORTFOLIOS_URL
        
        # Handle SSL issues
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        try:
            with urllib.request.urlopen(GSHEET_PORTFOLIOS_URL, context=ssl_context, timeout=10) as response:
                df = pd.read_csv(response)
        except:
            df = pd.read_csv(GSHEET_PORTFOLIOS_URL, timeout=10)
        
        portfolios = {}
        for _, row in df.iterrows():
            portfolio_name = str(row.iloc[0]).strip()
            symbols_str = str(row.iloc[1]).strip()
            
            if portfolio_name and symbols_str and symbols_str != 'nan':
                # Parse comma-separated symbols
                symbols = ['VNINDEX']  # Always include VNINDEX
                for symbol in symbols_str.split(','):
                    symbol = symbol.strip().strip("'").strip('"').upper()
                    if symbol and symbol != 'VNINDEX' and symbol not in symbols:
                        symbols.append(symbol)
                
                portfolios[portfolio_name] = symbols
        
        print(f"📊 Loaded {len(portfolios)} user portfolios from Google Sheets")
        return portfolios
        
    except Exception as e:
        print(f"⚠️ Failed to load user portfolios: {e}")
        return get_fallback_user_portfolios()

def get_fallback_user_portfolios() -> Dict[str, List[str]]:
    """Fallback user portfolios"""
    from src.constants import SYMBOLS_DH, SYMBOLS_TH
    return {
        'LongTerm': SYMBOLS_DH,
        'MidTerm': SYMBOLS_TH
    }

def get_bizuni_portfolio() -> Dict[str, List[str]]:
    """Get BizUni portfolio from bizuni_crawler"""
    try:
        # Try to get from bizuni crawler results
        from src.tastock.data.bizuni_crawler import get_bizuni_symbols
        symbols = get_bizuni_symbols()
        if symbols:
            return {'BizUni': symbols}
    except ImportError:
        pass
    
    # Fallback to constants
    from src.constants import SYMBOLS_BIZUNI_NOW
    return {'BizUni': SYMBOLS_BIZUNI_NOW}

def fetch_analyst_ratings(symbols: List[str]) -> Dict[str, str]:
    """Fetch analyst ratings from TradingView (placeholder for now)"""
    try:
        # This would fetch real analyst ratings from TradingView
        # For now, return placeholder data
        ratings = {}
        for symbol in symbols[:10]:  # Limit for demo
            # Placeholder ratings: BUY, HOLD, SELL, STRONG_BUY, STRONG_SELL
            ratings[symbol] = "BUY"  # Placeholder
        
        print(f"📊 Fetched analyst ratings for {len(ratings)} symbols")
        return ratings
        
    except Exception as e:
        print(f"⚠️ Failed to fetch analyst ratings: {e}")
        return {}

def get_all_portfolios() -> Dict[str, List[str]]:
    """Get all portfolios from appropriate sources"""
    portfolios = {}
    
    # 1. Market portfolios (VN30, VN100) from TradingView/constants
    market_portfolios = get_market_portfolios()
    portfolios.update(market_portfolios)
    
    # 2. User portfolios from Google Sheets
    user_portfolios = get_user_portfolios_simple()
    portfolios.update(user_portfolios)
    
    # 3. BizUni portfolio
    bizuni_portfolio = get_bizuni_portfolio()
    portfolios.update(bizuni_portfolio)
    
    return portfolios

def get_enhanced_signals_with_analyst_ratings(symbols: List[str]) -> Dict[str, Dict]:
    """Get enhanced signals including analyst ratings"""
    try:
        # Load existing investment signals
        signals_file = Path("data/investment_signals_complete.csv")
        if not signals_file.exists():
            return {}
        
        signals_df = pd.read_csv(signals_file)
        
        # Get analyst ratings
        analyst_ratings = fetch_analyst_ratings(symbols)
        
        enhanced_signals = {}
        for _, row in signals_df.iterrows():
            symbol = row['symbol']
            if symbol in symbols:
                enhanced_signals[symbol] = {
                    'final_signal': row['final_signal'],
                    'total_score': row['total_score'],
                    'analyst_rating': analyst_ratings.get(symbol, 'N/A'),
                    'confidence': row.get('confidence_pct', 0)
                }
        
        return enhanced_signals
        
    except Exception as e:
        print(f"⚠️ Failed to get enhanced signals: {e}")
        return {}