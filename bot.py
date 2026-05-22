import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import mercadopago

app = Flask(__name__)
TOKEN = "8662275976:AAHAZi8Xb6sXG_KM89y1m_64W2OsZyPJi_M"
MP_ACCESS_TOKEN = "APP_USR-8721767628431060-052201-b83d858c4685a65783f0a8dffeb12218-3419988712"
PIX = "15a51d92-9c05-45d3-a748-eb8354d06188"
SUPORTE = "https://t.me/Suporteuvip"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton("💎 Ver VIP", callback_data="vip_menu")
    )

    bot.send_message(
        message.chat.id,
        "👋 Bem-vindo!\n\nClique abaixo para ver os planos VIP:",
        reply_markup=markup
    )


    markup.add(
        InlineKeyboardButton("⚡ VIP SEMANAL — R$7,99", callback_data="vip_semanal"),
        InlineKeyboardButton("🔥 VIP MENSAL — R$19,99", callback_data="vip_mensal"),
        InlineKeyboardButton("👑 VIP VITALÍCIO — R$42,99", callback_data="vip_vitalicio"),
        InlineKeyboardButton("📞 SUPORTE", url=SUPORTE)
    )

    bot.send_message(
        message.chat.id,
        "🔥 VIP OFICIAL 🔥\n\n"
        "🚀 Acesso imediato\n"
        "💎 Conteúdo exclusivo\n"
        "📦 Atualizações constantes\n\n"
        "💳 Escolha seu plano abaixo:",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    bot.answer_callback_query(call.id)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📞 ENVIAR COMPROVANTE", url=SUPORTE))

    if call.data == "vip_semanal":
        msg = f"""⚡ VIP SEMANAL

💰 R$7,99
🕒 7 dias

PIX:
{PIX}

📸 Envie o comprovante no suporte."""

    elif call.data == "vip_mensal":
        msg = f"""🔥 VIP MENSAL

💰 R$19,99
🕒 30 dias

PIX:
{PIX}

📸 Envie o comprovante no suporte."""

    elif call.data == "vip_vitalicio":
        msg = f"""👑 VIP VITALÍCIO

💰 R$42,99
♾️ Acesso permanente

PIX:
{PIX}

📸 Envie o comprovante no suporte."""

    else:
        return

    bot.send_message(call.message.chat.id, msg, reply_markup=markup)


print("BOT ONLINE")

bot.infinity_polling(skip_pending=True)