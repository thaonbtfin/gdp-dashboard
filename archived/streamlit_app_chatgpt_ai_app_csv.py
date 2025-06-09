import pandas as pd
import numpy as np
import streamlit as st
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import plotly.express as px

# ============================
# Step 1: Load and preprocess data
# ============================
@st.cache_data

def load_data():
    url = "https://gist.githubusercontent.com/thaonbtfin/fcb2906734735389faa0d32c8b47d456/raw/5dcc232d24f45b95e388e334c3ceeddc874752e9/sample_history_stockData.csv"
    df = pd.read_csv(url)
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

def create_features(df, stock):
    data = df[['time', stock]].copy()
    data.rename(columns={stock: 'close'}, inplace=True)
    data = calculate_technical_indicators(data)
    
    # Labeling
    future_return = data['close'].shift(-5) / data['close'] - 1
    data['action'] = pd.cut(
        future_return,
        bins=[-np.inf, -0.05, 0.05, np.inf],
        labels=['Sell', 'Hold', 'Buy']
    )
    data.dropna(inplace=True)
    return data

def train_model(data, all_classes):
    X = data[['ma5', 'ma10', 'return_1d', 'return_5d', 'rsi']]
    y = data['action']

    le = LabelEncoder()
    le.fit(all_classes)
    y_encoded = le.transform(y)

    # Check if every present class has at least 2 samples
    unique, counts = np.unique(y_encoded, return_counts=True)
    if np.any(counts < 2):
        return None, None, le  # Not enough data to train

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

    present_labels = np.unique(np.concatenate([y_test, y_pred]))
    report = classification_report(
        y_test, y_pred,
        output_dict=True,
        labels=present_labels,
        target_names=le.inverse_transform(present_labels)
    )
    return model, report, le

# ============================
# Streamlit UI
# ============================
st.set_page_config(page_title="AI Dự đoán Chứng khoán", layout="wide")
st.title("📊 AI khuyến nghị Mua / Giữ / Bán cổ phiếu")

with st.spinner("Đang tải dữ liệu và huấn luyện mô hình..."):
    df = load_data()
    tickers = [col for col in df.columns if col not in ['time', 'VNINDEX']]
    models = {}
    latest_predictions = []
    all_classes = ['Sell', 'Hold', 'Buy']

    for ticker in tickers:
        data = create_features(df, ticker)
        model, report, le = train_model(data, all_classes)
        if model is None:
            continue  # Skip tickers with insufficient data
        models[ticker] = (model, data, le)
        latest = data.iloc[-1]
        pred_encoded = model.predict([latest[['ma5', 'ma10', 'return_1d', 'return_5d', 'rsi']].values])[0]
        pred = le.inverse_transform([pred_encoded])[0]
        latest_predictions.append({
            'Mã': ticker,
            'Giá hiện tại': latest['close'],
            'Khuyến nghị': pred
        })

# Tabs UI
all_tab, detail_tab = st.tabs(["📋 Tất cả cổ phiếu", "🔍 Chi tiết cổ phiếu"])

# Tóm tắt tất cả
with all_tab:
    st.subheader("Khuyến nghị tổng hợp")
    st.dataframe(pd.DataFrame(latest_predictions))

# Chi tiết từng mã
with detail_tab:
    selected = st.selectbox("Chọn mã cổ phiếu", tickers)
    model, data, le = models[selected]
    last_rows = data.tail(100).copy()
    pred_encoded = model.predict(last_rows[['ma5', 'ma10', 'return_1d', 'return_5d', 'rsi']])
    last_rows['predicted_action'] = le.inverse_transform(pred_encoded)

    st.subheader(f"Biểu đồ giá và khuyến nghị: {selected}")
    fig = px.line(last_rows, x='time', y='close', title=f'Giá đóng cửa - {selected}')
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(last_rows[['time', 'close', 'ma5', 'rsi', 'predicted_action']].reset_index(drop=True))