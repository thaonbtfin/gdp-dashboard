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

# stock_df = TAstock_def.get_stock_data()

# ============================
# Streamlit UI
# ============================

with st.spinner("Đang tải dữ liệu và huấn luyện mô hình..."):
    df = Streamlit_def.load_data()
    # Melt the raw DataFrame to get the 'Symbol' column
    stock_df_melted = TAstock_def.get_stock_data(df.copy()) # Use df.copy() if df is used elsewhere in its raw form

history_tab, detail_tab  = st.tabs(["📁 History", "🔍 Stock details"])

with history_tab:
    TAstock_st.history_tab(stock_df_melted)

with detail_tab:
    TAstock_st.detail_tab(df)