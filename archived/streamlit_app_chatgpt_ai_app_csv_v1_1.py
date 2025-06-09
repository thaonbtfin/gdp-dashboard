import pandas as pd
import numpy as np
import streamlit as st
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import plotly.express as px
import requests
import io
from sklearn.preprocessing import LabelEncoder

# ============================
# Step 1: Load and preprocess data
# ============================

def load_data():
    source = st.sidebar.radio("Chọn nguồn dữ liệu:", ["CSV URL", "Upload CSV", "API"], index=0)

    if source == "CSV URL":
        try:
            url = "https://gist.githubusercontent.com/thaonbtfin/fcb2906734735389faa0d32c8b47d456/raw/5dcc232d24f45b95e388e334c3ceeddc874752e9/sample_history_stockData.csv"
            response = requests.get(url)
            df = pd.read_csv(io.StringIO(response.text))
        except Exception as e:
            st.error(f"Không thể tải file CSV: {e}")
            return pd.DataFrame()

    elif source == "Upload CSV":
        uploaded_file = st.sidebar.file_uploader("Upload file CSV chứa dữ liệu chứng khoán", type=["csv"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
            except Exception as e:
                st.error(f"Lỗi đọc file CSV: {e}")
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    elif source == "API":
        try:
            api_url = "https://api.mocki.io/v2/12345678/stockdata"  # Replace with actual API URL
            response = requests.get(api_url)
            json_data = response.json()
            df = pd.DataFrame(json_data)
        except Exception as e:
            st.error(f"Không thể tải dữ liệu từ API: {e}")
            return pd.DataFrame()

    df['time'] = pd.to_datetime(df['time'], format='%Y%m%d')
    df.sort_values('time', inplace=True)
    return df

def calculate_technical_indicators(data):
    data['ma5'] = data['close'].rolling(window=5).mean()
    data['ma10'] = data['close'].rolling(window=10).mean()
    data['return_1d'] = data['close'].pct_change(1)
    data['return_5d'] = data['close'].pct_change(5)
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    return data

def add_financial_indicators(data):
    np.random.seed(42)
    data['eps'] = np.random.normal(5, 0.5, size=len(data))
    data['roe'] = np.random.normal(15, 2, size=len(data))
    return data

def create_features(df, stock):
    data = df[['time', stock]].copy()
    data.rename(columns={stock: 'close'}, inplace=True)
    data = calculate_technical_indicators(data)
    data = add_financial_indicators(data)
    future_return = data['close'].shift(-5) / data['close'] - 1
    data['action'] = pd.cut(
        future_return,
        bins=[-np.inf, -0.05, 0.05, np.inf],
        labels=['Sell', 'Hold', 'Buy']
    )
    data.dropna(inplace=True)
    return data

def train_model(data):
    X = data[['ma5', 'ma10', 'return_1d', 'return_5d', 'rsi', 'eps', 'roe']]
    y = data['action']

    if y.nunique() < 2:
        raise ValueError("Cần ít nhất 2 lớp (Buy/Hold/Sell) để huấn luyện mô hình")

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    class_counts = pd.Series(y_encoded).value_counts()
    min_class_count = class_counts.min()

    if min_class_count < 2:
        st.warning("Một số lớp quá ít dữ liệu để phân chia train/test. Sẽ huấn luyện toàn bộ dữ liệu.")
        X_train, y_train = X, y_encoded
        X_test, y_test = X, y_encoded
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

    model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric='mlogloss',
        random_state=42
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True)
    return model, report, le

# ============================
# Streamlit UI
# ============================
st.set_page_config(page_title="AI Dự đoán Chứng khoán", layout="wide")
st.title("📊 AI khuyến nghị Mua / Giữ / Bán cổ phiếu")

with st.spinner("Đang tải dữ liệu và huấn luyện mô hình..."):
    df = load_data()
    if df.empty:
        st.warning("Chưa có dữ liệu để hiển thị.")
        st.stop()

    tickers = [col for col in df.columns if col not in ['time', 'VNINDEX']]
    models = {}
    latest_predictions = []

    for ticker in tickers:
        data = create_features(df, ticker)
        if data['action'].nunique() < 2:
            continue
        try:
            model, report, le = train_model(data)
        except Exception as e:
            st.warning(f"Lỗi khi huấn luyện mô hình cho {ticker}: {e}")
            continue

        models[ticker] = (model, data, report, le)
        latest = data.iloc[-1]

        pred_encoded = model.predict([latest[['ma5', 'ma10', 'return_1d', 'return_5d', 'rsi', 'eps', 'roe']].values])[0]
        pred_label = le.inverse_transform([pred_encoded])[0]

        accuracy = report.get('accuracy', 0) * 100

        latest_predictions.append({
            'Mã': ticker,
            'Giá hiện tại': latest['close'],
            'Khuyến nghị': pred_label,
            'Accuracy (%)': f"{accuracy:.2f}%"
        })

    latest_predictions_df = pd.DataFrame(latest_predictions)
    latest_predictions_df['Ngày cuối'] = latest_predictions_df['Mã'].apply(lambda t: models[t][1]['time'].max())
    latest_predictions_df = latest_predictions_df.sort_values(by='Ngày cuối', ascending=False).drop(columns=['Ngày cuối'])

all_tab, detail_tab, report_tab = st.tabs(["📋 Tất cả cổ phiếu", "🔍 Chi tiết cổ phiếu", "📈 Hiệu năng mô hình"])

with all_tab:
    st.subheader("Khuyến nghị tổng hợp")
    st.dataframe(latest_predictions_df)

with detail_tab:
    selected = st.selectbox("Chọn mã cổ phiếu", list(models.keys()))
    model, data, report, le = models[selected]
    last_rows = data.tail(100).copy()

    pred_encoded = model.predict(last_rows[['ma5', 'ma10', 'return_1d', 'return_5d', 'rsi', 'eps', 'roe']])
    last_rows['predicted_action'] = le.inverse_transform(pred_encoded)

    accuracy = report.get('accuracy', 0) * 100
    last_rows['Accuracy (%)'] = f"{accuracy:.2f}%"

    last_rows = last_rows.sort_values(by='time', ascending=False)

    st.subheader(f"Biểu đồ giá và khuyến nghị: {selected}")
    fig = px.line(last_rows, x='time', y='close', title=f'Giá đóng cửa - {selected}')
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(last_rows[['time', 'close', 'ma5', 'rsi', 'eps', 'roe', 'predicted_action', 'Accuracy (%)']].reset_index(drop=True))

with report_tab:
    st.subheader("Báo cáo độ chính xác mô hình")
    for ticker in models:
        _, _, report, _ = models[ticker]
        st.markdown(f"### {ticker}")
        st.json(report)
