from flask import Flask
import threading
import time
import telebot

# === CONFIGURAÇÕES ===
BOT_TOKEN = "7392865352:AAGMZnERjrHpLTx7iHckgKfE8oihCXVp6uw"
CHAT_ID = -1002844793556  # ID do seu grupo no Telegram (com sinal de menos!)

# === INICIALIZA BOT E FLASK ===
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === FUNÇÃO QUE ANALISA E ENVIA SINAIS ===
def verificar_sinais():
    while True:
        try:
            # Aqui vai a lógica real (só exemplo por enquanto)
            mensagem = "🔔 Sinal automático enviado (exemplo com EMA + RSI)"
            bot.send_message(CHAT_ID, mensagem)
            print("Sinal enviado!")
        except Exception as e:
            print(f"Erro: {e}")
        
        time.sleep(300)  # Espera 5 minutos

# === THREAD PARA RODAR O BOT EM PARALELO ===
def start_bot():
    t = threading.Thread(target=verificar_sinais)
    t.daemon = True
    t.start()

# === ENDPOINT FLASK PARA MANTER RODANDO NA RENDER ===
@app.route('/')
def home():
    return 'Bot rodando com Flask!'

# === INÍCIO DO PROGRAMA ===
if __name__ == '__main__':
    start_bot()
    app.run(host='0.0.0.0', port=10000)
