import streamlit as st
import pandas as pd
import math
import numpy as np
from pathlib import Path

from src.tastock.ui.dashboard import TAstock_def, TAstock_st
from src.streamlit.streamlit_dashboard import Streamlit_def
from src.tastock.data.data_manager import DataManager
from src.portfolio_loader_csv import get_portfolios_csv
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

# Simple Portfolio Manager - CSV Based
@st.cache_data(ttl=3600)
def get_portfolios_cached():
    return get_portfolios_csv()

portfolios = get_portfolios_cached()

# Simple portfolio summary with data info
total_symbols = sum(len(symbols) for symbols in portfolios.values())
from src.portfolio_loader_csv import get_latest_data_folder
latest_folder = get_latest_data_folder()
if latest_folder:
    st.info(f"📊 {len(portfolios)} portfolios loaded • {total_symbols} symbols total • Data from: {latest_folder}")
else:
    st.warning("⚠️ No data folder found. Please run complete data update first.")

# Sidebar data update section
if latest_folder:
    st.sidebar.markdown(f"📅 Current Data: {latest_folder}")

# Button 1: Refresh Portfolios
if st.sidebar.button("🔄 Refresh Portfolios"):
    st.cache_data.clear()
    st.rerun()

# Button 2: Complete Data Update
if st.sidebar.button("📊 Update Data (~5 min)"):
    with st.spinner("Running complete data pipeline..."):
        import subprocess
        import sys
        try:
            # Run the workflow which now includes Git commit and push
            result = subprocess.run(
                [sys.executable, "src/tastock/workflows/wf_stock_data_updater.py"],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                st.success("✅ Data pipeline completed! Refreshing page...")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"❌ Pipeline failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            st.error("⏰ Pipeline timeout (5 minutes). Try running manually.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

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
    st.header("🔔 Cài đặt Thông báo")
    
    # Notification Configuration Section
    with st.expander("⚙️ Cấu hình Thông báo", expanded=False):
        st.markdown("### 📱 Cài đặt Kênh thông báo")
        
        # Load current config
        from src.tastock.notifications.config import NotificationConfig
        from src.tastock.notifications.gdrive_config import get_gdrive_url, set_gdrive_url, create_sample_config, get_folder_instructions
        
        # Google Drive configuration
        st.markdown("### ☁️ Google Drive Configuration")
        st.info("📁 **Shared Folder**: https://drive.google.com/drive/folders/1250E9USH25t0sy3np9ajhurpdYROpm9N")
        
        col_url1, col_url2 = st.columns([3, 1])
        with col_url1:
            gdrive_file_url = st.text_input(
                "Config File URL",
                value=get_gdrive_url(),
                help="Upload notification_config.json to shared folder, share it, then paste URL here"
            )
        
        with col_url2:
            if st.button("💾 Save"):
                if set_gdrive_url(gdrive_file_url):
                    st.success("✅ Saved!")
                else:
                    st.error("❌ Failed")
        
        st.markdown("**📝 Setup Instructions:**")
        st.markdown(get_folder_instructions())
        st.code(create_sample_config(), language='json')
        
        config = NotificationConfig(gdrive_url=gdrive_file_url)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Telegram Bot**")
            telegram_token = st.text_input("Bot Token", value=config.get('telegram_bot_token', ''), type="password")
            telegram_chat = st.text_input("Chat ID", value=config.get('telegram_chat_id', ''))
            
            st.markdown("**Discord Webhook**")
            discord_webhook = st.text_input("Webhook URL", value=config.get('discord_webhook_url', ''), type="password")
        
        with col2:
            st.markdown("**Email SMTP**")
            email_user = st.text_input("Email", value=config.get('email_user', ''))
            email_pass = st.text_input("Password", value=config.get('email_pass', ''), type="password")
            email_to = st.text_input("Send To", value=config.get('email_to', ''))
            
            st.markdown("**Pushover**")
            pushover_token = st.text_input("App Token", value=config.get('pushover_app_token', ''), type="password")
            pushover_user = st.text_input("User Key", value=config.get('pushover_user_key', ''), type="password")
        
        # Notification settings
        st.markdown("### 🎯 Cài đặt Tín hiệu")
        col3, col4 = st.columns(2)
        
        with col3:
            threshold = st.slider("Ngưỡng độ tin cậy (%)", 50, 100, config.get_threshold())
            
        with col4:
            enabled_channels = st.multiselect(
                "Kênh kích hoạt",
                ['telegram', 'discord', 'email', 'pushover'],
                default=config.get('enabled_channels', ['telegram', 'discord'])
            )
        
        # Save configuration
        if st.button("💾 Lưu cấu hình"):
            new_config = {
                'telegram_bot_token': telegram_token,
                'telegram_chat_id': telegram_chat,
                'discord_webhook_url': discord_webhook,
                'email_user': email_user,
                'email_pass': email_pass,
                'email_to': email_to,
                'pushover_app_token': pushover_token,
                'pushover_user_key': pushover_user,
                'notification_threshold': threshold,
                'enabled_channels': enabled_channels
            }
            config.save_config(new_config)
            st.success("✅ Đã lưu cấu hình thông báo!")
            st.rerun()  # Refresh to show updated validation
        
        # Show config validation
        st.markdown("**🔍 Config Status:**")
        validation = config.validate_config()
        col_val1, col_val2, col_val3, col_val4 = st.columns(4)
        with col_val1:
            st.write(f"Telegram: {'✅' if validation['telegram'] else '❌'}")
        with col_val2:
            st.write(f"Discord: {'✅' if validation['discord'] else '❌'}")
        with col_val3:
            st.write(f"Email: {'✅' if validation['email'] else '❌'}")
        with col_val4:
            st.write(f"Pushover: {'✅' if validation['pushover'] else '❌'}")
        
        # Test notification
        if st.button("🧪 Test Thông báo"):
            from src.tastock.notifications.notification_service import NotificationService
            service = NotificationService(config.config)
            
            test_data = {
                'stock_code': 'TEST',
                'signal': 'BUY',
                'confidence': 85,
                'price': 50000
            }
            
            results = service.send_notification(test_data)
            
            for channel, success in results.items():
                if channel in enabled_channels:
                    if success:
                        st.success(f"✅ {channel.title()}: Thành công")
                    else:
                        st.error(f"❌ {channel.title()}: Thất bại - Kiểm tra cấu hình")
    
    st.markdown("### 📊 Tín hiệu Đầu tư")
    
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
            
            # Auto-notification toggle
            st.markdown("### 🔔 Thông báo Tự động")
            
            col_auto1, col_auto2 = st.columns(2)
            with col_auto1:
                auto_notify = st.checkbox("Bật thông báo tự động", help="Tự động gửi thông báo khi có tín hiệu mới")
            
            with col_auto2:
                if st.button("📤 Gửi thông báo ngay"):
                    from src.tastock.notifications.notification_service import NotificationService
                    from src.tastock.notifications.config import NotificationConfig
                    from src.tastock.notifications.gdrive_config import get_gdrive_url
                    
                    config = NotificationConfig(gdrive_url=get_gdrive_url())
                    service = NotificationService(config.config)
                    
                    # Send notifications for high-priority BUY signals
                    high_priority_buys = buy_signals[buy_signals['priority'] == '🟢 Cao'] if not buy_signals.empty else pd.DataFrame()
                    
                    if not high_priority_buys.empty:
                        sent_count = 0
                        for _, row in high_priority_buys.iterrows():
                            notification_data = {
                                'stock_code': row['symbol'],
                                'signal': 'BUY',
                                'confidence': int(row['confidence_pct']),
                                'price': row['current_price']
                            }
                            results = service.send_notification(notification_data)
                            if any(results.values()):
                                sent_count += 1
                        
                        if sent_count > 0:
                            st.success(f"✅ Đã gửi {sent_count} thông báo BUY ưu tiên cao!")
                        else:
                            st.error("❌ Không thể gửi thông báo. Kiểm tra cấu hình.")
                    else:
                        st.info("Không có tín hiệu BUY ưu tiên cao để gửi.")
                
        except Exception as e:
            st.error(f"Lỗi khi đọc dữ liệu tín hiệu: {e}")
    else:
        st.warning("Không tìm thấy file investment_signals_complete.csv. Vui lòng chạy phân tích đầu tư trước.")