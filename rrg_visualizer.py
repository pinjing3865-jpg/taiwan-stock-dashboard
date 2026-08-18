import matplotlib.pyplot as plt
import numpy as np

def plot_rrg_chart(rrg_all_history):
    # 建立畫布
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    
    # 畫出十字象限基準線 (以 100 為中心)
    ax.axhline(100, color='#555555', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.axvline(100, color='#555555', linestyle='--', linewidth=1.5, alpha=0.7)
    
    # 四象限背景標示文字
    ax.text(102, 102.5, "🔥 第一象限 [領先]", color='#FF5252', fontsize=11, fontweight='bold', alpha=0.6)
    ax.text(97.5, 102.5, "🚀 第二象限 [轉強]", color='#448AFF', fontsize=11, fontweight='bold', alpha=0.6)
    ax.text(97.5, 97.2, "💤 第三象限 [落後]", color='#B0BEC5', fontsize=11, fontweight='bold', alpha=0.6)
    ax.text(102, 97.2, "⚠️ 第四象限 [轉弱]", color='#FFD740', fontsize=11, fontweight='bold', alpha=0.6)

    colors = ['#FF5252', '#448AFF', '#00E676', '#FFD740', '#E040FB', '#00B0FF', '#FF6E40', '#69F0AE']
    
    for idx, (sector_name, df_result) in enumerate(rrg_all_history.items()):
        if df_result is None or df_result.empty:
            continue
            
        color = colors[idx % len(colors)]
        
        x = df_result['RS-Ratio'].values
        y = df_result['RS-Momentum'].values
        
        # 畫出平滑的動能旋轉軌跡線
        ax.plot(x, y, color=color, linewidth=2, alpha=0.7, label=sector_name)
        ax.scatter(x, color=color, s=20, alpha=0.5)
        
        # 取得最新一個交易日的數值來判定狀態
        last_x = x[-1]
        last_y = y[-1]
        
        # 🌟 數值動能警示判定邏輯
        status_tag = ""
        if last_x > 101.5 and last_y > 101.5:
            status_tag = " [🔥過熱]"
        elif last_y > 101 and last_x < 100:
            status_tag = " [🚀強勢翻多]"
        elif last_x > 101 and last_y < 100:
            status_tag = " [⚠️降溫回檔]"
        else:
            status_tag = " [穩定]"
        
        # 標出最新位置實心圓點
        ax.scatter(last_x, last_y, color=color, s=120, zorder=5, edgecolor='white', linewidth=1.5)
        
        # 在圖表上直接印出帶有狀態標籤的族群名稱
        label_text = f"  {sector_name}{status_tag}"
        ax.annotate(label_text, (last_x, last_y), color='white', fontsize=10, fontweight='bold',
                    va='center', ha='left', bbox=dict(boxstyle='round,pad=0.2', facecolor='#1f1f1f', edgecolor=color, alpha=0.85))

    ax.set_title("RRG 產業動能旋轉圖 (內建即時過熱與轉強提示)", color='white', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("RS-Ratio (相對強勢)", color='white', fontsize=11)
    ax.set_ylabel("RS-Momentum (相對動能)", color='white', fontsize=11)
    
    ax.tick_params(colors='white', labelsize=10)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')
        
    plt.tight_layout()
    return fig