import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 匯入分析模組
from rrg_calculator import calculate_rrg_quadrants
from mops_revenue_crawler import fetch_latest_monthly_revenue
from rrg_visualizer import plot_rrg_chart
from twse_market_core import build_history_market_data, generate_sector_dataframes

# ==========================================
# 網頁基本設定
# ==========================================
st.set_page_config(page_title="台股全市場完整成分股戰情室", layout="wide", page_icon="📈")

# ==========================================
# 完整字典：同時收錄「傳統細產業」與「熱門概念股」
# ==========================================
my_custom_sectors = {
    # --- 💡 熱門題材與概念股 ---
    'CPO矽光子概念股': ['2330', '3363', '3163', '4979', '3450', '3081', '6442', '4908', '3711', '2455'],
    'AI伺服器概念股': ['2382', '2357', '3231', '6669', '2376', '3017', '2353', '2383', '3665'],
    'CoWoS先進封裝概念股': ['2330', '3711', '6259', '3131', '6187', '3583', '3680', '6525', '2449'],
    '低軌衛星概念股': ['2314', '3491', '3450', '6285', '2345', '3704', '5388', '6278','2313'],
    '蘋概股精選': ['2330', '3008', '4938', '2474', '2313', '4958', '3406', '6269'],
    '重電與綠能概念股': ['1503', '1519', '1513', '1514', '1504', '9958', '3708', '6806', '6505'],

    # --- 📊 傳統細產業 ---
    'PCB-製造': ['2368', '3037', '2313', '4958', '6274', '5381', '3044', '5469', '6213', '8046', '6292', '5349'],
    'PCB-材料設備': ['6213', '8046', '3189', '5340', '4721', '6552', '4767', '1815'],
    '光學鏡片': ['3008', '3406', '3362', '3019', '3441', '3504', '3630', '4976', '6209'],
    '航運': ['2603', '2609', '2615', '2606', '2618', '2610', '2637', '2612', '5609', '2607', '2614'],
    '矽晶圓': ['6488', '3532', '5483', '6182', '2338', '3707'],
    '散熱模組': ['3324', '3017', '2421', '3013', '3653', '8996', '2427', '6230', '3338', '3483'],
    '電源供應器': ['2308', '2301', '6412', '6282', '8155', '2362', '3015', '6796', '5386'],
    '儀器設備工程': ['3131', '6187', '3583', '3680', '6139', '2467', '3556', '5536', '6196'],
    '電子零組件': ['2327', '3023', '3533', '2492', '6217', '3042', '6283', '8042', '4938'],
    '塑膠': ['1301', '1303', '1326', '1304', '1307', '1308', '1309', '1310', '1312', '1313', '1314', '1315'],
    '電機': ['1504', '1503', '1519', '1513', '1514', '1515', '1516', '1521', '1525', '1532', '1536'],
    'IC-製造': ['2330', '2303', '6770', '5347', '6525', '6531', '3707'],
    'LCD面板': ['2409', '3481', '3149', '6116'],
    '化學工業': ['1723', '4739', '1707', '1732', '1709', '1711', '1783', '4720', '4755'],
    '被動元件': ['2327', '2456', '3026', '6173', '2498', '5328', '2472', '3624', '8043', '6207'],
    '工業電腦': ['2395', '6114', '8114', '6166', '8050', '2397', '6225', '6414', '6531', '5255'],
    '鋼鐵': ['2002', '2014', '2027', '2031', '2049', '2006', '2009', '2012', '2015', '5007', '5009'],
    '電信服務': ['3045', '2412', '4904', '4906'],
    '營建': ['2504', '2520', '2548', '5522', '2501', '2505', '2511', '2515', '2527', '2537', '2542'],
    '二極體': ['5425', '2481', '8255', '2342', '4943'],
    'LED及光元件': ['3714', '2448', '3069', '4956', '3698', '2393'],
    '軟體-系統整合': ['2471', '6112', '3029', '2468', '6183', '2453'],
    '車用電子': ['3552', '3665', '2231', '1536', '2228', '2233'],
    '運動': ['9904', '9914', '9941', '9921', '8404', '9910'],
    '玻璃陶瓷': ['1802', '1806', '1809'],
    '光碟片': ['2323', '2406', '3064'],
    'LCD零件': ['3149', '4961', '8215', '3545', '4952'],
    '紙業': ['1904', '1905', '1907', '1906', '1909'],
    '控股公司': ['3702', '2915', '1402', '2903', '5907'],
    '汽車零組件': ['1522', '1319', '1536', '6279', '2227', '2231', '2236', '4557'],
    '水泥': ['1101', '1102', '1103', '1104'],
    '家居': ['8464', '9938', '5534', '8454', '8436'],
    '安全監控': ['3454', '3356', '8072', '3128', '2398'],
    '金融-證券': ['6005', '2834', '6024', '2855', '6016'],
    '變壓器與UPS': ['1519', '1503', '1513', '1514', '1504'],
    '軟體-其他': ['6111', '3546', '3293', '4994', '6183', '3083'],
    '綠能環保': ['9958', '3708', '6806', '8422', '6505', '8938'],
    '電池': ['3211', '4721', '6509', '5232', '6547'],
    '軟體-遊戲': ['3293', '6111', '4994', '3083', '5478', '3152'],
    '居家生活': ['9938', '2912', '5904', '8464', '9907'],
    '運動休閒': ['9904', '9914', '9921', '8404', '9910', '2929'],
    '筆記型電腦': ['2382', '3231', '2357', '2353', '2356', '2324', '4938'],
    '顯示器': ['2406', '2340', '4961', '3059', '2424', '3593'],
    '生技': ['4743', '6446', '6472', '1795', '4147', '4123', '4162', '4174', '6541'],
    '電子-其他': ['3376', '6278', '6223', '5371', '3067', '4931'],
    '低軌衛星': ['2314', '3491', '3450', '6285', '2345', '3704', '5388'],
    '連接元件': ['3533', '3023', '6281', '2406', '3501', '3040', '6191'],
    '紡織纖維': ['1476', '1402', '1455', '1477', '1409', '1410', '1414'],
    '航天軍工': ['2634', '8222', '1533', '4541', '4583', '5284', '8033'],
    'DRAM': ['2408', '2344', '3260', '8299', '2337', '8271'],
    '板卡': ['2376', '2377', '2465', '5386', '6111', '3540'],
    '金融-金控': ['2881', '2882', '2891', '2884', '2886', '2880', '2883'],
    '電腦周邊產品': ['2357', '2376', '2324', '3231', '2382', '2395', '3017'],
    'IC-設計': ['2454', '3034', '3035', '3661', '3443', '4966', '5269', '3529', '6643', '6533'],
    'IC-封測': ['2311', '3711', '6259', '8150', '2449', '3264', '6239', '8110'],
    'IC-通路': ['3704', '3036', '2459', '8112', '5434', '3010', '3105'],
    '網通設備': ['2345', '3596', '5388', '3380', '6285', '2419', '3234']
}

