import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random

def get_stock_data_yfinance(symbols):
    """
    使用 yfinance 獲取股票數據 (最穩定)
    支援台股 (例如: 2330.TW), 美股 (例如: AAPL)
    """
    data = []
    if not symbols:
        return []
    
    # 處理符號，去除空白
    symbols = [s.strip() for s in symbols if s.strip()]
    
    try:
        tickers = yf.Tickers(' '.join(symbols))
        
        for symbol in symbols:
            try:
                ticker = tickers.tickers[symbol]
                # 獲取最新即時數據
                info = ticker.info
                # 獲取今日價格 (有些時候 info 裡的 price 會有延遲或缺失，嘗試用 fast_info 或 history)
                fast_info = ticker.fast_info
                
                current_price = fast_info.last_price if hasattr(fast_info, 'last_price') else info.get('currentPrice')
                previous_close = fast_info.previous_close if hasattr(fast_info, 'previous_close') else info.get('previousClose')
                
                if current_price is None:
                    # 如果拿不到，嘗試拿歷史數據的最後一筆
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                
                if current_price:
                    change = current_price - previous_close if previous_close else 0
                    change_pct = (change / previous_close * 100) if previous_close else 0
                    
                    data.append({
                        "代號": symbol,
                        "名稱": info.get('longName', symbol),
                        "最新價": round(current_price, 2),
                        "漲跌": round(change, 2),
                        "漲跌幅(%)": round(change_pct, 2),
                        "成交量": info.get('volume', 0)
                    })
                else:
                     data.append({
                        "代號": symbol,
                        "名稱": "無法獲取",
                        "最新價": 0,
                        "漲跌": 0,
                        "漲跌幅(%)": 0,
                        "成交量": 0
                    })

            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                data.append({
                        "代號": symbol,
                        "名稱": "錯誤",
                        "最新價": 0,
                        "漲跌": 0,
                        "漲跌幅(%)": 0,
                        "成交量": 0
                    })
                
    except Exception as e:
        print(f"Batch fetch error: {e}")
        
    return data

def get_stock_data_custom_url(url, selector, symbol):
    """
    示範：從自定義網站爬取數據
    這只是一個範例，需要根據實際目標網站的 HTML 結構調整 selector
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 假設 selector 是指向價格的元素
        element = soup.select_one(selector)
        price = element.text.strip() if element else "N/A"
        
        return {
            "代號": symbol,
            "來源": "自定義爬蟲",
            "最新價": price
        }
    except Exception as e:
        return {"代號": symbol, "error": str(e)}
