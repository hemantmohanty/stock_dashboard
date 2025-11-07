
import yfinance as yf
import pandas as pd

def get_stock_data(symbol):
    df = yf.download(symbol, period="60d")
    if df.empty:
        return {"error": "No data found for symbol"}

    df = df.reset_index()
    df['Daily Return'] = (df['Close'] - df['Open']) / df['Open']
    df['7d MA'] = df['Close'].rolling(7).mean()
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')  # ✅ safe string format

    # Select only safe columns
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Daily Return', '7d MA']]

    # ✅ This is the key line — no tuple keys
    return df.tail(30).to_dict(orient='records')


def get_summary(symbol):
    df = yf.download(symbol, period="1y")
    return {
        "52_week_high": df['High'].max(),
        "52_week_low": df['Low'].min(),
        "avg_close": df['Close'].mean()
    }

def compare_stocks(s1, s2):
    df1 = yf.download(s1, period="30d")['Close']
    df2 = yf.download(s2, period="30d")['Close']
    return {
        s1: df1.pct_change().cumsum().dropna().tolist(),
        s2: df2.pct_change().cumsum().dropna().tolist()
    }