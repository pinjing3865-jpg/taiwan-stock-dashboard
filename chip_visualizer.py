import plotly.graph_objects as go

def plot_chip_rotation_chart(df_data, title="大戶籌碼輪動圖"):
    fig = go.Figure()

    # 十字象限基準線 (以投顧報告的 70% 和 20% 為界)
    fig.add_hline(y=20, line_dash="dash", line_color="#888888", line_width=1.5, opacity=0.8)
    fig.add_vline(x=70, line_dash="dash", line_color="#888888", line_width=1.5, opacity=0.8)

    # 四象限背景標示文字
    fig.add_annotation(x=0.95, y=0.95, xref="paper", yref="paper", text="🔥 領先區 [強勢]", showarrow=False, font=dict(color="#FF5252", size=20), opacity=0.35)
    fig.add_annotation(x=0.05, y=0.95, xref="paper", yref="paper", text="🚀 改善區 [潛力]", showarrow=False, font=dict(color="#448AFF", size=20), opacity=0.35)
    fig.add_annotation(x=0.05, y=0.05, xref="paper", yref="paper", text="💤 落後區 [觀望]", showarrow=False, font=dict(color="#B0BEC5", size=20), opacity=0.35)
    fig.add_annotation(x=0.95, y=0.05, xref="paper", yref="paper", text="⚠️ 弱化區 [退潮]", showarrow=False, font=dict(color="#FFD740", size=20), opacity=0.35)

    # 繪製資料點
    for idx, row in df_data.iterrows():
        x_val = row['buy_sell_ratio']
        y_val = row['net_diff_ratio']
        name = row['name']
        code = row['code']

        # 根據所在象限決定顏色
        if x_val >= 70 and y_val >= 20:
            color = "#FF5252" # 領先區 (紅)
        elif x_val < 70 and y_val >= 20:
            color = "#448AFF" # 改善區 (藍)
        elif x_val >= 70 and y_val < 20:
            color = "#FFD740" # 弱化區 (橘)
        else:
            color = "#B0BEC5" # 落後區 (灰)

        label_text = f"<b>{code} {name}</b>"
        text_pos = "bottom right" if x_val < 85 else "bottom left"

        fig.add_trace(go.Scatter(
            x=[x_val], y=[y_val],
            mode='markers+text',
            text=[label_text],
            textposition=text_pos,
            marker=dict(color=color, size=14, line=dict(color='white', width=1.5)),
            name=name,
            showlegend=False,
            textfont=dict(color='white', size=13),
            hovertemplate=f"<b>{name} ({code})</b><br>大戶買賣比: %{{x:.2f}}%<br>大戶差比: %{{y:.2f}}%<extra></extra>"
        ))

    # 深色主題版面配置
    fig.update_layout(
        template="plotly_dark",
        title=title,
        title_font=dict(color='white', size=20),
        xaxis_title="大戶買賣比 (主力參與程度) %",
        yaxis_title="大戶差比 (%)",
        xaxis=dict(range=[40, 100], zeroline=False, showgrid=True, gridcolor='#333333', color='white'),
        yaxis=dict(range=[-40, 60], zeroline=False, showgrid=True, gridcolor='#333333', color='white'),
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#0a0a0a',
        margin=dict(l=40, r=40, t=60, b=40),
        height=600,
        hovermode="closest"
    )
    return fig

# ==========================================
# 🚀 以下為新增的 XQ 定義籌碼計算與繪圖專用函式（不影響舊功能）
# ==========================================

import plotly.graph_objects as go
import pandas as pd

