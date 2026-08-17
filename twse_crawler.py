import requests
import pandas as pd
from datetime import datetime

def fetch_twse_index_data(date_str):
    """
    抓取 TWSE 特定日期的「各類指數日成交量值」
    
    參數:
    date_str: 字串格式 YYYYMMDD，例如 "20260814"
    """
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date_str}&type=IND"
    
    # 加入 headers 模擬瀏覽器行為，避免被阻擋
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # 檢查請求是否成功
        data = response.json()
        
        # 檢查該日期是否有資料 (可能遇到假日)
        if data.get('stat') != 'OK':
            print(f"{date_str} 沒有資料 (可能是假日)")
            return None
            
        # 動態適應 TWSE 新舊版 JSON 格式
        if 'tables' in data:
            target_table = data['tables'][0]
            for table in data['tables']:
                if 'title' in table and '指數' in table['title']:
                    target_table = table
                    break
            raw_data = target_table['data']
            columns = target_table['fields']
        elif 'data1' in data:
            raw_data = data['data1']
            columns = data['fields1']
        elif 'data' in data:
            raw_data = data['data']
            columns = data['fields']
        else:
            print(f"未知的 JSON 格式，目前的欄位有: {list(data.keys())}")
            return None

        # 建立 DataFrame
        df = pd.DataFrame(raw_data, columns=columns)
        
        # 整理我們要的欄位
        df = df[['指數', '收盤指數']]
        # 將收盤指數轉為浮點數 (移除千分位逗號)
        df['收盤指數'] = df['收盤指數'].str.replace(',', '').astype(float)
        # 加入日期欄位
        df['Date'] = pd.to_datetime(date_str).strftime('%Y-%m-%d')
        
        return df
        
    except Exception as e:
        print(f"抓取 {date_str} 資料時發生錯誤: {e}")
        return None

# ==========================================
# 測試抓取單日真實資料 (可獨立執行測試)
# ==========================================
if __name__ == "__main__":
    test_date = "20260814" # 確保這天是有開盤的平日
    print(f"正在抓取 {test_date} 的 TWSE 類股指數...")
    
    twse_df = fetch_twse_index_data(test_date)
    
    if twse_df is not None:
        print("\n抓取成功！前 10 筆資料如下：")
        print(twse_df.head(10).to_markdown(index=False))
        
        print("\n擷取特定指數示範：")
        try:
            taiex_close = twse_df[twse_df['指數'] == '發行量加權股價指數']['收盤指數'].values[0]
            semi_close = twse_df[twse_df['指數'] == '半導體類指數']['收盤指數'].values[0]
            print(f"大盤加權指數收盤: {taiex_close}")
            print(f"半導體類指數收盤: {semi_close}")
        except IndexError:
            print("找不到特定指數名稱，可能是該日無此指數資料。")