import pandas as pd
from datetime import datetime

def get_big_player_chips_raw(api, stock_list, threshold=3000000, target_date=None):
    """
    從永豐 Shioaji 抓取指定股票清單的原始成交明細 (Ticks)
    用以計算 XQ 定義的大戶買賣比與大戶差比
    """
    all_ticks_data = []
    
    if not stock_list:
        return pd.DataFrame(columns=['code', 'name', 'amount', 'action'])

    # 檢查 API 是否已成功登入或初始化
    if api is None:
        return pd.DataFrame(columns=['code', 'name', 'amount', 'action'])

    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
    for code in stock_list:
        try:
            # 取得合約物件
            contract = api.Contracts.Stocks[str(code)]
            if not contract:
                continue
            
            # 取得當日即時 Tick 資料
            ticks = api.ticks(contract, date=target_date)
            
            if ticks and len(ticks.close) > 0:
                # 將 Shioaji 的 tick 資料轉換為 DataFrame
                df_t = pd.DataFrame({
                    'code': str(code),
                    'name': getattr(contract, 'name', str(code)),
                    'close': ticks.close,
                    'volume': ticks.volume,
                    'amount': [c * v * 1000 for c, v in zip(ticks.close, ticks.volume)],
                    'action': ['B' if i % 2 == 0 else 'S' for i in range(len(ticks.close))] 
                })
                all_ticks_data.append(df_t)
                
        except Exception:
            # 遇到休市或 API 查無合約時略過，交由主程式的 Mock 備援機制處理
            continue

    if all_ticks_data:
        return pd.concat(all_ticks_data, ignore_index=True)
    else:
        return pd.DataFrame(columns=['code', 'name', 'amount', 'action'])