import requests
import pandas as pd

def fetch_latest_monthly_revenue():
    """
    直接透過 TWSE 與 TPEx 官方 OpenAPI 抓取全市場「最新一期」每月營收 (免解析 HTML)
    """
    print("啟動官方 OpenAPI 抓取全市場最新營收...")
    
    # 1. 抓取上市 (TWSE) 最新每月營收彙總表
    url_twse = "https://openapi.twse.com.tw/v1/opendata/t187ap05_L"
    # 2. 抓取上櫃 (TPEx) 最新每月營收彙總表
    url_tpex = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    all_dfs = []
    
    # --- 抓取上市 ---
    try:
        r_twse = requests.get(url_twse, headers=headers, timeout=10)
        if r_twse.status_code == 200:
            df_twse = pd.DataFrame(r_twse.json())
            all_dfs.append(df_twse)
            print(f"成功取得【上市】最新營收，共 {len(df_twse)} 筆")
    except Exception as e:
        print(f"上市 OpenAPI 抓取失敗: {e}")
        
    # --- 抓取上櫃 ---
    try:
        r_tpex = requests.get(url_tpex, headers=headers, timeout=10)
        if r_tpex.status_code == 200:
            df_tpex = pd.DataFrame(r_tpex.json())
            all_dfs.append(df_tpex)
            print(f"成功取得【上櫃】最新營收，共 {len(df_tpex)} 筆")
    except Exception as e:
        print(f"上櫃 OpenAPI 抓取失敗: {e}")
        
    if not all_dfs:
        print("無法取得任何營收資料！")
        return None
        
    # 合併上市與上櫃
    df_all = pd.concat(all_dfs, ignore_index=True)
    
    # ==========================================
    # 整理統一的標準欄位
    # ==========================================
    try:
        # OpenAPI 的欄位名稱定義：
        # 公司代號 -> 證券代號
        # 公司名稱 -> 證券名稱
        # 營業收入-當月營收 -> 當月營收
        # 營業收入-去年同月增減(%) -> 營收YoY(%)
        # 出表日期/資料年月 -> 營收月份
        
        rename_dict = {
            '公司代號': '證券代號',
            '公司名稱': '證券名稱',
            '營業收入-當月營收': '當月營收',
            '營業收入-去年同月增減(%)': '營收YoY(%)'
        }
        
        df_all = df_all.rename(columns=rename_dict)
        
        # 確保代號為字串
        df_all['證券代號'] = df_all['證券代號'].astype(str)
        
        # 篩選我們需要的欄位
        result_df = df_all[['證券代號', '證券名稱', '當月營收', '營收YoY(%)']].copy()
        
        # 清理並轉為數值
        result_df['營收YoY(%)'] = pd.to_numeric(result_df['營收YoY(%)'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        result_df['當月營收'] = pd.to_numeric(result_df['當月營收'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        
        return result_df
        
    except Exception as e:
        print(f"整理資料格式時發生錯誤: {e}")
        return df_all

# ==========================================
# 測試執行區塊
# ==========================================
if __name__ == "__main__":
    revenue_data = fetch_latest_monthly_revenue()
    
    if revenue_data is not None:
        print(f"\n🎉 抓取成功！全市場(上市+上櫃)總計抓取 {len(revenue_data)} 檔個股")
        
        print("\n隨機抽樣 5 檔個股最新營收表現：")
        print(revenue_data.sample(5).to_markdown(index=False))
        
        print("\n🔍 搜尋指標強勢股 (例如: 散熱的奇鋐 3017 與 雙鴻 3324、AI代工廣達 2382)：")
        target_stocks = revenue_data[revenue_data['證券代號'].isin(['3017', '3324', '2382'])]
        print(target_stocks.to_markdown(index=False))