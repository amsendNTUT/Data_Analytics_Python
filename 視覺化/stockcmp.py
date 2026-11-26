import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# --- 1. 自動路徑修正 (解決「空的」最主要原因) ---
# 獲取目前腳本所在的目錄 (視覺化)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 獲取專案根目錄 (期末專題第六組)
base_dir = os.path.dirname(current_dir)
# 設定真正的 data 和 graph 路徑
data_dir = os.path.join(base_dir, 'data')
save_dir = os.path.join(base_dir, 'graph')

# 確保儲存資料夾存在
os.makedirs(save_dir, exist_ok=True)

# 指向正確的 CSV 路徑
us_index_file = os.path.join(data_dir, "US_Tech_Price_Index.csv")
tw_files = {
    '2317': os.path.join(data_dir, "2317.TW_data.csv"),
    '2330': os.path.join(data_dir, "2330.TW_data.csv"),
    '2382': os.path.join(data_dir, "2382.TW_data.csv"),
    '2454': os.path.join(data_dir, "2454.TW_data.csv"),
    '3231': os.path.join(data_dir, "3231.TW_data.csv")
}

# --- 2. 讀取資料並檢查是否為空 ---
try:
    us_df = pd.read_csv(us_index_file, index_col=0, parse_dates=True)
    if us_df.empty:
        print(f"警告：{us_index_file} 是空的！")
except FileNotFoundError:
    print(f"錯誤：找不到美股指數檔案，請先執行 US_tech_index.py")
    exit()

def load_tw_data(filename):
    if not os.path.exists(filename):
        print(f"找不到檔案: {filename}")
        return None
    try:
        df = pd.read_csv(filename, dtype=str)
        if 'Price' in df.columns:
            df = df[~df['Price'].isin(['Ticker', 'Date'])]
            df = df.rename(columns={'Price': 'Date'})
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')
            return pd.to_numeric(df['Close'], errors='coerce').dropna()
    except Exception as e:
        print(f"讀取 {filename} 出錯: {e}")
    return None

tw_data = {code: load_tw_data(f) for code, f in tw_files.items()}

# --- 3. 畫圖與日期對齊 ---
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# 自動抓取資料中重疊的時間範圍，避免畫出空白圖
# 如果手動設定 2021-2026 但資料只有到 2024，後面就會是空的
all_dates = us_df.index
start_date = all_dates.min()
end_date = all_dates.max()

with plt.style.context('dark_background'):
    fig, axes = plt.subplots(5, 1, figsize=(14, 25), facecolor='black')
    name_map = {'2317': '鴻海', '2330': '台積電', '2382': '廣達', '2454': '聯發科', '3231': '緯創'}

    for i, (code, ax1) in enumerate(zip(tw_files.keys(), axes)):
        if tw_data[code] is None or tw_data[code].empty:
            ax1.text(0.5, 0.5, f"{code} 資料讀取失敗", ha='center', color='red')
            continue

        # 繪製美股
        us_p = us_df['US_Tech_Price_Index'][start_date:end_date]
        ax1.plot(us_p.index, us_p, color='#FF3333', alpha=0.7, label='美股科技指數')
        ax1.set_ylabel('美股指數', color='#FF3333')

        # 繪製台股
        ax2 = ax1.twinx()
        tw_p = tw_data[code][start_date:end_date]
        ax2.plot(tw_p.index, tw_p, color='#00FF00', alpha=0.7, label=name_map[code])
        ax2.set_ylabel(f'{name_map[code]} 股價', color='#00FF00')

        ax1.set_title(f'{name_map[code]} vs 美股指數 ({start_date.date()} ~ {end_date.date()})')
        ax1.grid(alpha=0.2)

    plt.tight_layout()
    save_path = os.path.join(save_dir, 'stockcmp.png')
    plt.savefig(save_path)
    print(f"圖表已儲存至: {save_path}")
    plt.show()
