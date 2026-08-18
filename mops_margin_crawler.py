import pandas as pd
import requests
import time
from datetime import datetime
import streamlit as st
import io

@st.cache_data(ttl=86400) # 快取一天
def fetch_financial_margins():
    """從綜合損益表獲取絕對數值，並自行精準計算出三率"""
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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    # 嘗試抓取，如果這季沒資料就退一季
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
                        df = df.rename(columns={'公司代號': '證券代號'})
                        df['證券代號'] = df['證券代號'].astype(str)
                        # 過濾掉表格中的中文文字標題行
                        df['valid'] = pd.to_numeric(df['證券代號'], errors='coerce')
                        df = df.dropna(subset=['valid']).drop(columns=['valid'])
                        all_data.append(df)
                        break
            except Exception:
                pass
            time.sleep(1) # 保護機制，避免被封鎖
            
        if all_data:
            final_df = pd.concat(all_data, ignore_index=True)
            
            # 尋找計算所需的四個關鍵金額欄位 (因應官網名稱有時會微調，使用模糊比對)
            rev_col = next((c for c in final_df.columns if '營業收入' in c), None)
            gp_col = next((c for c in final_df.columns if '營業毛利' in c), None)
            op_col = next((c for c in final_df.columns if '營業利益' in c), None)
            ni_col = next((c for c in final_df.columns if '本期淨利' in c), None)

            # 如果四個金額都抓到了，就開始算數學
            if rev_col and gp_col and op_col and ni_col:
                # 轉為數值型態，並清掉千分位逗號
                for c in [rev_col, gp_col, op_col, ni_col]:
                    final_df[c] = pd.to_numeric(final_df[c].astype(str).str.replace(',', ''), errors='coerce')

                # 排除營收為 0 或空值的異常公司，避免數學上除以零
                final_df = final_df[final_df[rev_col] > 0].copy()

                # 💡 最核心的魔法：直接用金額算出三率百分比！
                final_df['毛利率(%)'] = (final_df[gp_col] / final_df[rev_col]) * 100
                final_df['營益率(%)'] = (final_df[op_col] / final_df[rev_col]) * 100
                final_df['淨利率(%)'] = (final_df[ni_col] / final_df[rev_col]) * 100

                return final_df[['證券代號', '毛利率(%)', '營益率(%)', '淨利率(%)']]

        # 如果跑到這裡，代表當季找不到資料，自動往前推一季
        season -= 1
        if season == 0:
            season = 4
            target_year -= 1
            
    return pd.DataFrame()