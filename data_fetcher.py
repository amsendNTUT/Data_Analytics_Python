import yfinance as yf
import pandas as pd
import os
import time

def fetch_stock_data(ticker, period="5y", interval="1d", max_retries=3):
    """
    從 yfinance 下載單一時間框架 (日線) 的股票數據，並包含重試機制。
    """
    
    for attempt in range(max_retries):
        print(f"正在下載 {ticker} 的 日線數據 (嘗試 {attempt + 1}/{max_retries})...")
        
        try:
            # 下載日線數據 (5年, 1天間隔)
            data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
            
            if data.empty or 'Close' not in data.columns:
                if attempt == max_retries - 1:
                    print(f" 警告：{ticker} 的數據在 {max_retries} 次嘗試後仍無效。")
                
            else:
                print(f"{ticker} 的數據下載成功。")
                return data
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"警告：{ticker} 的數據在 {max_retries} 次嘗試後遇到異常: {e}")
        
        if attempt < max_retries - 1:
            time.sleep(5) 
            
    return None


if __name__ == "__main__":
    # Apple、Microsoft、Corporation Alphabet、NVDIA、Amazon、台積電、廣達、緯創、鴻海、聯發科、比特幣、以太幣
    tickers = ["AAPL", "MSFT", "GOOG", "NVDA", "AMZN", "2330.TW", "2382.TW", "3231.TW", "2317.TW", "2454.TW", "BTC-USD", "ETH-USD"]
    folder = "data"
    os.makedirs(folder, exist_ok=True)

    print("--- 開始【單一時間框架】股票數據下載 ---")
    for ticker in tickers:
        df = fetch_stock_data(ticker)
        
        if df is not None and not df.empty:
            file_path = os.path.join(folder, f"{ticker}_data.csv")
            # 儲存為 {ticker}_data.csv
            df.to_csv(file_path)
            print(f"已存 {file_path}")
    
    
    print("--- 所有股票資料已下載完成 ---")
    
    
