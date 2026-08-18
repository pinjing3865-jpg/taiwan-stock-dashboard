import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta
import time
import yfinance as yf
import json # 🌟 新增：用於將資料轉換給 TradingView

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
# 完整成分股細產業與粗分類字典
# ==========================================
my_custom_sectors = {
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
    'IC-製造': ['2330', '2303', '6770', '5347', '6525', '5351', '6531', '3707'],
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
    "📊 半導體族群": ['IC-製造', 'IC-設計', 'IC-封測', 'IC-通路', '矽晶圓', 'DRAM', '二極體'],
    "🔌 電子零組件": ['PCB-製造', 'PCB-材料設備', '被動元件', '連接元件', '電子零組件', '散熱模組', '電源供應器', '變壓器與UPS', '電池', '儀器設備工程'],
    "🖥️ 電腦與軟體": ['筆記型電腦', '電腦周邊產品', '板卡', '工業電腦', '軟體-系統整合', '軟體-其他', '軟體-遊戲', '安全監控'],
    "📡 光電與網通": ['光學鏡片', 'LCD面板', 'LCD零件', 'LED及光元件', '顯示器', '光碟片', '網通設備', '低軌衛星'],
    "🚗 車用與軍工": ['車用電子', '汽車零組件', '航天軍工'],
    "🏗️ 傳統產業": ['航運', '鋼鐵', '塑膠', '電機', '化學工業', '營建', '水泥', '玻璃陶瓷', '紙業', '紡織纖維'],
    "💼 生技金融與其他": ['生技', '金融-證券', '金融-金控', '控股公司', '電信服務', '綠能環保', '運動', '運動休閒', '居家生活', '家居', '電子-其他']
}

@st.cache_data(ttl=3600)
def get_stock_kline(ticker):
    try:
        stock = yf.Ticker(f"{ticker}.TW")
        df = stock.history(period="6mo")
        if df.empty:
            stock = yf.Ticker(f"{ticker}.TWO")
            df = stock.history(period="6mo")
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
    df_taiex, market_stocks_data = build_history_market_data(trading_days=25)
    target_dict = {k: my_custom_sectors[k] for k in selected_sectors if k in my_custom_sectors}
    sector_dataframes = generate_sector_dataframes(market_stocks_data, target_dict)
    return revenue_df, df_taiex, sector_dataframes

# ==========================================
# 側邊欄控制台
# ==========================================
st.sidebar.title("🎛️ 法人戰情室控制台")
st.sidebar.markdown("---")

default_selection = [] 

st.sidebar.markdown("**📁 請展開粗分類並勾選細產業：**")
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
    st.warning("⚠️ 請從左側側邊欄至少勾選一個細產業！")
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
        
    rrg_result = calculate_rrg_quadrants(df_sector, df_taiex, period=5)
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
    st.subheader("📊 RRG 動能旋轉圖 (完整成分股計算)")
    if rrg_all_history:
        fig = plot_rrg_chart(rrg_all_history)
        st.pyplot(fig)
    else:
        st.warning("⚠️ 目前尚無足夠的 RRG 歷史數據可供繪圖。")

