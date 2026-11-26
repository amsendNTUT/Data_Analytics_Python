import matplotlib.pyplot as plt
import squarify
from matplotlib.colors import Normalize, LinearSegmentedColormap
import matplotlib
import numpy as np
import json
import os # 新增 os 模組處理路徑

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

# --- 修正路徑邏輯 ---
# 獲取當前腳本目錄 (視覺化)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 獲取根目錄 (期末專題第六組)
base_dir = os.path.dirname(current_dir)
# 設定 data 和 graph 路徑
data_path = os.path.join(base_dir, 'data', 'correlation_results.json')
save_dir = os.path.join(base_dir, 'graph')

# 確保儲存資料夾存在
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 股票名稱對應表
name_map = {
    '2317': '鴻海',
    '2330': '台積電',
    '2382': '廣達',
    '2454': '聯發科',
    '3231': '緯創'
}

# 讀取 JSON 檔案 (使用修正後的路徑)
try:
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"錯誤：找不到檔案 {data_path}，請確認是否已產生該檔案。")
    exit()

normal_corr_dict = data['all_days']
fall_corr_dict = data['bad_days']

# --- 後續繪圖邏輯保持不變 ---
names_base = [name_map[code] for code in name_map.keys()]
sizes_normal = [normal_corr_dict[code] for code in name_map.keys()]
sizes_fall = [fall_corr_dict[code] for code in name_map.keys()]

all_sizes = sizes_normal + sizes_fall
all_labels_plain = names_base + [f"{n}(跌)" for n in names_base]

combined = sorted(zip(all_sizes, all_labels_plain), reverse=True)
sorted_sizes, sorted_names = zip(*combined)

final_labels = [
    f"{name}\n{size * 100:.1f}%"
    for name, size in zip(sorted_names, sorted_sizes)
]

norm = Normalize(vmin=min(sorted_sizes) * 100, vmax=max(sorted_sizes) * 100)
base_cmap = matplotlib.colormaps['OrRd']
colors = base_cmap(np.linspace(0.3, 1.0, 256))
cmap = LinearSegmentedColormap.from_list('OrRd_truncated', colors)

fig, ax = plt.subplots(figsize=(15, 9))
squarify.plot(
    sizes=sorted_sizes,
    label=final_labels,
    color=[cmap(norm(size * 100)) for size in sorted_sizes],
    alpha=0.95, pad=False, ec='white', lw=2.5,
    text_kwargs={'weight': 'bold', 'color': 'white'},
    ax=ax
)
ax.invert_yaxis()

for i, text in enumerate(ax.texts):
    text.set_fontsize(12 + sorted_sizes[i] * 40)

sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.05, pad=0.08)
cbar.set_label('連動程度（%）', fontsize=14)
cbar.ax.invert_xaxis()

ax.set_title('美股指數與台股之相關性', fontsize=24, fontweight='bold', pad=25)
ax.axis('off')
plt.tight_layout()

# --- 修正儲存路徑 ---
save_path = os.path.join(save_dir, 'heatmap.png')
plt.savefig(save_path)
print(f"成功將熱力圖存入：{save_path}")

plt.show()
plt.close('all')
