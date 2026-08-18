import pandas as pd
import requests
import time
from datetime import datetime
import streamlit as st
import io

@st.cache_data(ttl=86400) # 財報一季才更新一次，快取設定一天即可
def fetch_financial_margins():
    """獲取台股最新季度的三率 (毛利率、營益率、淨利率)"""
    now = datetime.now()
    current_year = now.year - 1911
    month = now.month
    
    # 智慧判斷目前最新的財報季度 (Q1:5/15前, Q2:8/14前, Q3:11/14前, Q4:3/31前)
    if month >= 11:
        target_year, season = current_year, 3
    elif month >= 8:
        target_year, season = current_year, 2
    elif month >= 5:
        target_year, season = current_year, 1
    else:
        target_year, season = current_year - 1, 4

    url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb06'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    all_data = []
    # 同時抓取上市(sii)與上櫃(otc)的綜合損益表
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
                # 攤平公開資訊觀測站複雜的雙層表頭
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(-1)
                
                # 鎖定正確的損益表表格
                if '公司代號' in df.columns and '營業收入' in df.columns:
                    # 過濾掉表格中的中文分類標籤
                    df = df[pd.to_numeric(df['公司代號'], errors='coerce').notnull()]
                    df = df.rename(columns={'公司代號': '證券代號'})
                    df['證券代號'] = df['證券代號'].astype(str)
                    all_data.append(df)
                    break
        except Exception as e:
            pass
        time.sleep(1) # 溫柔爬取，避免被封鎖
        
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        
        # 模糊比對尋找三率欄位並重新命名 (因應官網有時會改欄位名稱)
        for col in final_df.columns:
            if '毛利率' in col: final_df.rename(columns={col: '毛利率(%)'}, inplace=True)
            elif '營業利益率' in col: final_df.rename(columns={col: '營益率(%)'}, inplace=True)
            elif '稅後純益率' in col: final_df.rename(columns={col: '淨利率(%)'}, inplace=True)
        
        # 只保留我們需要的核心戰略數據
        keep_cols = ['證券代號']
        for target_col in ['毛利率(%)', '營益率(%)', '淨利率(%)']:
            if target_col in final_df.columns:
                keep_cols.append(target_col)
                
        final_df = final_df[keep_cols]
        
        # 轉換為數字格式方便後續排序
        for c in keep_cols[1:]:
            final_df[c] = pd.to_numeric(final_df[c], errors='coerce')
            
        return final_df
        
    return pd.DataFrame()