def calculate_xq_chip_metrics(df_ticks, threshold=3000000):
    """
    根據 XQ 最新定義計算單日大戶買賣比與大戶差比
    """
    results = []
    
    if df_ticks.empty:
        return pd.DataFrame(columns=['code', 'name', 'buy_sell_ratio', 'net_diff_ratio', 'total_amount'])

    for code, group in df_ticks.groupby('code'):
        name = group['name'].iloc[0] if 'name' in group.columns else str(code)
        
        # 篩選大戶單 (預設 300 萬以上)
        big_df = group[group['amount'] >= threshold]
        
        buy_big = big_df[big_df['action'] == 'B']['amount'].sum() if not big_df.empty else 0
        sell_big = big_df[big_df['action'] == 'S']['amount'].sum() if not big_df.empty else 0
        total_turnover = group['amount'].sum()
        
        # 1. 大戶買賣比 (X軸)
        if (buy_big + sell_big) > 0:
            buy_sell_ratio = (buy_big / (buy_big + sell_big)) * 100
        else:
            buy_sell_ratio = 50.0  
            
        # 2. 大戶差比 (Y軸)
        if total_turnover > 0:
            net_diff_ratio = ((buy_big - sell_big) / total_turnover) * 100
        else:
            net_diff_ratio = 0.0
            
        results.append({
            'code': str(code),
            'name': str(name),
            'buy_sell_ratio': round(buy_sell_ratio, 2),
            'net_diff_ratio': round(net_diff_ratio, 2),
            'total_amount': total_turnover
        })
        
    return pd.DataFrame(results)


