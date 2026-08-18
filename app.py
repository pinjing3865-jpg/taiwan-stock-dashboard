import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# 匯入分析模組
from twse_crawler import fetch_twse_index_data
from rrg_calculator import calculate_rrg_quadrants
from custom_sector_builder import build_custom_sector_index
from mops_revenue_crawler import fetch_latest_monthly_revenue
from rrg_visualizer import plot_rrg_chart

# ==========================================
# 網頁基本設定
# ==========================================
st.set_page_config(page_title="台股全市場完整成分股戰情室", layout="wide", page_icon="📈")

# ==========================================
# 完整成分股升級版細產業字典 (涵蓋龍頭與中小型二線廠)
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

@st.cache_data(ttl=3600)
def get_benchmark_history(days=25):
    today = datetime.now()
    date_list = [(today - timedelta(days=x)).strftime("%Y%m%d") for x in range(days)]
    date_list.reverse()
    
    taiex_history = []
    for date_str in date_list:
        df = fetch_twse_index_data(date_str)
        if df is not None:
            taiex_row = df[df['指數'] == '發行量加權股價指數']
            if not taiex_row.empty:
                taiex_history.append({
                    'Date': taiex_row['Date'].values[0],
                    'Close': taiex_row['收盤指數'].values[0]
                })
        time.sleep(1)
    return pd.DataFrame(taiex_history)

@st.cache_data(ttl=3600)
def get_all_data(selected_sectors):
    revenue_df = fetch_latest_monthly_revenue()
    df_taiex = get_benchmark_history(days=25)
    target_dict = {k: my_custom_sectors[k] for k in selected_sectors if k in my_custom_sectors}
    sector_dataframes = build_custom_sector_index(target_dict, days_to_fetch=25)
    return revenue_df, df_taiex, sector_dataframes

# ==========================================
# 側邊欄：多選控制台
# ==========================================
st.sidebar.title("🎛️ 法人戰情室控制台")
st.sidebar.markdown("---")

default_selection = ['PCB-製造', '光學鏡片', '航運', '矽晶圓', '散熱模組', '電源供應器', 'IC-設計', 'IC-封測', '網通設備']

st.sidebar.markdown("**請勾選欲分析的細產業 (可複選)：**")
selected_sectors = []

# 建立所有的核取方塊
for sector in list(my_custom_sectors.keys()):
    is_checked = sector in default_selection
    if st.sidebar.checkbox(sector, value=is_checked, key=f"chk_{sector}"):
        selected_sectors.append(sector)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 強制更新資料"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 主畫面
# ==========================================
st.title("🚀 台股全市場完整成分股動能 x 營收決策儀表板")
st.markdown("---")

if not selected_sectors:
    st.warning("⚠️ 請從左側側邊欄至少勾選一個細產業！")
    st.stop()

with st.spinner('正在同步全市場完整成分股與最新月營收資料中...'):
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
    st.subheader("🏆 動能向上之強勢族群與基本面")
    
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
                st.success("✅ 具備基本面支援 (YoY > 0)")
                st.dataframe(
                    strong_stocks,
                    column_config={
                        "當月營收": st.column_config.NumberColumn(format="%d"),
                        "營收YoY(%)": st.column_config.NumberColumn(format="%.2f %%")
                    },
                    hide_index=True,
                    use_container_width=True
                )