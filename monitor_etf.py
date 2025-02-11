import requests
import pandas as pd
import numpy as np
import time
import yfinance as yf
import time
from datetime import datetime
import os

LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")


# get 006208 ETD historical data

def get_stock_data():
    stock = yf.Ticker('006208.TW')
    df = stock.history(period='1mo')
    return df


# 計算 K 值（隨機指數）
def calculate_stochastic_k(df, period=14):
    df["Low"] = df["Low"].rolling(window=period).min()
    df["High"] = df["High"].rolling(window=period).max()
    df["%K"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"]) * 100
    return df


# 發送 LINE 訊息
def send_line_message(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    requests.post(url, headers=headers, data=data)

# 獲取最新的收盤價
def get_latest_price():
    ticker = yf.Ticker('006208.TW')  # 006208 是台灣 ETF 的代碼
    df = ticker.history(period='1d')  # 抓取當天的數據
    if not df.empty:
        return df['Close'].iloc[-1]  # 獲取最新的收盤價
    return None

# 每小時報一次最新目標價
def monitor_latest_price():
    while True:
        latest_price = get_latest_price()
        if latest_price is not None:
            message = f"📢 006208 ETF 最新收盤價為：{latest_price:.2f} 元"
            send_line_message(message)
        time.sleep(3600)  # 每小時執行一次

# 主程式
if __name__ == "__main__":
    monitor_latest_price()

# 監控 ETF K 值
# def monitor_etf():
    # while True:
    #     df = get_stock_data()
    #     df = calculate_stochastic_k(df)

    #     latest_k = df["%K"].iloc[-1]  # 最新 K 值

    #     if latest_k < 20:  # 低於 20 時發送通知
    #         send_line_message(f"⚠️ 006208 ETF K值跌破 20，目前為 {latest_k:.2f}，請關注市場！")

    #     time.sleep(3600)  # 每小時檢查一次

# if __name__ == "__main__":
#     monitor_etf()