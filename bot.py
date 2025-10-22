import os
from telegram.ext import Updater, CommandHandler

# Mensagem inicial do bot
def start(update, context):
    update.message.reply_text("Olá! 👋 Seu bot está funcionando direitinho!")

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("❌ ERRO: TELEGRAM_TOKEN não configurado!")
        return

    print("🤖 Iniciando o bot do Telegram...")
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    # Comando /start
    dispatcher.add_handler(CommandHandler("start", start))

    # Inicia o bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
