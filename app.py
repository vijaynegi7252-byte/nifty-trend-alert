import requests
from flask import Flask
import pandas as pd
import numpy as np
import time
import threading

app = Flask(__name__)

# ---------------- CONFIG ----------------
BOT_TOKEN = "8005204216:AAGRaliYOC1VkGUwKBXgdJDpfnYHGuUEij0"
CHAT_ID = "1374000776"
DHAN_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzcxNDIzNTIzLCJpYXQiOjE3NzEzMzcxMjMsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTEwMDkyNDczIn0.ZqW0P1kFN0wPTVbBxnS9sIlb1yY5FZWQm9TybJnnysuiRyin5bncmLvqiriDKAjB2MdZWiaMlG7gpSw7a3HGlg"  # Replace wit your real key
SYMBOL = "NIFTY"
INTERVAL = "5minute"
CAPITAL = 25000
RISK_PER_TRADE = 500

# ---------------- TELEGRAM FUNCTION ----------------
def send_telegram(message):send_telegram("Test message: bot working")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram error:", e)

# ---------------- FETCH 5-MIN OHLC ----------------
def fetch_ohlc():
    url = "https://api.dhan.co/charts/intraday"
    headers = {"Authorization": f"Bearer {DHAN_API_KEY}"}
    payload = {"symbol": SYMBOL, "interval": INTERVAL}
    try:
        r = requests.post(url, headers=headers, json=payload)
        data = r.json()
        df = pd.DataFrame(data['candles'])
        df['close'] = pd.to_numeric(df['close'])
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        return df
    except Exception as e:
        print("Error fetching OHLC:", e)
        return None

# ---------------- EMA CALCULATION ----------------
def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def detect_trend(df):
    df['EMA20'] = calculate_ema(df, 20)
    df['EMA50'] = calculate_ema(df, 50)
    last_row = df.iloc[-1]
    if last_row['EMA20'] > last_row['EMA50']:
        return "Bullish"
    elif last_row['EMA20'] < last_row['EMA50']:
        return "Bearish"
    else:
        return "Sideways"

# ---------------- STRIKE, ENTRY, SL, TARGET ----------------
def calculate_trade(df, trend):
    last_price = df['close'].iloc[-1]
    if trend == "Bullish":
        strike = int(round(last_price/50)*50)
        option_type = "CE"
    elif trend == "Bearish":
        strike = int(round(last_price/50)*50)
        option_type = "PE"
    else:
        return None

    stop_loss = round(last_price * (RISK_PER_TRADE / CAPITAL), 1)
    target = round(stop_loss * 2, 1)

    return {
        "trend": trend,
        "strike": strike,
        "option_type": option_type,
        "entry": last_price,
        "stop_loss": stop_loss,
        "target": target
    }

# ---------------- SEND TRADE ALERT ----------------
def send_trade_alert(trade):
    message = (
        f"Nifty 5-min Trend Alert ✅\n"
        f"Trend: {trade['trend']}\n"
        f"Strike: {trade['strike']} {trade['option_type']}\n"
        f"Entry: ₹{trade['entry']}\n"
        f"Target: ₹{trade['target']}\n"
        f"Stop Loss: ₹{trade['stop_loss']}"
    )
    send_telegram(message)

# ---------------- BOT LOOP ----------------
def run_bot_loop():
    while True:
        df = fetch_ohlc()
        if df is not None and len(df) >= 20:
            trend = detect_trend(df)
            trade = calculate_trade(df, trend)
            if trade:
                send_trade_alert(trade)
        time.sleep(300)  # 5 minutes

# ---------------- FLASK ROUTE ----------------
@app.route("/")
def home():
    return "Nifty Trend Bot Running"

# ---------------- START BOT ----------------
if __name__ == "__main__":
    threading.Thread(target=run_bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