sector_categories = {
    "🔥 熱門主流題材": ['CPO矽光子概念股', 'AI伺服器概念股', 'CoWoS先進封裝概念股', '低軌衛星概念股', '蘋概股精選', '重電與綠能概念股'],
    "📊 半導體族群": ['IC-製造', 'IC-設計', 'IC-封測', 'IC-通路', '矽晶圓', 'DRAM', '二極體'],
    "🔌 電子零組件": ['PCB-製造', 'PCB-材料設備', '被動元件', '連接元件', '電子零組件', '散熱模組', '電源供應器', '變壓器與UPS', '電池', '儀器設備工程'],
    "🖥️ 電腦與軟體": ['筆記型電腦', '電腦周邊產品', '板卡', '工業電腦', '軟體-系統整合', '軟體-其他', '軟體-遊戲', '安全監控'],
    "📡 光電與網通": ['光學鏡片', 'LCD面板', 'LCD零件', 'LED及光元件', '顯示器', '光碟片', '網通設備', '低軌衛星'],
    "🚗 車用與軍工": ['車用電子', '汽車零組件', '航天軍工'],
    "🏗️ 傳統產業": ['航運', '鋼鐵', '塑膠', '電機', '化學工業', '營建', '水泥', '玻璃陶瓷', '紙業', '紡織纖維'],
    "💼 生技金融與其他": ['生技', '金融-證券', '金融-金控', '控股公司', '電信服務', '綠能環保', '運動', '運動休閒', '居家生活', '家居', '電子-其他']
}

