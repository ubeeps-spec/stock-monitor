import streamlit as st
import pandas as pd
import time
from crawler import get_stock_data_yfinance

# 設定頁面配置
st.set_page_config(
    page_title="股票即時爬蟲看板",
    page_icon="📈",
    layout="wide"
)

st.title("📈 股票即時監控看板")
st.markdown("輸入股票代號，自動抓取最新股價並定時刷新。")

# 側邊欄設定
with st.sidebar:
    st.header("設定")
    default_symbols = "AAPL, 2330.TW, TSLA, NVDA, 0050.TW"
    symbols_input = st.text_area("輸入股票代號 (用逗號分隔)", value=default_symbols, height=150)
    
    refresh_rate = st.slider("刷新頻率 (秒)", min_value=5, max_value=300, value=10)
    
    st.markdown("---")
    st.markdown("**說明：**")
    st.markdown("- 台股請加 `.TW` (例如 `2330.TW`)")
    st.markdown("- 美股直接輸入代號 (例如 `AAPL`)")

# 主內容區
if symbols_input:
    # 處理輸入的代號
    symbols = [s.strip() for s in symbols_input.split(',') if s.strip()]
    
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
                for i, item in enumerate(data):
                    if i < 4: # 只顯示前4個卡片以免太擠
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
    st.info("請在左側輸入股票代號以開始監控。")
