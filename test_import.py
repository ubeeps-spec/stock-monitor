try:
    import yfinance
    print("yfinance imported successfully")
except ImportError as e:
    print(f"Error importing yfinance: {e}")
