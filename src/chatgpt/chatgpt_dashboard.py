


from pathlib import Path

import numpy as np
import pandas as pd
import requests
import plotly.express as px
from sklearn.calibration import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
import streamlit as st
from xgboost import XGBClassifier

class ChatGPT_def:

    @staticmethod
    def models_prediction(df):
        if df.empty:
            st.warning("Chưa có dữ liệu để hiển thị.")
            st.stop()

        tickers = [col for col in df.columns if col not in ['time', 'VNINDEX']]
        models = {}
        latest_predictions = []

        for ticker in tickers:
            data = ChatGPT_def.create_features(df, ticker)
            if data['action'].nunique() < 2:
                continue
            try:
                model, report, le = ChatGPT_def.train_model(data)
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

        return models, latest_predictions_df

    @staticmethod
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

    @staticmethod
    def add_financial_indicators(data):
        np.random.seed(42)
        data['eps'] = np.random.normal(5, 0.5, size=len(data))
        data['roe'] = np.random.normal(15, 2, size=len(data))
        return data

    @staticmethod
    def create_features(df, stock):
        data = df[['time', stock]].copy()
        data.rename(columns={stock: 'close'}, inplace=True)
        data = ChatGPT_def.calculate_technical_indicators(data)
        data = ChatGPT_def.add_financial_indicators(data)
        future_return = data['close'].shift(-5) / data['close'] - 1
        data['action'] = pd.cut(
            future_return,
            bins=[-np.inf, -0.05, 0.05, np.inf],
            labels=['Sell', 'Hold', 'Buy']
        )
        data.dropna(inplace=True)
        return data

    @staticmethod
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

    @staticmethod
    def run_backtest(data):
        capital = 1.0
        position = 0
        capital_history = []

        for i in range(len(data)):
            action = data.iloc[i]['predicted_action']
            price = data.iloc[i]['close']

            if action == 'Buy' and position == 0:
                position = capital / price
                capital = 0
            elif action == 'Sell' and position > 0:
                capital = position * price
                position = 0

            current_value = capital if position == 0 else position * price
            capital_history.append(current_value)

        data['portfolio_value'] = capital_history
        return data

class ChatGPT_st:
    
    @staticmethod
    def all_tab(df):
        latest_predictions_df=df
        st.subheader("Khuyến nghị tổng hợp")
        st.dataframe(latest_predictions_df)
        # Thu, 12Jun: bảng cần hiển thị theo từng cổ phiếu với thông tin cột là: ngày, thị giá, TLSN 5 năm, ĐLC 5 năm

    @staticmethod
    def detail_tab(models):
        selected = st.selectbox("Chọn mã cổ phiếu", list(models.keys()))
    
        model, data, report, le = models[selected]
        last_rows = data.tail(100).copy()

        pred_encoded = model.predict(last_rows[['ma5', 'ma10', 'return_1d', 'return_5d', 'rsi', 'eps', 'roe']])
        last_rows['predicted_action'] = le.inverse_transform(pred_encoded)

        accuracy = report.get('accuracy', 0) * 100
        last_rows['Accuracy (%)'] = f"{accuracy:.2f}%"

        last_rows = last_rows.sort_values(by='time', ascending=False)

        st.subheader(f"Biểu đồ giá và khuyến nghị: {selected}")
        # st.info(f"Khuyến nghị gần nhất: **{last_rows.iloc[0]['predicted_action']}**", icon="ℹ️")
        st.markdown(f"ℹ️ Khuyến nghị gần nhất: **{last_rows.iloc[0]['predicted_action']}**")
        fig = px.line(last_rows, x='time', y='close', title=f'Giá đóng cửa - {selected}')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"Biểu đồ giá: {selected}")
        st.dataframe(last_rows[['time', 'close', 'ma5', 'rsi', 'eps', 'roe']].reset_index(drop=True))

    @staticmethod
    def backtest_tab(models):
        st.subheader("")
        selected_bt = st.selectbox("Chọn mã cổ phiếu để backtest", list(models.keys()), key="backtest_select")

        model, data_bt, _, le = models[selected_bt]
        last_rows_bt = data_bt.tail(200).copy()
        pred_encoded_bt = model.predict(last_rows_bt[['ma5', 'ma10', 'return_1d', 'return_5d', 'rsi', 'eps', 'roe']])
        last_rows_bt['predicted_action'] = le.inverse_transform(pred_encoded_bt)

        bt_result = ChatGPT_def.run_backtest(last_rows_bt)

        fig_bt = px.line(bt_result, x='time', y='portfolio_value', title=f'Giá trị danh mục nếu làm theo khuyến nghị - {selected_bt}')
        st.plotly_chart(fig_bt, use_container_width=True)
        st.write(f"Giá trị cuối cùng: {bt_result['portfolio_value'].iloc[-1]:.2f}x so với vốn ban đầu")

    @staticmethod
    def report_tab(models):
        st.subheader("Báo cáo")
        selected_report = st.selectbox("Chọn mã cổ phiếu để xem báo cáo", list(models.keys()), key="report_select")
        # for ticker in models:
        #     _, _, report, _ = models[ticker]
        #     st.markdown(f"### {ticker}")
        #     st.json(report)
        _, _, report, _ = models[selected_report]
        st.markdown(f"### {selected_report}")
        st.json(report)