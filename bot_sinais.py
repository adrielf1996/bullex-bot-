from datetime import datetime, timedelta

def enviar_sinal_telegram(par, direcao, chat_id):
    agora = datetime.now()
    entrada_hora = agora.strftime("%H:%M")
    protecao1_hora = (agora + timedelta(minutes=1)).strftime("%H:%M")
    protecao2_hora = (agora + timedelta(minutes=2)).strftime("%H:%M")
    
    emoji = "🟩" if direcao.lower() == "compra" else "🟥"
    
    mensagem = (
        f"{par}\n"
        f"⏳ Expiração 1M\n"
        f"👉🏻 Entre Às {entrada_hora}\n"
        f"{emoji} {direcao.upper()}\n\n"
        f"1️⃣ Proteção Às {protecao1_hora}\n"
        f"2️⃣ Proteção Às {protecao2_hora}"
    )
    
    bot.send_message(chat_id, mensagem)
