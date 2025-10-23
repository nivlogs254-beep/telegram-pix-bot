import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Variáveis principais
BOT_TOKEN = "SEU_TELEGRAM_TOKEN"
GROUP_ID = -4887647998  # Coloque o ID do seu grupo (use número negativo para grupos)
LINK_PIX = "https://link-do-seu-checkout-mercado-pago.com"  # Coloque o link do pagamento

# Dicionário pra armazenar quem enviou comprovante
comprovantes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Olá! Eu sou o bot de vendas. Digite /comprar para adquirir o e-book."
    )

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💰 Para comprar o e-book, envie o valor via PIX usando o link abaixo:\n\n{LINK_PIX}\n\n"
        "Depois, envie o comprovante aqui como foto 📸 ou PDF 📄."
    )

async def receber_comprovante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    comprovantes[user.id] = True
    await update.message.reply_text(
        "✅ Comprovante recebido! Aguarde um momento para aprovação manual."
    )

async def aprovar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        await update.message.reply_text("Esse comando deve ser usado no privado.")
        return

    if not context.args:
        await update.message.reply_text("Use assim: /aprovar <id do usuário>")
        return

    try:
        user_id = int(context.args[0])
        bot = context.bot
        await bot.add_chat_members(chat_id=GROUP_ID, user_ids=[user_id])
        await update.message.reply_text("✅ Usuário adicionado ao grupo com sucesso!")
        await bot.send_message(chat_id=user_id, text="🎉 Seu pagamento foi aprovado! Bem-vindo ao grupo!")
    except Exception as e:
        await update.message.reply_text(f"Erro ao adicionar: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("comprar", comprar))
app.add_handler(MessageHandler(filters.PHOTO | filters.Document.PDF, receber_comprovante))
app.add_handler(CommandHandler("aprovar", aprovar))

print("🤖 Bot rodando...")
app.run_polling()
