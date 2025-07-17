from flask import Flask
import threading
import time
import telebot
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

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

def enviar_mensagem_telegram(mensagem, chat_id):
    bot.send_message(chat_id, mensagem)

def formatar_hora(tempo):
    return tempo.strftime("%H:%M")

def enviar_sinal_telegram(par, direcao, chat_id):
    agora = datetime.now()
    entrada_hora = formatar_hora(agora)
    protecao1_hora = formatar_hora(agora + timedelta(minutes=1))
    protecao2_hora = formatar_hora(agora + timedelta(minutes=2))
    
    emoji = "🟩" if direcao.lower() == "compra" else "🟥"
    
    mensagem = (
        f"{par}\n"
        f"⏳ Expiração 1M\n"
        f"👉🏻 Entre Às {entrada_hora}\n"
        f"{emoji} {direcao.upper()}\n\n"
        f"1️⃣ Proteção Às {protecao1_hora}\n"
        f"2️⃣ Proteção Às {protecao2_hora}"
    )
    
    enviar_mensagem_telegram(mensagem, chat_id)

def enviar_resultado_telegram(par, direcao, resultado, chat_id):
    agora = datetime.now().strftime("%H:%M")
    emoji_resultado = "✅" if resultado == "WIN" else "❌"
    mensagem = (
        f"{emoji_resultado} Resultado: {resultado} no sinal de {direcao.upper()} - {par}\n"
        f"Hora do fechamento: {agora}"
    )
    enviar_mensagem_telegram(mensagem, chat_id)

def verificar_resultado(preco_entrada, preco_fechamento, direcao):
    if direcao == "compra":
        return "WIN" if preco_fechamento > preco_entrada else "LOSS"
    else:
        return "WIN" if preco_fechamento < preco_entrada else "LOSS"

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
            direcao = None

            if ultimo['EMA14'] > ultimo['EMA28'] and ultimo['RSI'] < 30:
                sinal = "compra"
                direcao = "compra"
            elif ultimo['EMA14'] < ultimo['EMA28'] and ultimo['RSI'] > 70:
                sinal = "venda"
                direcao = "venda"

            if sinal and sinal != ultimo_sinal:
                enviar_sinal_telegram("EUR / USD", direcao, CHAT_ID)
                print(f"Sinal enviado: {direcao.upper()}")

                preco_entrada = ultimo['Close']

                # Tentativa 1 - Entrada
                time.sleep(60)  # espera 1 minuto
                df_1 = buscar_dados(symbol)
                preco_fechamento_1 = df_1.iloc[-1]['Close']
                resultado = verificar_resultado(preco_entrada, preco_fechamento_1, direcao)
                if resultado == "WIN":
                    enviar_resultado_telegram("EUR / USD", direcao, resultado, CHAT_ID)
                    ultimo_sinal = sinal
                    time.sleep(240)  # espera antes de buscar próximo sinal
                    continue

                # Tentativa 2 - 1ª defesa
                time.sleep(60)  # espera mais 1 minuto
                df_2 = buscar_dados(symbol)
                preco_fechamento_2 = df_2.iloc[-1]['Close']
                resultado = verificar_resultado(preco_entrada, preco_fechamento_2, direcao)
                if resultado == "WIN":
                    enviar_resultado_telegram("EUR / USD", direcao, resultado, CHAT_ID)
                    ultimo_sinal = sinal
                    time.sleep(240)
                    continue

                # Tentativa 3 - 2ª defesa
                time.sleep(60)  # espera mais 1 minuto
                df_3 = buscar_dados(symbol)
                preco_fechamento_3 = df_3.iloc[-1]['Close']
                resultado = verificar_resultado(preco_entrada, preco_fechamento_3, direcao)
                enviar_resultado_telegram("EUR / USD", direcao, resultado, CHAT_ID)

                ultimo_sinal = sinal
                time.sleep(240)  # espera antes de próximo sinal

        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(60)  # espera e tenta novamente

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
