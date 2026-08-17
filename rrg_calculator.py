import pandas as pd
import numpy as np

def calculate_rrg_quadrants(df_sector, df_taiex, period=5):
    """計算 RRG 相對強弱與動能指標 (標準 100 基準化版)"""
    if df_sector is None or df_sector.empty or df_taiex is None or df_taiex.empty:
        return None
        
    df_s = df_sector.copy()
    df_t = df_taiex.copy()
    
    # 統一日期格式
    df_s['Date_Clean'] = df_s['Date'].astype(str).str.replace('-', '', regex=False).str.replace('/', '', regex=False)
    df_t['Date_Clean'] = df_t['Date'].astype(str).str.replace('-', '', regex=False).str.replace('/', '', regex=False)
    
    df_merged = pd.merge(df_s, df_t, on='Date_Clean', suffixes=('_Sector', '_Taiex'))
    
    if df_merged.empty or len(df_merged) < period:
        min_len = min(len(df_s), len(df_t))
        if min_len < period:
            return None
        df_merged = pd.DataFrame({
            'Date_Clean': df_s['Date_Clean'].values[-min_len:],
            'Close_Sector': df_s['Close'].values[-min_len:],
            'Close_Taiex': df_t['Close'].values[-min_len:]
        })
        
    df_merged = df_merged.reset_index(drop=True)
    
    # 1. 算出原始相對強度 (RS)
    df_merged['RS'] = df_merged['Close_Sector'] / df_merged['Close_Taiex']
    
    # 2. 將 RS 轉換為以 100 為中心的 RS-Ratio (相對大盤強弱)
    df_merged['RS_MA'] = df_merged['RS'].rolling(window=period).mean()
    df_merged['RS-Ratio'] = (df_merged['RS'] / df_merged['RS_MA']) * 100
    
    # 3. 將動能轉換為以 100 為中心的 RS-Momentum (趨勢動能)
    df_merged['RS-Ratio_MA'] = df_merged['RS-Ratio'].rolling(window=period).mean()
    df_merged['RS-Momentum'] = (df_merged['RS-Ratio'] / df_merged['RS-Ratio_MA']) * 100
    
    df_merged = df_merged.dropna().reset_index(drop=True)
    if df_merged.empty:
        return None
        
    # 定義象限
    quadrants = []
    for idx, row in df_merged.iterrows():
        r = row['RS-Ratio']
        m = row['RS-Momentum']
        if r >= 100 and m >= 100:
            quadrants.append('第一象限 [領先]')
        elif r < 100 and m >= 100:
            quadrants.append('第二象限 [轉強]')
        elif r < 100 and m < 100:
            quadrants.append('第三象限 [落後]')
        else:
            quadrants.append('第四象限 [轉弱]')
            
    df_merged['Quadrant'] = quadrants
    return df_merged