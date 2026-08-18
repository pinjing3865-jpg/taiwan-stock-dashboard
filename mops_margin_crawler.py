import pandas as pd
import requests
import time
from datetime import datetime
import streamlit as st
import io

@st.cache_data(ttl=86400) # 快取一天
def fetch_financial_margins():
    """獲取台股最新季度的三率，具備自動往前一季尋找的防呆機制"""
    now = datetime.now()
    current_year = now.year - 1911
    month = now.month
    
    # 決定初始查詢的季度
    if month >= 11:
        target_year, season = current_year, 3
    elif month >= 8:
        target_year, season = current_year, 2
    elif month >= 5:
        target_year, season = current_year, 1
    else:
        target_year, season = current_year - 1, 4

    url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb06'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Referer': 'https://mops.twse.com.tw/mops/web/t163sb06'
    }
    
    # 嘗試抓取，如果這一季沒資料或失敗，就自動往前找一季 (最多嘗試 2 次)
    for attempt in range(2):
        all_data = []
        for typek in ['sii', 'otc']:
            data = {
                'encodeURIComponent': '1',
                'step': '1',
                'firstin': '1',
                'off': '1',
                'TYPEK': typek,
                'year': str(target_year),
                'season': str(season)
            }
            try:
                res = requests.post(url, data=data, headers=headers, timeout=15)
                res.encoding = 'utf-8'
                dfs = pd.read_html(io.StringIO(res.text))
                
                for df in dfs:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(-1)
                    
                    if '公司代號' in df.columns and '營業收入' in df.columns:
                        df = df[pd.to_numeric(df['公司代號'], errors='coerce').notnull()]
                        df = df.rename(columns={'公司代號': '證券代號'})
                        df['證券代號'] = df['證券代號'].astype(str)
                        all_data.append(df)
                        break
            except Exception:
                pass
            time.sleep(1.5) # 避免被 MOPS 阻擋
            
        # 如果成功抓到資料，開始整理欄位
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            
            # 模糊比對尋找三率欄位 (官網名稱有時會變動)
            for col in final_df.columns:
                if '毛利率' in col: final_df.rename(columns={col: '毛利率(%)'}, inplace=True)
                elif '營業利益率' in col: final_df.rename(columns={col: '營益率(%)'}, inplace=True)
                elif '稅後純益率' in col: final_df.rename(columns={col: '淨利率(%)'}, inplace=True)
                elif '淨利率' in col: final_df.rename(columns={col: '淨利率(%)'}, inplace=True)
            
            keep_cols = ['證券代號']
            for target_col in ['毛利率(%)', '營益率(%)', '淨利率(%)']:
                if target_col in final_df.columns:
                    keep_cols.append(target_col)
                    
            final_df = final_df[keep_cols]
            for c in keep_cols[1:]:
                final_df[c] = pd.to_numeric(final_df[c], errors='coerce')
                
            return final_df
            
        # 如果這季沒資料，往前推一季繼續嘗試
        season -= 1
        if season == 0:
            season = 4
            target_year -= 1
            
    return pd.DataFrame()