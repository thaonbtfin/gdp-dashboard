import streamlit as st
import pandas as pd
import math
import numpy as np
from pathlib import Path

from src.tastock.ui.dashboard import TAstock_def, TAstock_st
from src.streamlit.streamlit_dashboard import Streamlit_def
from src.tastock.data.data_manager import DataManager
from src.constants import DATA_DIR

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Stock History Dashboard',
    page_icon=':chart_with_upwards_trend:',
    layout='wide'
)

# ============================
# Load and preprocess data
# ============================



# ============================
# Streamlit UI
# ============================

with st.spinner("Đang tải dữ liệu..."):
    df = Streamlit_def.load_data()
    
    # Load BizUni data using DataManager
    data_manager = DataManager(base_output_dir=DATA_DIR)
    bizuni_df = data_manager.load_latest_data('bizuni')

# Main check for loaded data
if df.empty:
    st.warning("Không có dữ liệu để hiển thị. Vui lòng chọn nguồn dữ liệu hợp lệ, tải lên tệp CSV, hoặc kiểm tra lại thông báo lỗi (nếu có).")
    # Still create tabs so user can attempt to load data again.
    # Content within tabs will show specific messages.

history_tab, investment_tab, technical_tab, detail_tab, bizuni_tab, notification_tab = st.tabs(["🗂 History", "💼 Phân tích Đầu tư", "📈 Phân tích kỹ thuật", "🔍 Details", "📁 BizUni", "🔔 Thông báo"])

with history_tab:
    if df.empty:
        st.info("Không có dữ liệu để hiển thị biểu đồ lịch sử. Vui lòng chọn hoặc tải lên dữ liệu hợp lệ.")
    else:
        # Process data for history tab only if raw data (df) is available
        stock_df_melted = TAstock_def.get_stock_data(df.copy())
        TAstock_st.history_sub_tab(stock_df_melted)

with investment_tab:
    if df.empty:
        st.info("Không có dữ liệu để phân tích đầu tư. Vui lòng chọn hoặc tải lên dữ liệu hợp lệ.")
    else:
        TAstock_st.investment_analysis_tab(df)

with technical_tab:
    if df.empty:
        st.info("Không có dữ liệu để phân tích kỹ thuật. Vui lòng chọn hoặc tải lên dữ liệu hợp lệ.")
    else:
        TAstock_st.technical_analysis_tab(df)

with detail_tab:
    if df.empty:
        st.info("Không có dữ liệu để hiển thị chi tiết. Vui lòng chọn hoặc tải lên dữ liệu hợp lệ.")
    else:
        TAstock_st.detail_tab(df) # df is the raw dataframe

with bizuni_tab:
    # Load BizUni data from CSV file
    bizuni_file = Path("data/bizuni_cpgt.csv")
    if bizuni_file.exists():
        try:
            bizuni_df = pd.read_csv(bizuni_file)
            
            # Extract intrinsic value columns and current price
            def extract_numeric(val):
                if pd.isna(val) or val == '':
                    return 0
                try:
                    # Clean the value: remove quotes, commas, spaces, and percentage signs
                    clean_val = str(val).replace(',', '').replace('"', '').replace('%', '').replace('&#39;', '').strip()
                    return float(clean_val)
                except (ValueError, TypeError):
                    return 0
            
            # Store BizUni data for notification tab
            st.session_state['bizuni_data'] = bizuni_df.copy()
            
            # Get safety margin from column 5
            bizuni_df['safety_margin'] = bizuni_df.iloc[:, 5].apply(extract_numeric)
            
            # Categorize into 3 groups based on safety_margin
            valid_margins = bizuni_df[bizuni_df['safety_margin'] != 0]['safety_margin']
            if len(valid_margins) > 0:
                q33 = valid_margins.quantile(0.33)
                q67 = valid_margins.quantile(0.67)
                
                def categorize_stock(margin):
                    if margin == 0:
                        return 'med'
                    elif margin >= q67:
                        return 'max'
                    elif margin <= q33:
                        return 'min'
                    else:
                        return 'med'
                
                bizuni_df['category'] = bizuni_df['safety_margin'].apply(categorize_stock)
            else:
                bizuni_df['category'] = 'med'
            
            # Define styling function
            def highlight_rows(row):
                if row['category'] == 'max':
                    return ['background-color: #CCFFCC'] * len(row)  # Light green
                elif row['category'] == 'min':
                    return ['background-color: #FFFFE0'] * len(row)  # Light yellow
                else:  # med
                    return ['background-color: #CCFFFF'] * len(row)  # Light blue
            
            # Display data
            
            # Show category counts with ranges
            category_counts = bizuni_df['category'].value_counts()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🟢 MAX Value → Ưu tiên đầu tư", category_counts.get('max', 0))
                if len(valid_margins) > 0:
                    st.caption(f"Biên độ an toàn ≥ {q67:.1f}%")
            with col2:
                st.metric("🔵 MEDIUM Value → Cân nhắc", category_counts.get('med', 0))
                if len(valid_margins) > 0:
                    st.caption(f"{q33:.1f}% < Biên độ < {q67:.1f}%")
            with col3:
                st.metric("🟡 MIN Value → Thận trọng", category_counts.get('min', 0))
                if len(valid_margins) > 0:
                    st.caption(f"Biên độ an toàn ≤ {q33:.1f}%")
            
            # Add explanation expander
            with st.expander("📋 Hướng dẫn nhanh"):
                st.markdown("""
**Biên độ an toàn = % giảm giá so với giá trị thực**

**Màu sắc:**
- 🟢 **Xanh lá**: Giảm giá nhiều nhất → **Ưu tiên mua**
- 🔵 **Xanh dương**: Giảm giá vừa → **Cân nhắc**
- 🟡 **Vàng**: Giảm giá ít → **Thận trọng**

**Chiến lược:** Tập trung vào cổ phiếu **xanh lá** để có cơ hội tốt nhất!
                """)
            
            # Apply styling and display
            styled_df = bizuni_df.style.apply(highlight_rows, axis=1)
            display_df = bizuni_df.drop(['safety_margin', 'category'], axis=1)
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            st.success(f"✅ Hiển thị {len(bizuni_df)} cổ phiếu - Phân loại theo biên độ an toàn. Hãy tập trung vào các cổ phiếu **xanh lá** để có cơ hội đầu tư tốt nhất!")
            
        except Exception as e:
            st.error(f"Lỗi khi đọc file BizUni: {e}")
    else:
        st.warning("Không tìm thấy file bizuni_cpgt.csv. Vui lòng chạy crawler BizUni trước.")

