import streamlit as st
import pandas as pd
import math
from pathlib import Path

from src.tastock.tastock_dashboard import TAstock_def, TAstock_st
from src.streamlit.streamlit_dashboard import Streamlit_def

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

# Main check for loaded data
if df.empty:
    st.warning("Không có dữ liệu để hiển thị. Vui lòng chọn nguồn dữ liệu hợp lệ, tải lên tệp CSV, hoặc kiểm tra lại thông báo lỗi (nếu có).")
    # Still create tabs so user can attempt to load data again.
    # Content within tabs will show specific messages.

history_tab, detail_tab  = st.tabs(["📁 History", "🔍 Details"])

with history_tab:
    if df.empty:
        st.info("Không có dữ liệu để hiển thị biểu đồ lịch sử. Vui lòng chọn hoặc tải lên dữ liệu hợp lệ.")
    else:
        # Process data for history tab only if raw data (df) is available
        stock_df_melted = TAstock_def.get_stock_data(df.copy())
        if stock_df_melted.empty:
            # This implies df was not empty, but get_stock_data resulted in an empty df.
            # TAstock_def.get_stock_data should have shown specific warnings/errors.
            st.info("Không thể xử lý dữ liệu để hiển thị biểu đồ lịch sử. Vui lòng kiểm tra định dạng dữ liệu hoặc các thông báo lỗi trước đó.")
        else:
            TAstock_st.history_tab(stock_df_melted)

with detail_tab:
    if df.empty:
        st.info("Không có dữ liệu để hiển thị chi tiết. Vui lòng chọn hoặc tải lên dữ liệu hợp lệ.")
    else:
        TAstock_st.detail_tab(df) # df is the raw dataframe