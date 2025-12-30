import streamlit as st
import pandas as pd
import time
from crawler import get_stock_data_yfinance
import db_manager as db

# 設定頁面配置
st.set_page_config(
    page_title="股票即時爬蟲看板",
    page_icon="📈",
    layout="wide"
)

# 初始化 Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# 登入/註冊 邏輯
if not st.session_state.logged_in:
    st.title("🔐 股票看板登入系統")
    
    tab1, tab2 = st.tabs(["登入", "註冊"])
    
    with tab1:
        st.header("登入")
        login_user = st.text_input("使用者名稱", key="login_user")
        login_pass = st.text_input("密碼", type="password", key="login_pass")
        if st.button("登入"):
            if login_user and login_pass:
                user_id = db.login_user(login_user, login_pass)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = login_user
                    st.success("登入成功！")
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤")
            else:
                st.warning("請輸入帳號和密碼")

    with tab2:
        st.header("註冊")
        reg_user = st.text_input("設定使用者名稱", key="reg_user")
        reg_pass = st.text_input("設定密碼", type="password", key="reg_pass")
        reg_pass_confirm = st.text_input("確認密碼", type="password", key="reg_pass_confirm")
        
        if st.button("註冊"):
            if reg_user and reg_pass:
                if reg_pass != reg_pass_confirm:
                    st.error("兩次密碼輸入不一致")
                else:
                    if db.register_user(reg_user, reg_pass):
                        st.success("註冊成功！請切換到登入分頁進行登入。")
                    else:
                        st.error("使用者名稱已存在")
            else:
                st.warning("請填寫所有欄位")

else:
    # 已登入狀態 - 顯示主儀表板
    st.title(f"📈 {st.session_state.username} 的股票監控看板")
    st.markdown("輸入股票代號，自動抓取最新股價並定時刷新。")
    
    # 側邊欄設定
    with st.sidebar:
        st.write(f"👤 **{st.session_state.username}**")
        if st.button("登出"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
            
        st.markdown("---")
        st.header("設定")
        
        # 從資料庫獲取用戶的清單
        current_watchlist = db.get_user_watchlist(st.session_state.user_id)
        
        # 讓用戶編輯清單
        # 注意：這裡使用 form 來避免每次打字都觸發 rerun，或者提供一個明確的儲存按鈕
        with st.form("watchlist_form"):
            symbols_input = st.text_area("編輯股票代號 (用逗號分隔)", value=current_watchlist, height=150)
            submitted = st.form_submit_button("儲存清單")
            
            if submitted:
                db.update_user_watchlist(st.session_state.user_id, symbols_input)
                st.success("清單已儲存！")
                current_watchlist = symbols_input # 更新當前變數以便立即反映
        
        refresh_rate = st.slider("刷新頻率 (秒)", min_value=5, max_value=300, value=10)
        
        st.markdown("---")
        st.markdown("**說明：**")
        st.markdown("- 台股請加 `.TW` (例如 `2330.TW`)")
        st.markdown("- 美股直接輸入代號 (例如 `AAPL`)")

    # 主內容區
    # 使用從 DB 或 表單 獲取的 symbols
    if current_watchlist:
        # 處理輸入的代號
        symbols = [s.strip() for s in current_watchlist.split(',') if s.strip()]
        
        if not symbols:
             st.info("您的觀察清單是空的，請在左側新增股票代號。")
        else:
            # 建立一個佔位符容器，用於更新數據
            placeholder = st.empty()
            
            # 這裡我們使用 Streamlit 的 rerun 機制或者簡單的循環來模擬連動
            # Streamlit 原生支援 st.empty() + time.sleep() 來做簡單的動畫/更新
            
            while True:
                with placeholder.container():
                    # 獲取數據
                    with st.spinner(f'正在更新數據... ({time.strftime("%H:%M:%S")})'):
                        data = get_stock_data_yfinance(symbols)
                    
                    if data:
                        df = pd.DataFrame(data)
                        
                        # 樣式化 DataFrame
                        def color_change(val):
                            if isinstance(val, (int, float)):
                                color = 'red' if val > 0 else 'green' if val < 0 else 'black'
                                return f'color: {color}'
                            return ''

                        st.subheader(f"最新報價 (更新時間: {time.strftime('%H:%M:%S')})")
                        
                        # 顯示數據表格
                        # 針對漲跌幅欄位應用顏色 (台股習慣：紅漲綠跌)
                        st.dataframe(
                            df.style.map(color_change, subset=['漲跌', '漲跌幅(%)'])
                            .format({"最新價": "{:.2f}", "漲跌": "{:+.2f}", "漲跌幅(%)": "{:+.2f}%"}),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # 簡單的指標卡片
                        cols = st.columns(len(data))
                        # 限制顯示卡片數量，避免過多
                        display_limit = 4
                        for i, item in enumerate(data):
                            if i < display_limit: 
                                with cols[i]:
                                    st.metric(
                                        label=item['代號'],
                                        value=item['最新價'],
                                        delta=f"{item['漲跌']} ({item['漲跌幅(%)']}%)"
                                    )
                    else:
                        st.warning("無法獲取數據，請檢查股票代號是否正確。")
                
                # 等待下一次刷新
                time.sleep(refresh_rate)
                # 注意：在 Streamlit Cloud 或某些環境中，長時間的 while True loop 可能會被中斷
                # 但在本地執行這是最簡單的即時更新方式
    else:
        st.info("請在左側輸入股票代號並儲存以開始監控。")