with notification_tab:
    
    # Load investment signals
    signals_file = Path("data/investment_signals_complete.csv")
    if signals_file.exists():
        try:
            signals_df = pd.read_csv(signals_file)
            
            # Load BizUni data for categorization
            bizuni_file = Path("data/bizuni_cpgt.csv")
            bizuni_categories = {}
            if bizuni_file.exists():
                bizuni_df = pd.read_csv(bizuni_file)
                def extract_numeric(val):
                    if pd.isna(val) or val == '':
                        return 0
                    try:
                        clean_val = str(val).replace(',', '').replace('"', '').replace('%', '').replace('&#39;', '').strip()
                        return float(clean_val)
                    except (ValueError, TypeError):
                        return 0
                
                bizuni_df['safety_margin'] = bizuni_df.iloc[:, 5].apply(extract_numeric)
                valid_margins = bizuni_df[bizuni_df['safety_margin'] != 0]['safety_margin']
                if len(valid_margins) > 0:
                    q33 = valid_margins.quantile(0.33)
                    q67 = valid_margins.quantile(0.67)
                    
                    for _, row in bizuni_df.iterrows():
                        symbol = row.iloc[1]  # Column 1 is stock symbol
                        margin = row['safety_margin']
                        if margin >= q67:
                            bizuni_categories[symbol] = 'max'
                        elif margin <= q33:
                            bizuni_categories[symbol] = 'min'
                        else:
                            bizuni_categories[symbol] = 'med'
            
            # Filter for BUY and SELL signals
            buy_signals = signals_df[signals_df['final_signal'] == 'BUY'].copy()
            sell_signals = signals_df[signals_df['final_signal'] == 'SELL'].copy()
            
            # Add BizUni category for both BUY and SELL
            def get_priority(row, signal_type):
                bizuni_cat = bizuni_categories.get(row['symbol'], 'unknown')
                if signal_type == 'BUY':
                    if bizuni_cat == 'max':
                        return '🟢 Cao'
                    elif bizuni_cat == 'med':
                        return '🔵 Trung bình'
                    elif bizuni_cat == 'min':
                        return '🟡 Thấp'
                    else:
                        return '⚪ Chưa xác định'
                else:  # SELL
                    return '🔴 Tránh'
            
            if not buy_signals.empty:
                buy_signals['priority'] = buy_signals.apply(lambda row: get_priority(row, 'BUY'), axis=1)
                buy_signals = buy_signals.sort_values(['confidence_pct', 'total_score'], ascending=[False, False])
            
            if not sell_signals.empty:
                sell_signals['priority'] = sell_signals.apply(lambda row: get_priority(row, 'SELL'), axis=1)
                sell_signals = sell_signals.sort_values(['confidence_pct', 'total_score'], ascending=[False, False])
            
            # Display summary metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                buy_high = len(buy_signals[buy_signals['priority'] == '🟢 Cao']) if not buy_signals.empty else 0
                st.metric("🟢 BUY Cao", buy_high)
            with col2:
                buy_med = len(buy_signals[buy_signals['priority'] == '🔵 Trung bình']) if not buy_signals.empty else 0
                st.metric("🔵 BUY TB", buy_med)
            with col3:
                buy_low = len(buy_signals[buy_signals['priority'] == '🟡 Thấp']) if not buy_signals.empty else 0
                st.metric("🟡 BUY Thấp", buy_low)
            with col4:
                sell_count = len(sell_signals) if not sell_signals.empty else 0
                st.metric("🔴 SELL", sell_count)
            with col5:
                total_signals = len(buy_signals) + len(sell_signals)
                st.metric("📊 Tổng", total_signals)
            
            # Quick guide moved here
            with st.expander("📋 Hướng dẫn đọc thông báo"):
                st.markdown("""
**Tín hiệu BUY - Ưu tiên đầu tư:**
- 🟢 **Cao**: BUY + BizUni Max → Ưu tiên đầu tư cao nhất
- 🔵 **Trung bình**: BUY + BizUni Med → Cân nhắc đầu tư
- 🟡 **Thấp**: BUY + BizUni Min → Thận trọng

**Tín hiệu SELL:**
- 🔴 **Tránh**: Các cổ phiếu nên tránh hoặc bán ra

**Các phương pháp phân tích:**
- **Value**: Phân tích giá trị (P/E, ROE)
- **CANSLIM**: Phân tích tăng trưởng và động lực
- **Kỹ thuật**: Phân tích biểu đồ và xu hướng
                """)
                
            # Create tabs for BUY and SELL signals
            buy_tab, sell_tab = st.tabs(["🟢 Tín hiệu BUY", "🔴 Tín hiệu SELL"])
            
            with buy_tab:
                if not buy_signals.empty:
                    st.subheader("📋 Danh sách Tín hiệu BUY")
                    
                    # Create display dataframe for BUY
                    display_cols = ['symbol', 'current_price', 'priority', 'confidence_pct', 'total_score', 'value_signal', 'canslim_signal', 'technical_signal']
                    buy_notification_df = buy_signals[display_cols].copy()
                    buy_notification_df.columns = ['Mã CP', 'Giá hiện tại', 'Ưu tiên', 'Độ tin cậy (%)', 'Điểm tổng', 'Value', 'CANSLIM', 'Kỹ thuật']
                    
                    # Style the dataframe
                    def highlight_buy_priority(row):
                        if '🟢' in str(row['Ưu tiên']):
                            return ['background-color: #CCFFCC'] * len(row)
                        elif '🔵' in str(row['Ưu tiên']):
                            return ['background-color: #CCFFFF'] * len(row)
                        elif '🟡' in str(row['Ưu tiên']):
                            return ['background-color: #FFFFE0'] * len(row)
                        else:
                            return [''] * len(row)
                    
                    styled_buy_df = buy_notification_df.style.apply(highlight_buy_priority, axis=1)
                    st.dataframe(styled_buy_df, use_container_width=True, hide_index=True)
                    
                    st.success(f"✅ Tìm thấy {len(buy_signals)} tín hiệu BUY. Tập trung vào **ưu tiên cao** (🟢)!")
                else:
                    st.info("Hiện tại không có tín hiệu BUY nào.")
            
            with sell_tab:
                if not sell_signals.empty:
                    st.subheader("📋 Danh sách Tín hiệu SELL")
                    
                    # Create display dataframe for SELL
                    display_cols = ['symbol', 'current_price', 'priority', 'confidence_pct', 'total_score', 'value_signal', 'canslim_signal', 'technical_signal']
                    sell_notification_df = sell_signals[display_cols].copy()
                    sell_notification_df.columns = ['Mã CP', 'Giá hiện tại', 'Cảnh báo', 'Độ tin cậy (%)', 'Điểm tổng', 'Value', 'CANSLIM', 'Kỹ thuật']
                    
                    # Style SELL signals with red background
                    def highlight_sell_priority(row):
                        return ['background-color: #FFCCCB'] * len(row)  # Light red for all SELL signals
                    
                    styled_sell_df = sell_notification_df.style.apply(highlight_sell_priority, axis=1)
                    st.dataframe(styled_sell_df, use_container_width=True, hide_index=True)
                    
                    st.warning(f"⚠️ Tìm thấy {len(sell_signals)} tín hiệu SELL. Cân nhắc **tránh hoặc bán** các cổ phiếu này!")
                else:
                    st.info("Hiện tại không có tín hiệu SELL nào.")
                

            
            # Overall summary
            if not buy_signals.empty or not sell_signals.empty:
                total_buy = len(buy_signals)
                total_sell = len(sell_signals)
                if total_buy > 0 and total_sell > 0:
                    st.info(f"📊 Tổng kết: {total_buy} tín hiệu BUY và {total_sell} tín hiệu SELL")
                elif total_buy > 0:
                    st.success(f"📊 Tổng kết: {total_buy} tín hiệu BUY")
                elif total_sell > 0:
                    st.warning(f"📊 Tổng kết: {total_sell} tín hiệu SELL")
            else:
                st.info("Hiện tại không có tín hiệu BUY hoặc SELL nào.")
                
        except Exception as e:
            st.error(f"Lỗi khi đọc dữ liệu tín hiệu: {e}")
    else:
        st.warning("Không tìm thấy file investment_signals_complete.csv. Vui lòng chạy phân tích đầu tư trước.")