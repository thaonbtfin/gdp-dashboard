import streamlit as st
import pandas as pd
import os

def color_final_signal(val):
    """Color code the final_signal column"""
    if val == 'BUY':
        return 'background-color: lightgreen'
    elif val == 'SELL':
        return 'background-color: lightcoral'
    else:
        return ''

def main():
    st.title("📊 Phân tích Tín hiệu Đầu tư")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Tổng quan", 
        "💰 Value Investing", 
        "🚀 CANSLIM", 
        "📊 Tổng hợp so sánh 3 trường phái"
    ])
    
    with tab4:
        with st.expander("📋 Bảng so sánh tín hiệu đầu tư", expanded=True):
            # Load the investment signals data
            data_file = "data/investment_signals_complete.csv"
            
            if os.path.exists(data_file):
                df = pd.read_csv(data_file)
                
                # Apply styling to the final_signal column
                styled_df = df.style.applymap(
                    color_final_signal, 
                    subset=['final_signal']
                )
                
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=600
                )
                
                # Summary statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    buy_count = len(df[df['final_signal'] == 'BUY'])
                    st.metric("🟢 BUY", buy_count)
                
                with col2:
                    hold_count = len(df[df['final_signal'] == 'HOLD'])
                    st.metric("🟡 HOLD", hold_count)
                
                with col3:
                    sell_count = len(df[df['final_signal'] == 'SELL'])
                    st.metric("🔴 SELL", sell_count)
                    
            else:
                st.error(f"❌ Không tìm thấy file: {data_file}")
                st.info("Vui lòng chạy script generate_investment_signals.py trước")

if __name__ == "__main__":
    main()