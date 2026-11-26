import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# 設定中文顯示
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 1. 自動路徑修正 (關鍵改動) ---
# 獲取目前腳本所在目錄 (視覺化)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 獲取專案根目錄 (期末專題第六組)
base_dir = os.path.dirname(current_dir)
# 設定真正的 data 和 graph 路徑
data_dir = os.path.join(base_dir, 'data')
save_dir = os.path.join(base_dir, 'graph')

# 確保 graph 資料夾存在
os.makedirs(save_dir, exist_ok=True)

# 股票名稱對應表
name_map = {
    '2317': '鴻海',
    '2330': '台積電',
    '2382': '廣達',
    '2454': '聯發科',
    '3231': '緯創'
}

# 指向正確的檔案位置
us_index_file = os.path.join(data_dir, 'US_Tech_Price_Index.csv') 
tw_files = {
    '2317': os.path.join(data_dir, '2317.TW_data.csv'),
    '2330': os.path.join(data_dir, '2330.TW_data.csv'),
    '2382': os.path.join(data_dir, '2382.TW_data.csv'),
    '2454': os.path.join(data_dir, '2454.TW_data.csv'),
    '3231': os.path.join(data_dir, '3231.TW_data.csv')
}

# --- 2. 讀取資料 ---
try:
    us_df = pd.read_csv(us_index_file, index_col=0, parse_dates=True)
    us_return = us_df['US_Tech_Return']
except FileNotFoundError:
    print(f"錯誤：找不到檔案 {us_index_file}，請先跑完相關性分析流程。")
    exit()

def load_tw_data(filename):
    try:
        if not os.path.exists(filename): return None
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

tw_data = {code: load_tw_data(f) for code, f in tw_files.items()}
tw_df = pd.DataFrame(tw_data)

# --- 3. 時差調整與篩選 ---
merged_df = tw_df.copy()
merged_df['US_Index'] = us_return
for code in tw_files.keys():
    merged_df[code] = merged_df[code].shift(-1)
merged_df = merged_df.dropna()

bad_days = merged_df[merged_df['US_Index'] < 0] 

# --- 4. 視覺化 ---
tw_stocks = [code for code in name_map.keys()]
tw_stocks_names = [name_map[code] for code in tw_stocks]

plt.figure(figsize=(10, 6))
# 畫箱型圖
bad_days[tw_stocks].boxplot( 
    patch_artist=True, 
    medianprops=dict(color='black', linewidth=2),
    boxprops=dict(linewidth=1.5),
    whiskerprops=dict(linewidth=1.5),
    capprops=dict(linewidth=1.5),
    showfliers=False) 

plt.axhline(0, color='gray', linestyle='dashed', alpha=0.8)
plt.title('TW Stock Returns When US Market Declines', fontsize=13)
plt.ylabel('Next-Day Return')
plt.xlabel('Taiwan Stocks')
plt.xticks(range(1, len(tw_stocks_names) + 1), tw_stocks_names, fontsize=11)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

# --- 5. 正確路徑儲存 ---
save_path = os.path.join(save_dir, 'TW_Returns_when_fall.png')
plt.savefig(save_path)
print(f"圖表已成功儲存至: {save_path}")

plt.show() 
plt.close('all')
