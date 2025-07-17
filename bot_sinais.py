from flask import Flask
import threading
import time
import telebot
import yfinance as yf
import pandas as pd
import numpy as np

BOT_TOKEN = "7392865352:AAGMZnERjrHpLTx7iHckgKfE8oihCXVp6uw"
CHAT_ID = -1002844793556  # Seu grupo Telegram

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def calcular_ema(series, periodo):
    return series.ewm(span=periodo, adjust=False).mean()

def calcular_rsi(series, periodo=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=periodo).mean()
    avg_loss = loss.rolling(window=periodo).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def buscar_dados(symbol):
    data = yf.download(tickers=symbol, period="1d", interval="1m")
    return data

ultimo_sinal = None

def verificar_sinais():
    global ultimo_sinal
    while True:
        try:
            symbol = "EURUSD=X"
            df = buscar_dados(symbol)

            df['EMA14'] = calcular_ema(df['Close'], 14)
            df['EMA28'] = calcular_ema(df['Close'], 28)
            df['RSI'] = calcular_rsi(df['Close'])

            ultimo = df.iloc[-1]

            sinal = None

            if ultimo['EMA14'] > ultimo['EMA28'] and ultimo['RSI'] < 30:
                sinal = "📈 Sinal de COMPRA em EUR/USD"
            elif ultimo['EMA14'] < ultimo['EMA28'] and ultimo['RSI'] > 70:
                sinal = "📉 Sinal de VENDA em EUR/USD"

            if sinal and sinal != ultimo_sinal:
                bot.send_message(CHAT_ID, sinal)
                print(sinal)
                ultimo_sinal = sinal

        except Exception as e:
            print(f"Erro: {e}")

        time.sleep(300)

def start_bot():
    t = threading.Thread(target=verificar_sinais)
    t.daemon = True
    t.start()

@app.route('/')
def home():
    return 'Bot rodando com Flask!'

if __name__ == '__main__':
    start_bot()
    app.run(host='0.0.0.0', port=10000)