@st.cache_data(ttl=300)
def get_pro_stock_data(ticker, interval_label):
    try:
        tf_map = {
            "日K (近半年)": ("1d", "6mo"),
            "週K (近2年)": ("1wk", "2y"),
            "60分K (近2個月)": ("60m", "60d"),
            "15分K (近1個月)": ("15m", "1mo")
        }
        inter, per = tf_map[interval_label]
        
        df = pd.DataFrame()
        for suffix in [".TW", ".TWO", ""]:
            try:
                stock = yf.Ticker(f"{ticker}{suffix}")
                df = stock.history(period=per, interval=inter)
                if not df.empty:
                    break
            except:
                continue
            
        if df.empty:
            return pd.DataFrame()

        df = df.reset_index()
        date_col = df.columns[0]
        df.rename(columns={date_col: 'Date'}, inplace=True)
        
        df['Date_str'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M') if inter in ['15m', '60m'] else df['Date'].dt.strftime('%Y-%m-%d')
        
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df = df[df['Volume'] > 0].copy()

        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()

        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        delta = df['Close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        rs = ema_up / ema_down
        df['RSI'] = 100 - (100 / (1 + rs))

        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def fetch_margins_via_yf(tickers):
    margin_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(f"{ticker}.TW")
            q_fin = stock.quarterly_financials
            if q_fin.empty:
                stock = yf.Ticker(f"{ticker}.TWO")
                q_fin = stock.quarterly_financials

            if not q_fin.empty and q_fin.shape[1] >= 2:
                latest = q_fin.iloc[:, 0]
                prev = q_fin.iloc[:, 1]

                def safe_get(series, keys):
                    for k in keys:
                        if k in series.index and pd.notnull(series[k]) and series[k] != 0:
                            return series[k]
                    return None

                rev_keys = ['Total Revenue', 'Operating Revenue', 'Revenue']
                gp_keys = ['Gross Profit']
                op_keys = ['Operating Income']
                ni_keys = ['Net Income', 'Net Income Common Stockholders']

                r1, g1, o1, n1 = safe_get(latest, rev_keys), safe_get(latest, gp_keys), safe_get(latest, op_keys), safe_get(latest, ni_keys)
                r2, g2, o2, n2 = safe_get(prev, rev_keys), safe_get(prev, gp_keys), safe_get(prev, op_keys), safe_get(prev, ni_keys)

                gm1 = (g1 / r1 * 100) if g1 and r1 else None
                om1 = (o1 / r1 * 100) if o1 and r1 else None
                nm1 = (n1 / r1 * 100) if n1 and r1 else None

                gm2 = (g2 / r2 * 100) if g2 and r2 else None
                om2 = (o2 / r2 * 100) if o2 and r2 else None
                nm2 = (n2 / r2 * 100) if n2 and r2 else None

                def format_margin(v1, v2):
                    if v1 is None: return None
                    if v2 is None: return f"{v1:.2f}%"
                    diff = v1 - v2
                    arrow = "🔺" if diff > 0 else ("🔻" if diff < 0 else "➖")
                    return f"{v1:.2f}% ({arrow}{diff:+.2f})"

                is_3_up = False
                if gm1 and gm2 and om1 and om2 and nm1 and nm2:
                    if (gm1 > gm2) and (om1 > om2) and (nm1 > nm2):
                        is_3_up = True

                margin_data.append({
                    '證券代號': str(ticker),
                    '三率狀態': '🔥 三率三升' if is_3_up else '',
                    '毛利率(季增減)': format_margin(gm1, gm2),
                    '營益率(季增減)': format_margin(om1, om2),
                    '淨利率(季增減)': format_margin(nm1, nm2)
                })
            else:
                info = stock.info
                margin_data.append({
                    '證券代號': str(ticker),
                    '三率狀態': '',
                    '毛利率(季增減)': f"{round(info.get('grossMargins', 0)*100, 2)}%" if info.get('grossMargins') else None,
                    '營益率(季增減)': f"{round(info.get('operatingMargins', 0)*100, 2)}%" if info.get('operatingMargins') else None,
                    '淨利率(季增減)': f"{round(info.get('profitMargins', 0)*100, 2)}%" if info.get('profitMargins') else None
                })
        except Exception:
            pass
    return pd.DataFrame(margin_data)

@st.cache_data(ttl=3600)
def get_all_data(selected_sectors):
    revenue_df = fetch_latest_monthly_revenue()
    df_taiex, market_stocks_data = build_history_market_data(trading_days=60)
    target_dict = {k: my_custom_sectors[k] for k in selected_sectors if k in my_custom_sectors}
    sector_dataframes = generate_sector_dataframes(market_stocks_data, target_dict)
    return revenue_df, df_taiex, sector_dataframes

# ==========================================
# 側邊欄控制台
# ==========================================
st.sidebar.title("🎛️ 法人戰情室控制台")
st.sidebar.markdown("---")

default_selection = [] 

st.sidebar.markdown("**📁 請展開分類並勾選項目：**")
selected_sectors = []

for category_name, sub_sectors in sector_categories.items():
    with st.sidebar.expander(category_name, expanded=False):
        for sector in sub_sectors:
            if sector in my_custom_sectors:
                is_checked = sector in default_selection
                if st.checkbox(sector, value=is_checked, key=f"chk_{sector}"):
                    selected_sectors.append(sector)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 強制更新資料"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 主畫面
# ==========================================
st.title("🚀 台股全市場動能 x 營收 x 三率決策儀表板")
st.markdown("---")

if not selected_sectors:
    st.warning("⚠️ 請從左側側邊欄至少勾選一個分類或題材！")
    st.stop()

with st.spinner('正在同步全市場成分股與最新月營收資料中...'):
    revenue_df, df_taiex, sector_dataframes = get_all_data(tuple(selected_sectors))

if revenue_df is None or df_taiex.empty:
    st.error("資料載入失敗，請確認網路連線。")
    st.stop()

strong_sectors = {}
rrg_all_history = {}

for sector_name, df_sector in sector_dataframes.items():
    if df_sector is None or df_sector.empty or 'Close' not in df_sector.columns:
        continue
        
    rrg_result = calculate_rrg_quadrants(df_sector, df_taiex, period=15)
    if rrg_result is None or rrg_result.empty:
        continue
        
    rrg_all_history[sector_name] = rrg_result
    
    if 'Quadrant' in rrg_result.columns and not rrg_result.empty:
        latest_status = rrg_result.iloc[-1]['Quadrant']
        if "第二象限 [轉強]" in latest_status or "第一象限 [領先]" in latest_status:
            strong_sectors[sector_name] = latest_status

# 左右雙欄配置
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📊 RRG 動能旋轉圖 (波段平滑化過濾雜訊)")
    if rrg_all_history:
        fig = plot_rrg_chart(rrg_all_history)
        st.pyplot(fig)
    else:
        st.warning("⚠️ 目前尚無足夠的 RRG 歷史數據可供繪圖。")

with col2:
    st.subheader("🏆 動能強勢群組：營收與三率檢驗")
    
    if not strong_sectors:
        st.info("在您勾選的群組中，目前沒有偵測到動能向上的標的。")
    else:
        for sector, quadrant in strong_sectors.items():
            st.markdown(f"#### 🔥 【{sector}】")
            st.caption(f"狀態：{quadrant}")
            
            stock_list = my_custom_sectors[sector]
            sector_revenue = revenue_df[revenue_df['證券代號'].isin(stock_list)].copy()
            
            if sector_revenue.empty:
                st.warning("尚無營收資料")
                continue
                
            strong_stocks = sector_revenue[sector_revenue['營收YoY(%)'] > 0].copy()
            strong_stocks = strong_stocks.sort_values('營收YoY(%)', ascending=False)
            
            if strong_stocks.empty:
                st.error("⚠️ 成分股最新營收皆衰退，留意純籌碼炒作。")
            else:
                with st.spinner(f'正在分析 {sector} 財報三率增減幅度...'):
                    tickers = strong_stocks['證券代號'].tolist()
                    margin_df = fetch_margins_via_yf(tuple(tickers))
                    if not margin_df.empty:
                        strong_stocks = pd.merge(strong_stocks, margin_df, on='證券代號', how='left')

                st.success("✅ 具備基本面支援 (營收YoY > 0)")
                
                display_cols = ["證券代號", "證券名稱", "當月營收", "營收YoY(%)"]
                
                if "累計營收YoY(%)" in strong_stocks.columns:
                    display_cols.append("累計營收YoY(%)")
                elif "累計營收成長率(%)" in strong_stocks.columns:
                    display_cols.append("累計營收成長率(%)")
                    
                for m in ['三率狀態', '毛利率(季增減)', '營益率(季增減)', '淨利率(季增減)']:
                    if m in strong_stocks.columns:
                        display_cols.append(m)
                
                strong_stocks = strong_stocks[display_cols]
                
                col_config = {
                    "當月營收": st.column_config.NumberColumn(format="%d"),
                    "營收YoY(%)": st.column_config.NumberColumn(format="%.2f %%")
                }
                if "累計營收YoY(%)" in display_cols:
                    col_config["累計營收YoY(%)"] = st.column_config.NumberColumn(format="%.2f %%")
                elif "累計營收成長率(%)" in display_cols:
                    col_config["累計營收成長率(%)"] = st.column_config.NumberColumn(format="%.2f %%")
                
                event = st.dataframe(
                    strong_stocks,
                    column_config=col_config,
                    hide_index=True,
                    use_container_width=True,
                    on_select="rerun",          
                    selection_mode="single-row" 
                )
                
                st.markdown("---")
                
                col_title, col_tf = st.columns([2, 1])
                with col_title:
                    st.subheader("📈 專業級技術分析面板 (無版權限制)")
                with col_tf:
                    selected_tf = st.radio("切換 K 線週期：", ["日K (近半年)", "週K (近2年)", "60分K (近2個月)", "15分K (近1個月)"], horizontal=True)
                
                if event.selection.rows:
                    selected_idx = event.selection.rows[0]
                    ticker = str(strong_stocks.iloc[selected_idx]['證券代號']).strip()
                    name = str(strong_stocks.iloc[selected_idx]['證券名稱']).strip()
                else:
                    ticker = str(strong_stocks.iloc[0]['證券代號']).strip()
                    name = str(strong_stocks.iloc[0]['證券名稱']).strip()
                
                st.info(f"📌 目前分析標的：**{ticker} {name}**")
                
                with st.spinner(f'正在運算 {ticker} 的 MACD 與 RSI 技術指標...'):
                    df_kline = get_pro_stock_data(ticker, selected_tf)
                    
                    if not df_kline.empty:
                        fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                                            row_heights=[0.5, 0.15, 0.15, 0.2], 
                                            vertical_spacing=0.02,
                                            subplot_titles=("K線與移動平均", "成交量", "MACD (12, 26, 9)", "RSI (14)"))
                        
                        colors = ['#ff0000' if row['Close'] >= row['Open'] else '#ffffff' for i, row in df_kline.iterrows()]
                        
                        fig.add_trace(go.Candlestick(
                            x=df_kline['Date_str'], open=df_kline['Open'], high=df_kline['High'], low=df_kline['Low'], close=df_kline['Close'],
                            name="K線", increasing_line_color='#ff0000', increasing_fillcolor='#ff0000', decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff'
                        ), row=1, col=1)
                        
                        fig.add_trace(go.Scatter(x=df_kline['Date_str'], y=df_kline['MA5'], name='MA5', line=dict(color='#2962FF', width=1.5)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df_kline['Date_str'], y=df_kline['MA20'], name='MA20', line=dict(color='#FFD600', width=1.5)), row=1, col=1)

                        fig.add_trace(go.Bar(x=df_kline['Date_str'], y=df_kline['Volume'], name="成交量", marker_color=colors), row=2, col=1)

                        fig.add_trace(go.Scatter(x=df_kline['Date_str'], y=df_kline['MACD'], name='MACD', line=dict(color='#00E676', width=1.5)), row=3, col=1)
                        fig.add_trace(go.Scatter(x=df_kline['Date_str'], y=df_kline['MACD_Signal'], name='Signal', line=dict(color='#FF1744', width=1.5)), row=3, col=1)
                        macd_colors = ['#ff0000' if val > 0 else '#ffffff' for val in df_kline['MACD_Hist']]
                        fig.add_trace(go.Bar(x=df_kline['Date_str'], y=df_kline['MACD_Hist'], name='Histogram', marker_color=macd_colors), row=3, col=1)

                        fig.add_trace(go.Scatter(x=df_kline['Date_str'], y=df_kline['RSI'], name='RSI', line=dict(color='#E040FB', width=1.5)), row=4, col=1)
                        fig.add_hline(y=70, line_dash="dash", line_color="gray", row=4, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color="gray", row=4, col=1)

                        fig.update_layout(
                            template='plotly_dark',
                            height=850,
                            xaxis_rangeslider_visible=False,
                            showlegend=False,
                            paper_bgcolor='#0a0a0a',
                            plot_bgcolor='#0a0a0a',
                            margin=dict(l=10, r=10, t=30, b=10)
                        )
                        fig.update_xaxes(type='category')
                        fig.update_xaxes(showticklabels=False, row=1, col=1)
                        fig.update_xaxes(showticklabels=False, row=2, col=1)
                        fig.update_xaxes(showticklabels=False, row=3, col=1)
                        fig.update_xaxes(nticks=10, row=4, col=1)

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"⚠️ 無法取得 {ticker} 的歷史 K 線資料。")