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
    print("取得的原始數據：")
    print(df.tail(14))  # 輸出最近 14 天的數據，供檢查ｓ
    return df


# 計算 K 值（隨機指數）
def calculateStochasticK(df, period=14, smooth_k=1):
    if len(df) < period:
        print(f"數據不足，需至少 {period} 天，當前只有 {len(df)} 天")
        return None
    
    df["Low"] = df["Low"].rolling(window=period, min_periods=period).min()
    df["High"] = df["High"].rolling(window=period, min_periods=period).max()
    df["%K"] = (df["Close"] - df["Low"]) / (df["High"] - df["Low"]) * 100
    
    if smooth_k > 1:
        df["%K"] = df["%K"].rolling(window=smooth_k, min_periods=smooth_k).mean()
    
    df.dropna(inplace=True)
    print("計算後的數據（含 Low、High、%K）：")
    print(df[["Close", "Low", "High", "%K"]].tail(5))  # 輸出最後 5 天的計算結果
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
def getLatestPrice(df):
    if not df.empty:
        return df['Close'].iloc[-1]
    else:
        print("無法獲取最新價格，數據為空")
        return None
    

def monitorETF():
    if not isMarketOpen():
        return
    
    df = getStockData()
    if df is None or df.empty:
        print("無法獲取股票數據")
        return
    
    df = calculateStochasticK(df, period=14, smooth_k=1)  # 先用原始 %K，無平滑
    if df is None or df.empty:
        print("K 值計算失敗")
        return
    
    latest_k = df["%K"].iloc[-1]
    latest_price = getLatestPrice(df)
    print(f"最終計算出的 %K: {latest_k:.2f}")

    
    if latest_k < 20:  
        sendLineMessage(f"⚠️ {TARGET_ETF} K值跌破 20，目前為 {latest_k:.2f}，最新收盤價為：{latest_price:.2f} 元<，請關注市場！")
    else:
        print(f"K值未跌破20，最新收盤價為：{latest_price:.2f} 元，不發送通知")

# 主程式
if __name__ == "__main__":
    monitorETF()
    
