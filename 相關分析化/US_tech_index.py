import pandas as pd
import os


current_script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_script_dir)
data_dir = os.path.join(base_dir, 'data')

files = {
    'NVDA': os.path.join(data_dir, 'NVDA_data.csv'),
    'AAPL': os.path.join(data_dir, 'AAPL_data.csv'),
    'AMZN': os.path.join(data_dir, 'AMZN_data.csv'),
    'GOOG': os.path.join(data_dir, 'GOOG_data.csv'),
    'MSFT': os.path.join(data_dir, 'MSFT_data.csv')
}

def load_clean_data(filename):
    try:
        # 檢查檔案是否存在
        if not os.path.exists(filename):
            return None

        df = pd.read_csv(filename, dtype=str)

        if 'Price' in df.columns:
            df = df[~df['Price'].isin(['Ticker', 'Date'])]
            df = df.rename(columns={'Price': 'Date'})
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            # 轉換為數值，並處理掉可能出現的空值
            return pd.to_numeric(df['Close'], errors='coerce')
        else:
            return None
    except:
        return None


# --- 主程式 ---
data_dict = {}

for stock_name, file_path in files.items():
    clean_data = load_clean_data(file_path)
    if clean_data is not None:
        data_dict[stock_name] = clean_data

# 建立表格並對齊日期
df_all = pd.DataFrame(data_dict).dropna()

# 檢查是否真的有抓到資料，避免 iloc 報錯
if df_all.empty:
    print("錯誤：讀取的資料為空，請檢查 CSV 檔案內容或路徑。")
else:
    # 1. 算出每天漲跌幅
    returns = df_all.pct_change()

    # 2. 算出 5 支股票的平均漲跌幅
    us_tech_return = returns.mean(axis=1)

    # 3. 計算指數價格
    # 先算出累計乘積
    us_tech_price_index = (1 + us_tech_return).cumprod() * 100

    # 修正：直接對 Series 的第一個有效值賦值，或使用 concat 補上基期
    # 這裡建議直接確保第一筆有效資料存在
    if not us_tech_price_index.empty:
        # 找到第一個非 NaN 的位置並設定為 100
        first_valid_idx = us_tech_price_index.first_valid_index()
        us_tech_price_index.loc[first_valid_idx] = 100

    output = pd.DataFrame({
        'US_Tech_Return': us_tech_return,
        'US_Tech_Price_Index': us_tech_price_index
    })

    # 儲存到正確的 data 資料夾位置
    output_save_path = os.path.join(data_dir, 'US_Tech_Price_Index.csv')
    output.to_csv(output_save_path)
    print(f"成功！檔案已儲存至: {output_save_path}")
