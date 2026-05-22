import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import mercadopago

# ============================================================
# CONFIGURAÇÃO
# ============================================================
TOKEN           = "8662275976:AAHAZi8Xb6sXG_KM89y1m_64W2OsZyPJi_M"
MP_ACCESS_TOKEN = "APP_USR-8721767628431060-052201-b83d858c4685a65783f0a8dffeb12218-3419988712"
PIX             = "15a51d92-9c05-45d3-a748-eb8354d06188"
SUPORTE         = "https://t.me/Suporteuvip"
WEBHOOK_URL     = os.getenv("WEBHOOK_URL", "https://seusite.com")  # URL pública do servidor
VIP_GROUP_LINK  = os.getenv("VIP_GROUP_LINK", "")

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# ============================================================
# PLANOS
# ============================================================
PLANOS = {
    "vip_semanal":   {"nome": "VIP Semanal",   "valor": 7.99,  "duracao": "7 dias"},
    "vip_mensal":    {"nome": "VIP Mensal",     "valor": 19.99, "duracao": "30 dias"},
    "vip_vitalicio": {"nome": "VIP Vitalício",  "valor": 42.99, "duracao": "Acesso permanente ♾️"},
}

# ============================================================
# HELPERS
# ============================================================
def menu_vip():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("⚡ VIP Semanal — R$7,99",    callback_data="vip_semanal"),
        InlineKeyboardButton("🔥 VIP Mensal — R$19,99",    callback_data="vip_mensal"),
        InlineKeyboardButton("👑 VIP Vitalício — R$42,99", callback_data="vip_vitalicio"),
        InlineKeyboardButton("📞 Suporte",                  url=SUPORTE),
    )
    return markup


def criar_pagamento_pix(plano_key: str, chat_id: int) -> dict | None:
    plano = PLANOS[plano_key]
    payload = {
        "transaction_amount": plano["valor"],
        "description": plano["nome"],
        "payment_method_id": "pix",
        "payer": {"email": f"cliente_{chat_id}@telegram.com"},
        "notification_url": f"{WEBHOOK_URL}/mp/webhook",
        "external_reference": f"{chat_id}|{plano_key}",
    }
    response = sdk.payment().create(payload)
    if response["status"] == 201:
        return response["response"]
    return None


# ============================================================
# BOT — COMANDOS
# ============================================================
@bot.message_handler(commands=["start"])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 Ver Planos VIP", callback_data="vip_menu"))
    bot.send_message(
        message.chat.id,
        f"👋 Olá, *{message.from_user.first_name}*!\n\nClique abaixo para ver os planos VIP:",
        parse_mode="Markdown",
        reply_markup=markup,
    )


# ============================================================
# BOT — CALLBACKS
# ============================================================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    bot.answer_callback_query(call.id)

    # ── Menu de planos ────────────────────────────────────────
    if call.data == "vip_menu":
        bot.send_message(
            call.message.chat.id,
            "🔥 *VIP OFICIAL* 🔥\n\n"
            "🚀 Acesso imediato\n"
            "💎 Conteúdo exclusivo\n"
            "📦 Atualizações constantes\n\n"
            "👇 Escolha seu plano:",
            parse_mode="Markdown",
            reply_markup=menu_vip(),
        )
        return

    # ── Planos ───────────────────────────────────────────────
    if call.data in PLANOS:
        plano = PLANOS[call.data]

        bot.send_message(
            call.message.chat.id,
            f"⏳ Gerando seu PIX para *{plano['nome']}*...",
            parse_mode="Markdown",
        )

        pagamento = criar_pagamento_pix(call.data, call.message.chat.id)

        if pagamento:
            pix_copia_cola = (
                pagamento.get("point_of_interaction", {})
                .get("transaction_data", {})
                .get("qr_code", PIX)
            )
            payment_id = pagamento.get("id", "—")

            msg = (
                f"*{plano['nome']}*\n\n"
                f"💰 Valor: *R${plano['valor']:.2f}*\n"
                f"⏳ Duração: *{plano['duracao']}*\n"
                f"🔖 Pedido: `#{payment_id}`\n\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"💳 *PIX Copia e Cola:*\n\n"
                f"`{pix_copia_cola}`\n\n"
                f"_Copie o código acima e pague no seu banco._\n\n"
                f"✅ O acesso é liberado *automaticamente* após a confirmação!"
            )
        else:
            # Fallback para PIX manual se o MP falhar
            msg = (
                f"*{plano['nome']}*\n\n"
                f"💰 Valor: *R${plano['valor']:.2f}*\n"
                f"⏳ Duração: *{plano['duracao']}*\n\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"💳 *Chave Pix:*\n\n"
                f"`{PIX}`\n\n"
                f"_Copie a chave acima e faça o pagamento._\n\n"
                f"📸 Após pagar, envie o comprovante no suporte."
            )

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📩 Suporte / Comprovante", url=SUPORTE),
            InlineKeyboardButton("⬅️ Voltar aos planos",     callback_data="vip_menu"),
        )
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown", reply_markup=markup)


# ============================================================
# FLASK — WEBHOOK DO TELEGRAM
# ============================================================
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    json_data = request.get_json()
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "ok", 200


# ============================================================
# FLASK — WEBHOOK DO MERCADO PAGO
# ============================================================
@app.route("/mp/webhook", methods=["POST"])
def mp_webhook():
    data = request.get_json(silent=True) or {}

    if data.get("type") == "payment":
        payment_id = data.get("data", {}).get("id")
        if payment_id:
            response = sdk.payment().get(payment_id)
            pagamento = response.get("response", {})

            if pagamento.get("status") == "approved":
                external_ref = pagamento.get("external_reference", "")
                if "|" in external_ref:
                    chat_id_str, plano_key = external_ref.split("|", 1)
                    chat_id = int(chat_id_str)
                    plano_nome = PLANOS.get(plano_key, {}).get("nome", "VIP")

                    msg = (
                        f"✅ *Pagamento confirmado!*\n\n"
                        f"Seu acesso ao *{plano_nome}* foi liberado.\n\n"
                    )
                    if VIP_GROUP_LINK:
                        msg += f"👉 Entre no grupo agora: {VIP_GROUP_LINK}"
                    else:
                        msg += "Em breve você receberá o link do grupo."

                    bot.send_message(chat_id, msg, parse_mode="Markdown")

    return "ok", 200


# ============================================================
# INICIALIZAÇÃO
# ============================================================
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    print(f"Webhook configurado: {WEBHOOK_URL}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))