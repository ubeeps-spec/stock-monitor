import streamlit as st
import pandas as pd
import time
from crawler import get_stock_data_yfinance
import db_manager as db

st.set_page_config(
    page_title="股票即時監控看板",
    page_icon="📈",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.logged_in:
    st.title("📈 股票看板登入系統")
    tab_login, tab_register = st.tabs(["登入", "註冊"])

    with tab_login:
        login_user = st.text_input("使用者名稱", key="login_user")
        login_pass = st.text_input("密碼", type="password", key="login_pass")
        if st.button("登入"):
            if login_user and login_pass:
                user_id = db.login_user(login_user, login_pass)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id
                    st.session_state.username = login_user
                    st.success("登入成功")
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤")
            else:
                st.warning("請輸入帳號和密碼")

    with tab_register:
        reg_user = st.text_input("設定使用者名稱", key="reg_user")
        reg_pass = st.text_input("設定密碼", type="password", key="reg_pass")
        reg_pass_confirm = st.text_input("確認密碼", type="password", key="reg_pass_confirm")
        if st.button("註冊"):
            if reg_user and reg_pass and reg_pass_confirm:
                if reg_pass != reg_pass_confirm:
                    st.error("兩次密碼輸入不一致")
                else:
                    if db.register_user(reg_user, reg_pass):
                        st.success("註冊成功，請切換到登入分頁登入")
                    else:
                        st.error("使用者名稱已存在")
            else:
                st.warning("請填寫所有欄位")
else:
    st.title(f"� {st.session_state.username} 的股票即時監控看板")
    st.markdown("輸入股票代號，自動抓取最新股價並定時刷新。")

    with st.sidebar:
        st.write(f"👤 {st.session_state.username}")
        if st.button("登出"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

        st.markdown("---")
        st.header("設定")

        current_watchlist = db.get_user_watchlist(st.session_state.user_id)

        with st.form("watchlist_form"):
            symbols_input = st.text_area("編輯股票代號 (用逗號分隔)", value=current_watchlist, height=150)
            submitted = st.form_submit_button("儲存清單")
            if submitted:
                db.update_user_watchlist(st.session_state.user_id, symbols_input)
                st.success("清單已儲存")
                current_watchlist = symbols_input

        refresh_rate = st.slider("刷新頻率 (秒)", min_value=5, max_value=300, value=10)

        st.markdown("---")
        st.markdown("**說明：**")
        st.markdown("- 台股請加 `.TW` (例如 `2330.TW`)")
        st.markdown("- 美股直接輸入代號 (例如 `AAPL`)")

    if current_watchlist:
        symbols = [s.strip() for s in current_watchlist.split(",") if s.strip()]
        if not symbols:
            st.info("您的觀察清單是空的，請在左側新增股票代號。")
        else:
            placeholder = st.empty()
            while True:
                with placeholder.container():
                    with st.spinner(f"正在更新數據... ({time.strftime('%H:%M:%S')})"):
                        data = get_stock_data_yfinance(symbols)

                    if data:
                        df = pd.DataFrame(data)

                        def color_change(val):
                            if isinstance(val, (int, float)):
                                if val > 0:
                                    return "color: red"
                                if val < 0:
                                    return "color: green"
                                return "color: black"
                            return ""

                        st.subheader(f"最新報價 (更新時間: {time.strftime('%H:%M:%S')})")

                        st.dataframe(
                            df.style.map(color_change, subset=["漲跌", "漲跌幅(%)"])
                            .format({"最新價": "{:.2f}", "漲跌": "{:+.2f}", "漲跌幅(%)": "{:+.2f}%"}),
                            use_container_width=True,
                            hide_index=True,
                        )

                        cols = st.columns(len(data))
                        for i, item in enumerate(data):
                            if i < 4:
                                with cols[i]:
                                    st.metric(
                                        label=item["代號"],
                                        value=item["最新價"],
                                        delta=f"{item['漲跌']} ({item['漲跌幅(%)']}%)",
                                    )
                    else:
                        st.warning("無法獲取數據，請檢查股票代號是否正確。")

                time.sleep(refresh_rate)
    else:
        st.info("請在左側輸入股票代號並儲存以開始監控。")
