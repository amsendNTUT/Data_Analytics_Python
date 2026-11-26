import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# 設定字體與負號顯示
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 動態路徑處理：獲取當前腳本所在目錄的上一層（專案根目錄）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'correlation_results.json')
SAVE_DIR = os.path.join(BASE_DIR, 'graph')

# 確保 graph 資料夾存在，否則 savefig 會報錯
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 股票名稱對應表
name_map = {
    '2317': '鴻海',
    '2330': '台積電',
    '2382': '廣達',
    '2454': '聯發科',
    '3231': '緯創'
}

# 2. 讀取 JSON 檔案
try:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"錯誤：找不到檔案 {DATA_PATH}，請確認檔案是否已建立。")
    exit()

#-------------- 視覺化 ----------------
AllDay_corr = data['all_days']
colors = ['green' if v >= 0 else 'red' for v in AllDay_corr.values()]

plt.figure(figsize=(10, 6))
# 這裡使用 .get(key, key) 防止 json 內有 name_map 沒定義的代碼
bars = plt.bar([name_map.get(key, key) for key in AllDay_corr.keys()], AllDay_corr.values(), color=colors)

# 加上數值標籤
for bar in bars:
    height = bar.get_height()
    center = bar.get_x() + bar.get_width() / 2
    plt.text(
        center,
        height,
        f'{height:.2f}',
        ha='center',
        va='bottom' if height >= 0 else 'top'
    )

plt.axhline(0, color='black', linewidth=1)
plt.title('Correlation with US Tech Index', fontsize=13)
plt.ylabel('Correlation Coefficient')
plt.xlabel('Taiwan Stocks')
plt.grid(axis='y', alpha=0.3)

# 修正圖例：確保顏色對應正確
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], color='green', lw=4, label='Positive Correlation'),
                   Line2D([0], [0], color='red', lw=4, label='Negative Correlation')]
plt.legend(handles=legend_elements, loc='upper right')

plt.tight_layout()

# 3. 儲存為 PNG 格式
save_path = os.path.join(SAVE_DIR, 'Correlation_with_US_Tech_Index.png')
plt.savefig(save_path)
print(f"圖表已儲存至: {save_path}")

plt.show() 
plt.close('all')