with col2:
    st.subheader("🏆 動能強勢族群：營收與三率檢驗")
    
    if not strong_sectors:
        st.info("在您勾選的產業中，目前沒有偵測到動能向上的標的。")
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
                
                # 啟動可點擊連動的表格
                event = st.dataframe(
                    strong_stocks,
                    column_config=col_config,
                    hide_index=True,
                    use_container_width=True,
                    on_select="rerun",          
                    selection_mode="single-row" 
                )
                
                # ==========================================
                # 🌟 TradingView Lightweight Charts (官方輕量版開發引擎)
                # ==========================================
                st.markdown("---")
                st.subheader("📈 個股技術線圖 (TradingView 核心引擎驅動)")
                
                if event.selection.rows:
                    selected_idx = event.selection.rows[0]
                    ticker = str(strong_stocks.iloc[selected_idx]['證券代號'])
                    name = strong_stocks.iloc[selected_idx]['證券名稱']
                else:
                    ticker = str(strong_stocks.iloc[0]['證券代號'])
                    name = strong_stocks.iloc[0]['證券名稱']
                
                st.info(f"📌 目前顯示線圖：**{ticker} {name}** (請直接點擊上方表格內的任意列來切換)")
                
                with st.spinner(f'正在載入 {ticker} {name} 的 TradingView 線圖...'):
                    df_kline = get_stock_kline(ticker)
                    
                    if not df_kline.empty:
                        df_kline = df_kline.reset_index()
                        # 將時間轉換為 TradingView 讀得懂的格式
                        df_kline['Date_str'] = df_kline['Date'].dt.strftime('%Y-%m-%d')
                        
                        candle_data = []
                        volume_data = []
                        
                        for _, row in df_kline.iterrows():
                            # 判斷漲跌以決定成交量的顏色 (紅是漲白是跌)
                            is_up = row['Close'] >= row['Open']
                            vol_color = "#ff0000" if is_up else "#ffffff"
                            
                            candle_data.append({
                                "time": row['Date_str'],
                                "open": row['Open'],
                                "high": row['High'],
                                "low": row['Low'],
                                "close": row['Close']
                            })
                            volume_data.append({
                                "time": row['Date_str'],
                                "value": row['Volume'],
                                "color": vol_color
                            })
                            
                        # 將 Python 字典轉換為 JavaScript 讀得懂的 JSON 字串
                        candle_json = json.dumps(candle_data)
                        volume_json = json.dumps(volume_data)
                        
                        # 注入官方 Lightweight Charts 語法 (無版權干擾，無彈窗)
                        tv_light_html = f"""
                        <div id="tvchart" style="width: 100%; height: 500px;"></div>
                        <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
                        <script>
                            const chartOptions = {{
                                layout: {{
                                    textColor: 'white',
                                    background: {{ type: 'solid', color: '#000000' }}
                                }},
                                grid: {{
                                    vertLines: {{ color: '#1f1f1f' }},
                                    horzLines: {{ color: '#1f1f1f' }}
                                }},
                                crosshair: {{
                                    mode: LightweightCharts.CrosshairMode.Normal,
                                }},
                                rightPriceScale: {{
                                    borderColor: '#1f1f1f',
                                }},
                                timeScale: {{
                                    borderColor: '#1f1f1f',
                                }}
                            }};
                            
                            const chart = LightweightCharts.createChart(document.getElementById('tvchart'), chartOptions);

                            // 設定 K 線的紅漲白跌
                            const candlestickSeries = chart.addCandlestickSeries({{
                                upColor: '#ff0000',
                                downColor: '#ffffff',
                                borderUpColor: '#ff0000',
                                borderDownColor: '#ffffff',
                                wickUpColor: '#ff0000',
                                wickDownColor: '#ffffff'
                            }});
                            candlestickSeries.setData({candle_json});

                            // 設定成交量，將其壓在圖表的底部 20%
                            const volumeSeries = chart.addHistogramSeries({{
                                priceFormat: {{ type: 'volume' }},
                                priceScaleId: '', 
                            }});
                            chart.priceScale('').applyOptions({{
                                scaleMargins: {{ top: 0.8, bottom: 0 }},
                            }});
                            volumeSeries.setData({volume_json});
                            
                            // 自動縮放以適應螢幕寬度
                            chart.timeScale().fitContent();
                            
                            // 監聽視窗大小變化，維持 100% 寬度
                            window.addEventListener('resize', () => {{
                                chart.resize(document.getElementById('tvchart').clientWidth, 500);
                            }});
                        </script>
                        """
                        components.html(tv_light_html, height=500)
                    else:
                        st.error(f"⚠️ 無法取得 {ticker} 的歷史 K 線資料。")