from flask import Flask, jsonify, request, render_template
import yfinance as yf
import pandas as pd
import sqlite3

app = Flask(__name__)

# --- Database with companies ---
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS companies(
            symbol TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    # Insert some Indian stocks (you can add more)
    companies = [
        ("RELIANCE.NS", "Reliance Industries"),
        ("TCS.NS", "Tata Consultancy Services"),
        ("INFY.NS", "Infosys"),
        ("HDFCBANK.NS", "HDFC Bank"),
        ("SBIN.NS", "State Bank of India")
    ]
    c.executemany("INSERT OR IGNORE INTO companies VALUES (?,?)", companies)
    conn.commit()
    conn.close()

init_db()

# Function to fetch & process data
def get_stock_data(symbol):
    df = yf.download(symbol, period="1y")

# ✅ Fix MultiIndex Columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    
    # Clean and transform
    df['Daily_Return'] = (df['Close'] - df['Open']) / df['Open']
    df['7Day_MA'] = df['Close'].rolling(window=7).mean()
    df['52Week_High'] = df['Close'].rolling(window=252).max()
    df['52Week_Low'] = df['Close'].rolling(window=252).min()

    return df

# --- API: List all companies ---
@app.route('/companies', methods=['GET'])
def companies():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT symbol, name FROM companies")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"symbol": r[0], "name": r[1]} for r in rows])

# --- API: Last 30 days Data ---
@app.route('/data/<symbol>', methods=['GET'])
def stock_data(symbol):
    df = get_stock_data(symbol).tail(30)
    return df.to_json(orient="records")

# --- API: Summary (52-week stats) ---
@app.route('/summary/<symbol>', methods=['GET'])
def summary(symbol):
    df = get_stock_data(symbol)
    high = df['52Week_High'].max()
    low = df['52Week_Low'].min()
    avg = df['Close'].mean()

    return jsonify({
        "symbol": symbol,
        "52Week_High": round(high,2),
        "52Week_Low": round(low,2),
        "Average_Close": round(avg,2)
    })

# --- API: Compare two stocks ---
@app.route('/compare', methods=['GET'])
def compare():
    s1 = request.args.get("symbol1")
    s2 = request.args.get("symbol2")

    df1 = get_stock_data(s1).tail(30)
    df2 = get_stock_data(s2).tail(30)

    return jsonify({
        s1: df1[['Date', 'Close']].to_dict(orient='records'),
        s2: df2[['Date', 'Close']].to_dict(orient='records')
    })

# --- Simple Frontend Dashboard (Bonus) ---
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
