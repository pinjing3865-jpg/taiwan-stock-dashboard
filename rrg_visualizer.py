import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import urllib.request
import os

# 1. 終極防擋下載：偽裝成正常瀏覽器，並改用最穩定的 Google 官方思源黑體
font_url = 'https://github.com/google/fonts/raw/main/ofl/notosanstc/NotoSansTC-Regular.ttf'
font_path = 'NotoSansTC-Regular.ttf'

if not os.path.exists(font_path):
    try:
        # 加入 headers 偽裝，避免被雲端伺服器阻擋下載
        req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(font_path, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        pass

# 2. 強制載入字型
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.sans-serif'] = ['Noto Sans TC']
    my_font = fm.FontProperties(fname=font_path)
else:
    plt.rcParams['font.sans-serif'] = ['sans-serif']
    my_font = fm.FontProperties()

plt.rcParams['axes.unicode_minus'] = False

def plot_rrg_chart(rrg_all_history):
    """繪製 RRG 動能旋轉圖 (終極字型掛載版)"""
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='black')
    ax.set_facecolor('black')
    
    # 畫出象限格線
    ax.axvline(100, color='gray', linestyle='--', alpha=0.7)
    ax.axhline(100, color='gray', linestyle='--', alpha=0.7)
    
    # 象限名稱標示
    ax.text(100.5, 101, '第一象限 [領先]', color='gray', fontproperties=my_font, size=12, alpha=0.6)
    ax.text(98.5, 101, '第二象限 [轉強]', color='gray', fontproperties=my_font, size=12, alpha=0.6)
    ax.text(98.5, 99, '第三象限 [落後]', color='gray', fontproperties=my_font, size=12, alpha=0.6)
    ax.text(100.5, 99, '第四象限 [轉弱]', color='gray', fontproperties=my_font, size=12, alpha=0.6)
    
    drawn_count = 0
    if rrg_all_history:
        for sector_name, df in rrg_all_history.items():
            if df is None or df.empty or 'RS-Ratio' not in df.columns or 'RS-Momentum' not in df.columns:
                continue
                
            x = df['RS-Ratio'].values
            y = df['RS-Momentum'].values
            
            if len(x) == 0 or len(y) == 0:
                continue
                
            drawn_count += 1
            latest_quadrant = df.iloc[-1]['Quadrant'] if 'Quadrant' in df.columns else ""
            
            # 依據你的指示：紅是漲(強勢)、白是跌(弱勢)
            is_strong = "第一象限" in latest_quadrant or "第二象限" in latest_quadrant
            line_color = 'red' if is_strong else 'white'
            
            # 畫軌跡線與點
            ax.plot(x, y, color=line_color, alpha=0.7, linewidth=1.5)
            ax.scatter(x[:-1], y[:-1], color='white', alpha=0.4, s=25)
            ax.scatter(x[-1], y[-1], color='red' if is_strong else 'white', s=80, zorder=5)
            
            # 標示產業名稱
            ax.text(x[-1] + 0.1, y[-1] + 0.1, sector_name, color='red' if is_strong else 'white', fontproperties=my_font, size=10, weight='bold')

    if drawn_count == 0:
        ax.text(100, 100, '目前尚無 RRG 資料可顯示', color='yellow', fontproperties=my_font, size=14, ha='center', weight='bold')

    # 標題與軸標籤
    ax.set_title('RRG 產業動能旋轉圖', color='white', fontproperties=my_font, size=15, pad=15)
    ax.set_xlabel('RS-Ratio (相對強弱)', color='white', fontproperties=my_font, size=12)
    ax.set_ylabel('RS-Momentum (相對動能)', color='white', fontproperties=my_font, size=12)
    
    ax.tick_params(colors='white', labelsize=10)
    for spine in ax.spines.values():
        spine.set_edgecolor('gray')
        
    plt.tight_layout()
    return fig