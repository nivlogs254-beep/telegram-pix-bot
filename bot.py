import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Função que responde ao comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! 👋 Seu bot está funcionando direitinho agora!")

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("❌ ERRO: TELEGRAM_TOKEN não configurado!")
        return

    print("🤖 Iniciando o bot do Telegram...")
    app = ApplicationBuilder().token(token).build()

    # Adiciona o comando /start
    app.add_handler(CommandHandler("start", start))

    # Inicia o bot
    app.run_polling()

if __name__ == "__main__":
    main()
