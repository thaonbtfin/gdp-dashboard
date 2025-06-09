# Bước 2: Lưu mô hình sau khi huấn luyện
import joblib

def save_model(model, le, ticker):
    os.makedirs("models", exist_ok=True)
    joblib.dump((model, le), f"models/{ticker}_model.pkl")

def load_model(ticker):
    path = f"models/{ticker}_model.pkl"
    if os.path.exists(path):
        return joblib.load(path)
    return None

# Trong phần huấn luyện trong Streamlit:
model_data = load_model(ticker)
if model_data:
    model, le = model_data
    report = {}  # không có báo cáo khi tải
else:
    model, report, le = train_model(data)
    save_model(model, le, ticker)

# Bước 4: Tự động cập nhật dữ liệu hàng ngày
# Đối với Google Sheets, sử dụng gspread (cần chia sẻ file và lấy API credentials):
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def load_google_sheet(sheet_url, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).worksheet(worksheet_name)
    df = pd.DataFrame(sheet.get_all_records())
    df['time'] = pd.to_datetime(df['time'])
    return df

# Backtest đơn giản: theo dõi lợi nhuận nếu theo khuyến nghị

def simple_backtest(data):
    cash = 1.0
    position = 0.0
    for i in range(len(data)-1):
        action = data.iloc[i]['predicted_action']
        price_today = data.iloc[i]['close']
        price_next = data.iloc[i+1]['close']
        if action == 'Buy' and cash > 0:
            position = cash / price_today
            cash = 0
        elif action == 'Sell' and position > 0:
            cash = position * price_today
            position = 0
    # Cuối kì thanh lý
    if position > 0:
        cash = position * data.iloc[-1]['close']
    return cash  # Lợi nhuận cuối kì
