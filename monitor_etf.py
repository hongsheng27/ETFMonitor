import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, time as dtTime  
import os
import pytz


LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")

TARGET_ETF = "006208"

# check market is open
def isMarketOpen():
    taiwanTimeZone = pytz.timezone('Asia/Taipei')
    now = datetime.now(taiwanTimeZone)
    marketOpen = dtTime(9, 0, 0)
    marketClose = dtTime(13, 30, 0)
    return now.weekday() < 5 and marketOpen <= now.time() <= marketClose


# get ETF historical data
def getStockData():
    stock = yf.Ticker(f"{TARGET_ETF}.TW")
    df = stock.history(period='1mo')
    return df


# 計算 K 值（隨機指數）
def calculateStochasticK(df, period=14):
    df["Low"] = df["Low"].rolling(window=period).min()
    df["High"] = df["High"].rolling(window=period).max()
    df["%K"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"]) * 100
    return df


# 發送 LINE 訊息
def sendLineMessage(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("通知發送成功")
    else:
        print(f"通知發送失敗: {response.status_code}", response.text)

# 獲取最新的收盤價
def getLatestPrice():
    try:
        ticker = yf.Ticker(f"{TARGET_ETF}.TW") 
        df = ticker.history(period='1d')  # 抓取當天的數據
        if not df.empty:
            return df['Close'].iloc[-1]  # 獲取最新的收盤價
        else:
            print("無法獲取數據，可能是市場未開盤或數據來源有問題")
            return None
    except Exception as e:
        print(f"發生錯誤：{e}")
        return None
    

def monitorETF():
    if not isMarketOpen():
        return
    df = calculateStochasticK(getStockData())
    latest_k = df["%K"].iloc[-1]  
    latest_price = getLatestPrice()
    if latest_k < 20:  
        sendLineMessage(f"⚠️ {TARGET_ETF} K值跌破 20，目前為 {latest_k:.2f}，最新收盤價為：{latest_price:.2f} 元<，請關注市場！")
    else:
        sendLineMessage(f"⚠️ {TARGET_ETF} K值未跌破20，最新收盤價為：{latest_price:.2f} 元，不發送通知")

# 主程式
if __name__ == "__main__":
    monitorETF()
    
