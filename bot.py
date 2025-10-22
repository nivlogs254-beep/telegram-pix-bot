# bot.py
# Bibliotecas necessárias:
# pip install python-telegram-bot mercadopago flask requests

import os
import json
import base64
import threading
import time
import requests
from flask import Flask, request
import mercadopago
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========= CONFIGURAÇÕES =========
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "COLOQUE_SEU_TOKEN_AQUI_SE_FOR_TESTE")
MERCADOPAGO_TOKEN = os.environ.get("MERCADOPAGO_TOKEN", "COLOQUE_SEU_TOKEN_AQUI_SE_FOR_TESTE")
GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID", None)  # Exemplo: -1001234567890
PAYMENTS_DB = "payments.json"
# =================================

sdk = mercadopago.SDK(MERCADOPAGO_TOKEN)
app = Flask(__name__)

def load_db():
    try:
        with open(PAYMENTS_DB, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(db):
    with open(PAYMENTS_DB, "w") as f:
        json.dump(db, f)

# ======== COMANDOS DO BOT =========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Olá! Bem-vindo ao bot de vendas.\n\n"
        "Temos o seguinte produto disponível:\n"
        "1️⃣ Curso Básico — R$10,00\n\n"
        "Digite /comprar 1 para adquirir."
    )

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use o comando assim: /comprar 1")
        return

    item = context.args[0]
    chat_id = update.effective_chat.id

    if item == "1":
        payment_data = {
            "transaction_amount": 10.0,
            "description": "Curso Básico - Acesso VIP",
            "payment_method_id": "pix",
            "external_reference": str(chat_id),
            "payer": {"email": "teste@teste.com"}
        }

        payment = sdk.payment().create(payment_data)
        response = payment["response"]
        tx_data = response.get("point_of_interaction", {}).get("transaction_data", {})
        qr_code = tx_data.get("qr_code", "")
        qr_base64 = tx_data.get("qr_code_base64", "")

        db = load_db()
        db[str(response.get("id"))] = {"chat_id": chat_id, "item": item}
        save_db(db)

        if qr_base64:
            img_bytes = base64.b64decode(qr_base64)
            await update.message.reply_photo(
                photo=img_bytes,
                caption=f"💰 Pague via PIX usando o QR Code ou copie o código abaixo:\n\n{qr_code}\n\nApós o pagamento, o acesso será liberado automaticamente."
            )
        else:
            await update.message.reply_text(f"Pague via PIX copiando o código abaixo:\n\n{qr_code}")
    else:
        await update.message.reply_text("Produto inválido.")

# ======= WEBHOOK DO MERCADO PAGO =======

@app.route("/notificacao", methods=["POST"])
def notificacao():
    data = request.json or {}
    payment_id = data.get("data", {}).get("id") or data.get("id")

    if not payment_id:
        return "no id", 200

    try:
        payment_info = sdk.payment().get(payment_id)
        payment_resp = payment_info.get("response", {})
        status = payment_resp.get("status")
        external_ref = payment_resp.get("external_reference")

        if status == "approved":
            chat_id = int(external_ref)
            tg_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

            # Criar link de convite para o grupo
            expire_date = int(time.time()) + 3600
            payload = {
                "chat_id": GROUP_CHAT_ID,
                "expire_date": expire_date,
                "member_limit": 1,
                "name": "Acesso Comprador"
            }

            r = requests.post(f"{tg_api}/createChatInviteLink", data=payload)
            link = None
            if r.status_code == 200 and r.json().get("ok"):
                link = r.json()["result"]["invite_link"]

            # Enviar mensagem ao comprador
            text = (
                f"✅ Pagamento confirmado!\n\n"
                f"Aqui está seu link de acesso (válido por 1 hora):\n\n{link}"
                if link else
                "Pagamento confirmado! Mas ocorreu um erro ao gerar o link, avise o suporte."
            )

            requests.post(f"{tg_api}/sendMessage", data={"chat_id": chat_id, "text": text})

    except Exception as e:
        print("Erro:", e)

    return "ok", 200

# ======= INICIAR BOT E SERVIDOR =======

def run_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("comprar", comprar))
    app_bot.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