def plot_xq_chip_rotation_chart(df_metrics, title="大戶籌碼熱門股輪動圖 (按 XQ 最新定義)"):
    fig = go.Figure()
    
    if df_metrics.empty:
        fig.update_layout(title="尚無籌碼數據", template="plotly_dark")
        return fig

    # 1. 專業黑底背景色塊 (將原本的淺色改為深色，並保持極低透明度)
    fig.add_shape(type="rect", x0=0, y0=20, x1=70, y1=40, fillcolor="rgba(30, 30, 50, 0.5)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=70, y0=20, x1=100, y1=40, fillcolor="rgba(30, 50, 30, 0.5)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=0, y0=-40, x1=70, y1=20, fillcolor="rgba(50, 30, 30, 0.5)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=70, y0=-40, x1=100, y1=20, fillcolor="rgba(50, 40, 30, 0.5)", line=dict(width=0), layer="below")

    # 2. 分隔虛線 (改為淺灰色，在黑底上更清晰)
    fig.add_shape(type="line", x0=70, y0=-40, x1=70, y1=40, line=dict(color="rgba(200, 200, 200, 0.3)", width=1, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=20, x1=100, y1=20, line=dict(color="rgba(200, 200, 200, 0.3)", width=1, dash="dash"))

    # 3. 繪製個股散佈點 (改用亮色系配色，確保黑底上清晰易讀)
    fig.add_trace(go.Scatter(
        x=df_metrics['buy_sell_ratio'],
        y=df_metrics['net_diff_ratio'],
        mode='text+markers',
        text=df_metrics['code'] + " " + df_metrics['name'],
        textposition="top center",
        marker=dict(
            size=14,
            color=df_metrics['net_diff_ratio'],
            colorscale='Turbo', # 換成視覺效果更強烈的 Turbo
            showscale=True,
            colorbar=dict(title="大戶差比 (%)", tickfont=dict(color='white'))
        ),
        textfont=dict(color='white', size=12)
    ))

    # 4. 象限文字標籤 (調整顏色以符合黑底)
    fig.add_annotation(x=85, y=30, text="<b>領先區 [強勢主流]</b>", showarrow=False, font=dict(color="#00FF66", size=14))
    fig.add_annotation(x=35, y=30, text="<b>改善區 [潛力啟動]</b>", showarrow=False, font=dict(color="#00BFFF", size=14))
    fig.add_annotation(x=35, y=-30, text="<b>落後區 [弱勢觀望]</b>", showarrow=False, font=dict(color="#FF4500", size=14))
    fig.add_annotation(x=85, y=-30, text="<b>弱化區 [資金退潮]</b>", showarrow=False, font=dict(color="#FFD700", size=14))

    fig.update_layout(
        title=dict(text=title, font=dict(color='white')),
        xaxis=dict(range=[-5, 105], zeroline=False, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white')),
yaxis=dict(range=[-50, 60], zeroline=False, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white')),
        template="plotly_dark", # 強制設定深色主題
        paper_bgcolor='black',  # 背景設為純黑
        plot_bgcolor='black',   # 繪圖區設為純黑
        height=650,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    return fig

def plot_xq_chip_rotation_with_trajectory(df_history, title="大戶籌碼熱門股輪動圖 (帶軌跡)"):
    import plotly.graph_objects as go
    fig = go.Figure()
    
    if df_history.empty:
        fig.update_layout(title="尚無籌碼數據", template="plotly_dark")
        return fig

    # 1. 專業黑底背景色塊
    fig.add_shape(type="rect", x0=0, y0=20, x1=70, y1=40, fillcolor="rgba(30, 30, 50, 0.5)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=70, y0=20, x1=100, y1=40, fillcolor="rgba(30, 50, 30, 0.5)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=0, y0=-40, x1=70, y1=20, fillcolor="rgba(50, 30, 30, 0.5)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=70, y0=-40, x1=100, y1=20, fillcolor="rgba(50, 40, 30, 0.5)", line=dict(width=0), layer="below")

    # 2. 分隔虛線
    fig.add_shape(type="line", x0=70, y0=-40, x1=70, y1=40, line=dict(color="rgba(200, 200, 200, 0.3)", width=1, dash="dash"))
    fig.add_shape(type="line", x0=0, y0=20, x1=100, y1=20, line=dict(color="rgba(200, 200, 200, 0.3)", width=1, dash="dash"))

    # 3. 按照股票代碼分組繪製軌跡
    import plotly.express as px
    # 使用包含 24 種高辨識度顏色的色票，避免股票太多顏色重複
    color_palette = px.colors.qualitative.Light24 
    
    for i, (code, group) in enumerate(df_history.groupby('code')):
        group = group.sort_values('date', ascending=True)
        name = group['name'].iloc[0]
        
        text_labels = [None] * (len(group) - 1) + [f"{code} {name}"]
        marker_sizes = [6] * (len(group) - 1) + [14]
        
        # 依照迴圈順序，給這檔股票分配一個專屬顏色
        stock_color = color_palette[i % len(color_palette)]
        
        fig.add_trace(go.Scatter(
            x=group['buy_sell_ratio'],
            y=group['net_diff_ratio'],
            mode='lines+markers+text',
            name=f"{code} {name}",
            text=text_labels,
            textposition="top center",
            # ✨ 關鍵修改：讓線條與圓點都綁定同一個專屬顏色！
            line=dict(width=2, color=stock_color),
            marker=dict(
                size=marker_sizes,
                color=stock_color,
                opacity=0.9
            ),
            textfont=dict(color='white', size=12),
            showlegend=False
        ))

    # ⚠️ 註解：原本下方的「簡化色條設定 (add_trace)」已經徹底刪除！
    # 因為圓點不再依照 Y 軸數值變色，所以右側的色條已經不需要了。

    # 4. 象限文字標籤
    fig.add_annotation(x=85, y=30, text="<b>領先區 [強勢主流]</b>", showarrow=False, font=dict(color="#00FF66", size=14))
    fig.add_annotation(x=35, y=30, text="<b>改善區 [潛力啟動]</b>", showarrow=False, font=dict(color="#00BFFF", size=14))
    fig.add_annotation(x=35, y=-30, text="<b>落後區 [弱勢觀望]</b>", showarrow=False, font=dict(color="#FF4500", size=14))
    fig.add_annotation(x=85, y=-30, text="<b>弱化區 [資金退潮]</b>", showarrow=False, font=dict(color="#FFD700", size=14))

    fig.update_layout(
        title=dict(text=title, font=dict(color='white')),
        xaxis=dict(
            range=[-5, 105], zeroline=False, gridcolor='rgba(255,255,255,0.1)', 
            tickfont=dict(color='white'), 
            title=dict(text="大戶買賣比 (%)", font=dict(color='white'))
        ),
        yaxis=dict(
            range=[-50, 60], zeroline=False, gridcolor='rgba(255,255,255,0.1)', 
            tickfont=dict(color='white'), 
            title=dict(text="大戶差比 (%)", font=dict(color='white'))
        ),
        paper_bgcolor='black',  
        plot_bgcolor='black',   
        height=650,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    return fig