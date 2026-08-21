import shioaji as sj
import streamlit as st

# 1. 建立 Shioaji 物件
api = sj.Shioaji()

print("⏳ 準備連線至永豐伺服器...")

# 2. 從 Streamlit 的機密保險箱中讀取金鑰
API_KEY = st.secrets["SHIOAJI_API_KEY"]
SECRET_KEY = st.secrets["SHIOAJI_SECRET_KEY"]

# 3. 登入 API
try:
    api.login(
        api_key=API_KEY,
        secret_key=SECRET_KEY
    )
    print("🎉 恭喜！成功使用保險箱金鑰登入永豐 Shioaji API！")
    
    contract = api.Contracts.Stocks["2330"]
    print(f"📌 成功取得合約資訊: {contract.code} {contract.name}")
    
except Exception as e:
    print(f"❌ 登入失敗，錯誤訊息: {e}")