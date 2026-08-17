import requests
import pandas as pd
import time
from datetime import datetime, timedelta

def fetch_twse_all_stocks(date_str):
    """抓取上市 (TWSE) 全市場個股收盤價"""
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date_str}&type=ALLBUT0999"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get('stat') != 'OK':
            return pd.DataFrame()
            
        target_table = None
        if 'tables' in data:
            for table in data['tables']:
                if 'title' in table and '每日收盤行情' in table['title'] and '全部' in table['title']:
                    target_table = table
                    break
        elif 'data9' in data:
            target_table = {'data': data['data9'], 'fields': data['fields9']}
            
        if not target_table:
            return pd.DataFrame()
            
        df = pd.DataFrame(target_table['data'], columns=target_table['fields'])
        df = df[['證券代號', '證券名稱', '收盤價']]
        df = df[df['收盤價'] != '--'].copy()
        df['收盤價'] = df['收盤價'].str.replace(',', '').astype(float)
        df['Date'] = pd.to_datetime(date_str).strftime('%Y-%m-%d')
        return df
    except Exception as e:
        print(f"抓取 {date_str} 上市資料錯誤: {e}")
        return pd.DataFrame()

def fetch_tpex_all_stocks(date_str):
    """抓取上櫃 (TPEx) 全市場個股收盤價"""
    roc_year = int(date_str[:4]) - 1911
    roc_date = f"{roc_year}/{date_str[4:6]}/{date_str[6:]}"
    
    url = f"https://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={roc_date}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        raw_data = None
        if 'aaData' in data and data['aaData']:
            raw_data = data['aaData']
        elif 'tables' in data and data['tables']:
            raw_data = data['tables'][0].get('data', [])
        elif 'data' in data:
            raw_data = data['data']
            
        if not raw_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(raw_data)
        if len(df.columns) >= 3:
            df = df.iloc[:, [0, 1, 2]]
            df.columns = ['證券代號', '證券名稱', '收盤價']
            df = df[~df['收盤價'].isin(['--', '---', ''])].copy()
            df['收盤價'] = df['收盤價'].astype(str).str.replace(r'[^0-9.]', '', regex=True)
            df = df[df['收盤價'] != '']
            df['收盤價'] = df['收盤價'].astype(float)
            df['Date'] = pd.to_datetime(date_str).strftime('%Y-%m-%d')
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"抓取 {date_str} 上櫃資料錯誤: {e}")
        return pd.DataFrame()

def build_custom_sector_index(custom_sectors, days_to_fetch=40):
    """結合上市與上櫃資料，建構自訂細產業的歷史指數"""
    today = datetime.now()
    date_list = [(today - timedelta(days=x)).strftime("%Y%m%d") for x in range(days_to_fetch)]
    date_list.reverse()
    
    custom_index_history = {sector: [] for sector in custom_sectors.keys()}
    
    for date_str in date_list:
        twse_df = fetch_twse_all_stocks(date_str)
        tpex_df = fetch_tpex_all_stocks(date_str)
        market_df = pd.concat([twse_df, tpex_df], ignore_index=True)
        
        if not market_df.empty:
            for sector_name, stock_list in custom_sectors.items():
                sector_stocks = market_df[market_df['證券代號'].isin(stock_list)]
                if not sector_stocks.empty:
                    avg_price = sector_stocks['收盤價'].mean()
                    custom_index_history[sector_name].append({
                        'Date': sector_stocks['Date'].iloc[0],
                        'Close': avg_price
                    })
        time.sleep(3)
        
    result_dfs = {}
    for sector_name, history in custom_index_history.items():
        if history:
            result_dfs[sector_name] = pd.DataFrame(history)
    return result_dfs