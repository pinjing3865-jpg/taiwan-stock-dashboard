import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import streamlit as st

def get_market_data_for_date(date_str):
    """向證交所請求單日【全市場】收盤行情"""
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date_str}&type=ALLBUT0999"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        if data.get('stat') != 'OK':
            return None, None
        
        taiex_close = None
        stocks_df = None
        
        for table in data.get('tables', []):
            # 抓取大盤指數
            if 'fields' in table and '指數' in table['fields'] and '收盤指數' in table['fields']:
                idx_df = pd.DataFrame(table['data'], columns=table['fields'])
                taiex_row = idx_df[idx_df['指數'] == '發行量加權股價指數']
                if not taiex_row.empty:
                    taiex_close = float(taiex_row['收盤指數'].values[0].replace(',', ''))
            
            # 抓取全市場個股收盤價
            if 'fields' in table and '證券代號' in table['fields'] and '收盤價' in table['fields']:
                stocks_df = pd.DataFrame(table['data'], columns=table['fields'])
                stocks_df = stocks_df[['證券代號', '收盤價']].copy()
                # 過濾掉無效數值與字串
                stocks_df['收盤價'] = pd.to_numeric(stocks_df['收盤價'].astype(str).str.replace(',', '').replace('--', 'NaN'), errors='coerce')
                stocks_df = stocks_df.dropna()
                
        if taiex_close is not None and stocks_df is not None:
            return taiex_close, stocks_df
    except Exception:
        pass
    return None, None

@st.cache_data(ttl=43200) # 快取半天 (12小時)，避免重複請求
def build_history_market_data(trading_days=25):
    """往前收集全市場資料，並附帶進度條提示以降低等待焦慮"""
    current_date = datetime.now()
    
    # 建立動態進度提示
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    days_collected = 0
    days_lookback = 0
    
    taiex_data = []
    market_stocks_data = {} # 存放格式為 {日期: 該日全市場DataFrame}
    
    while days_collected < trading_days and days_lookback < 60:
        target_date = current_date - timedelta(days=days_lookback)
        date_str = target_date.strftime("%Y%m%d")
        
        # 排除週末
        if target_date.weekday() < 5:
            status_text.text(f"📥 正在向台灣證券交易所請求 {date_str} 全市場行情... [已收集 {days_collected}/{trading_days} 天]")
            
            taiex_close, stocks_df = get_market_data_for_date(date_str)
            
            if taiex_close is not None:
                taiex_data.append({'Date': date_str, 'Close': taiex_close})
                market_stocks_data[date_str] = stocks_df
                days_collected += 1
                progress_bar.progress(days_collected / trading_days)
                
                # 🛡️ 非常重要：遵守證交所防爬蟲規範，抓取成功後嚴格休息 3 秒，避免被封鎖 IP
                time.sleep(3) 
            else:
                # 遇國定假日或當日尚未收盤無資料，稍微停頓後繼續往前找
                time.sleep(0.5) 
                
        days_lookback += 1
        
    # 收集完畢後清空提示
    status_text.empty()
    progress_bar.empty()
    
    df_taiex = pd.DataFrame(taiex_data).sort_values('Date').reset_index(drop=True)
    return df_taiex, market_stocks_data

def generate_sector_dataframes(market_stocks_data, target_dict):
    """從全市場快取包中組裝各產業 DataFrame，加入防斷層與型別對齊處理"""
    sector_dataframes = {}
    sorted_dates = sorted(list(market_stocks_data.keys()))
    
    for sector_name, stock_list in target_dict.items():
        sector_history = []
        for date_str in sorted_dates:
            daily_df = market_stocks_data.get(date_str)
            if daily_df is None:
                continue
            
            # 確保代號皆為字串以正確匹配
            daily_df['證券代號'] = daily_df['證券代號'].astype(str)
            target_stocks = daily_df[daily_df['證券代號'].isin([str(s) for s in stock_list])]
            
            if not target_stocks.empty:
                avg_close = target_stocks['收盤價'].mean()
                sector_history.append({'Date': date_str, 'Close': avg_close})
        
        # 只要有 5 天以上的歷史數據就允許繪製 RRG
        if len(sector_history) >= 5:
            df = pd.DataFrame(sector_history)
            df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
            sector_dataframes[sector_name] = df.sort_values('Date')
            
    return sector_dataframes