"""
Portfolio Manager V2 - Improved architecture with proper data sources
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, List
from pathlib import Path

try:
    from src.portfolio_sources import get_all_portfolios, get_market_portfolios, get_user_portfolios
    from src.constants import PORTFOLIOS
except ImportError:
    from portfolio_sources import get_all_portfolios, get_market_portfolios, get_user_portfolios
    from constants import PORTFOLIOS

class PortfolioManagerV2:
    """Advanced portfolio management with proper data sources"""
    
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_portfolios_cached() -> Dict[str, List[str]]:
        """Get all portfolios with caching"""
        return get_all_portfolios()
    
    @staticmethod
    def display_portfolio_controls():
        """Display portfolio controls in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Portfolio Manager V2")
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Portfolios", help="Refresh from all sources"):
            st.cache_data.clear()
            st.rerun()
        
        # Show sources button
        if st.sidebar.button("📋 View Sources", help="View portfolio sources"):
            st.session_state['show_portfolio_sources'] = True
    
    @staticmethod
    def display_portfolio_sources():
        """Display detailed portfolio source information"""
        if st.session_state.get('show_portfolio_sources', False):
            with st.expander("📊 Portfolio Sources", expanded=True):
                
                # Market Portfolios
                st.subheader("🏛️ Market Portfolios (TradingView)")
                try:
                    market_portfolios = get_market_portfolios()
                    for name, symbols in market_portfolios.items():
                        st.write(f"**{name}**: {len(symbols)} symbols")
                        st.caption(f"Source: TradingView HOSE-{name}")
                except Exception as e:
                    st.error(f"Failed to load market portfolios: {e}")
                
                # User Portfolios
                st.subheader("👤 User Portfolios (Google Sheets)")
                try:
                    user_portfolios = get_user_portfolios()
                    if user_portfolios:
                        for name, symbols in user_portfolios.items():
                            st.write(f"**{name}**: {len(symbols)} symbols")
                            if len(symbols) <= 10:
                                st.caption(", ".join(symbols))
                            else:
                                st.caption(f"{', '.join(symbols[:10])}... (+{len(symbols)-10} more)")
                    else:
                        st.warning("No user portfolios found in Google Sheets")
                except Exception as e:
                    st.error(f"Failed to load user portfolios: {e}")
                
                # Google Sheets Format Guide
                st.subheader("📝 Google Sheets Format")
                st.code("""
Portfolio_Name | Symbol1 | Symbol2 | Symbol3 | ...
LongTerm      | ACB     | FPT     | HPG     | MBB
MidTerm       | BVB     | TCB     |         |
                """)
                st.caption("Simple format: Portfolio name in first column, symbols in remaining columns")
                
                if st.button("❌ Close"):
                    st.session_state['show_portfolio_sources'] = False
                    st.rerun()
    
    @staticmethod
    def create_portfolio_summary() -> str:
        """Create portfolio summary with source breakdown"""
        portfolios = PortfolioManagerV2.get_portfolios_cached()
        
        # Count by source
        market_count = 2  # VN30, VN100
        user_count = len(portfolios) - market_count - 1  # Exclude BizUni
        total_symbols = sum(len(symbols) for symbols in portfolios.values())
        
        return f"""
        <div style="
            background: linear-gradient(90deg, #e8f4fd 0%, #ffffff 100%);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #1f77b4;
            margin: 10px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>📊 {len(portfolios)} Active Portfolios</strong>
                    <br>
                    <small>
                        🏛️ {market_count} Market • 👤 {user_count} User • 💼 1 BizUni
                        <br>
                        📈 {total_symbols} total symbols
                    </small>
                </div>
                <div style="text-align: right; font-size: 12px; color: #666;">
                    Updated: {datetime.now().strftime('%H:%M')}
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def get_portfolios_with_ui() -> Dict[str, List[str]]:
        """Get portfolios with UI controls"""
        # Display controls
        PortfolioManagerV2.display_portfolio_controls()
        PortfolioManagerV2.display_portfolio_sources()
        
        # Return cached portfolios
        return PortfolioManagerV2.get_portfolios_cached()

# Simple Google Sheets editor interface
class GoogleSheetsEditor:
    """Simple interface for editing user portfolios"""
    
    @staticmethod
    def display_editor():
        """Display Google Sheets editor interface"""
        st.subheader("✏️ Portfolio Editor")
        
        # Load current user portfolios
        try:
            user_portfolios = get_user_portfolios()
        except:
            user_portfolios = {}
        
        # Edit interface
        with st.form("portfolio_editor"):
            st.write("**Current User Portfolios:**")
            
            # Display current portfolios
            for name, symbols in user_portfolios.items():
                st.write(f"• **{name}**: {', '.join(symbols[1:])}")  # Skip VNINDEX
            
            st.markdown("---")
            st.write("**Add/Edit Portfolio:**")
            
            portfolio_name = st.text_input("Portfolio Name", placeholder="e.g., MyPortfolio")
            symbols_input = st.text_area(
                "Symbols (comma-separated)", 
                placeholder="ACB, FPT, HPG, MBB",
                help="Enter stock symbols separated by commas"
            )
            
            if st.form_submit_button("💾 Save to Google Sheets"):
                if portfolio_name and symbols_input:
                    symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
                    st.success(f"Portfolio '{portfolio_name}' with {len(symbols)} symbols ready to save")
                    st.info("📝 Please manually update your Google Sheets with this data")
                    
                    # Show the format for Google Sheets
                    st.code(f"{portfolio_name},{','.join(symbols)}")
                else:
                    st.error("Please enter both portfolio name and symbols")