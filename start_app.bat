@echo off
echo ==========================================
echo 正在檢查並安裝必要的套件...
echo ==========================================
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 套件安裝失敗。
    echo 請嘗試手動執行: python -m pip install yfinance streamlit pandas requests plotly beautifulsoup4
    pause
    exit /b
)

echo.
echo ==========================================
echo 套件安裝完成，正在啟動股票看板...
echo ==========================================
python -m streamlit run app.py
pause
