import plotly.graph_objects as go
import numpy as np

def plot_rrg_chart(rrg_all_history, *args, **kwargs):
    fig = go.Figure()
    
    # 動態計算最大偏移量，確保 (100, 100) 永遠在圖表正中央
    max_dev = 2 
    for df_result in rrg_all_history.values():
        if df_result is not None and not df_result.empty:
            dev_x = max(abs(df_result['RS-Ratio'].max() - 100), abs(df_result['RS-Ratio'].min() - 100))
            dev_y = max(abs(df_result['RS-Momentum'].max() - 100), abs(df_result['RS-Momentum'].min() - 100))
            max_dev = max(max_dev, dev_x, dev_y)
    
    axis_min = 100 - max_dev - 1
    axis_max = 100 + max_dev + 1

    # 畫出十字象限基準線 (以 100 為中心)，換成較明顯的亮灰色
    fig.add_hline(y=100, line_dash="dash", line_color="#888888", line_width=1.5, opacity=0.8)
    fig.add_vline(x=100, line_dash="dash", line_color="#888888", line_width=1.5, opacity=0.8)
    
    # 四象限背景標示文字
    fig.add_annotation(x=0.95, y=0.95, xref="paper", yref="paper", text="🔥 第一象限 [領先]", showarrow=False, font=dict(color="#FF5252", size=20, weight="bold"), opacity=0.35)
    fig.add_annotation(x=0.05, y=0.95, xref="paper", yref="paper", text="🚀 第二象限 [轉強]", showarrow=False, font=dict(color="#448AFF", size=20, weight="bold"), opacity=0.35)
    fig.add_annotation(x=0.05, y=0.05, xref="paper", yref="paper", text="💤 第三象限 [落後]", showarrow=False, font=dict(color="#B0BEC5", size=20, weight="bold"), opacity=0.35)
    fig.add_annotation(x=0.95, y=0.05, xref="paper", yref="paper", text="⚠️ 第四象限 [轉弱]", showarrow=False, font=dict(color="#FFD740", size=20, weight="bold"), opacity=0.35)

    colors = ['#FF5252', '#448AFF', '#00E676', '#FFD740', '#E040FB', '#00B0FF', '#FF6E40', '#69F0AE']
    
    for idx, (sector_name, df_result) in enumerate(rrg_all_history.items()):
        if df_result is None or df_result.empty:
            continue
            
        color = colors[idx % len(colors)]
        
        x = df_result['RS-Ratio'].values
        y = df_result['RS-Momentum'].values
        
        # 畫出平滑的動能旋轉軌跡線
        fig.add_trace(go.Scatter(
            x=x, y=y, mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(color=color, size=6, opacity=0.7),
            name=sector_name,
            showlegend=True,  # 顯示圖例
            hoverinfo='skip'
        ))
        
        last_x = x[-1]
        last_y = y[-1]
        
        status_tag = ""
        if last_x > 101.5 and last_y > 101.5:
            status_tag = " [🔥過熱]"
        elif last_y > 101 and last_x < 100:
            status_tag = " [🚀轉強]"
        elif last_x > 101 and last_y < 100:
            status_tag = " [⚠️降溫]"
        else:
            status_tag = " [穩定]"
        
        # 🌟 最新位置強制設為純白字，配黑底最清楚
        label_text = f"<b>{sector_name}</b>{status_tag}"
        fig.add_trace(go.Scatter(
            x=[last_x], y=[last_y], mode='markers+text',
            text=[label_text], textposition="middle right",
            marker=dict(color=color, size=15, line=dict(color='white', width=1.5)),
            name=sector_name,
            showlegend=False,
            textfont=dict(color='white', size=14),
            hovertemplate=f"<b>{sector_name}</b><br>RS-Ratio: %{{x:.2f}}<br>RS-Momentum: %{{y:.2f}}<extra></extra>"
        ))

    # 🌟 強制設定深色主題 (Dark Theme) 與超大畫布 (Height: 800)
    fig.update_layout(
        template="plotly_dark",
        title="RRG 產業動能旋轉圖 (內建即時過熱與轉強提示)",
        title_font=dict(color='white', size=20, weight='bold'),
        xaxis_title="RS-Ratio (相對強勢)",
        yaxis_title="RS-Momentum (相對動能)",
        xaxis=dict(range=[axis_min, axis_max], zeroline=False, showgrid=True, gridcolor='#333333', color='white'),
        yaxis=dict(range=[axis_min, axis_max], zeroline=False, showgrid=True, gridcolor='#333333', color='white'),
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#0a0a0a',
        legend=dict(font=dict(color="white")),
        margin=dict(l=40, r=120, t=60, b=40),
        height=800,  # <--- 這裡把高度拉大，圖表就會跟著變大！
        hovermode="closest"
    )
    
    return fig