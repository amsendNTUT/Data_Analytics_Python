import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# --- 自動路徑修正 ---
# 獲取目前腳本所在目錄 (C:\...\相關性分析)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 獲取專案根目錄 (C:\...\期末專題第六組)
base_dir = os.path.dirname(current_dir)
# 設定真正的 data 資料夾路徑
data_dir = os.path.join(base_dir, 'data')

# 設定美股指數路徑
us_index_file = os.path.join(data_dir, 'US_Tech_Price_Index.csv')

# 台股資料路徑
tw_files = {
    '2317': os.path.join(data_dir, '2317.TW_data.csv'),
    '2330': os.path.join(data_dir, '2330.TW_data.csv'),
    '2382': os.path.join(data_dir, '2382.TW_data.csv'),
    '2454': os.path.join(data_dir, '2454.TW_data.csv'),
    '3231': os.path.join(data_dir, '3231.TW_data.csv')
}

# --- 步驟 A: 讀取美股指數 ---
if not os.path.exists(us_index_file):
    print(f"錯誤：找不到檔案 {us_index_file}。請先執行 US_tech_index.py 產生該檔案。")
    exit()

us_df = pd.read_csv(us_index_file, index_col=0, parse_dates=True)
us_return = us_df['US_Tech_Return']


# --- 步驟 B: 讀取台股 (函數維持不變) ---
def load_tw_data(filename):
    try:
        df = pd.read_csv(filename, dtype=str)
        if 'Price' in df.columns:
            df = df[~df['Price'].isin(['Ticker', 'Date'])]
            df = df.rename(columns={'Price': 'Date'})
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            return pd.to_numeric(df['Close']).pct_change()
        return None
    except:
        return None


tw_data = {}
for code, f in tw_files.items():
    if os.path.exists(f):
        tw_data[code] = load_tw_data(f)

# (中間的運算邏輯 merged_df, shift, corr 維持不變...)
tw_df = pd.DataFrame(tw_data)
merged_df = tw_df.copy()
merged_df['US_Index'] = us_return
for code in tw_files.keys():
    merged_df[code] = merged_df[code].shift(-1)
merged_df = merged_df.dropna()

bad_days = merged_df[merged_df['US_Index'] < 0]
all_days = merged_df
b_correlation = bad_days.corr()['US_Index']
a_correlation = all_days.corr()['US_Index']

# --- 步驟 C: 執行儲存 ---
results_to_save = {
    "desc": "美股台股相關性分析結果",
    "bad_days": b_correlation.drop('US_Index').to_dict(),
    "all_days": a_correlation.drop('US_Index').to_dict()
}

# 使用動態路徑儲存
save_path = os.path.join(data_dir, 'correlation_results.json')

with open(save_path, 'w', encoding='utf-8') as f:
    json.dump(results_to_save, f, indent=4, ensure_ascii=False)

print(f"成功將字典存入：{save_path}")