import os
import threading
import http.server
import socketserver

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Lê o TOKEN da variável de ambiente (Render -> Environment -> TOKEN)
TOKEN = os.getenv("TOKEN")


# --------- Servidor HTTP "fake" só pra agradar o Render ---------
def start_dummy_http_server():
    """Abre um servidor HTTP simples na porta definida em PORT."""
    port = int(os.environ.get("PORT", "10000"))
    handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Servidor HTTP de saúde rodando na porta {port}")
        httpd.serve_forever()


# ---------------------- Handlers do bot ---------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # LOG pra gente ver no Render se o comando chegou
    user = update.effective_user
    print(f"Recebi /start de {user.id} - {user.first_name}")

    texto_inicial = (
        "Bonjour! 🇫🇷✨\n\n"
        "Antes de começar sua jornada no francês, entre no Grupo Oficial da Plataforma!\n"
        "Lá você recebe dicas diárias, materiais gratuitos, avisos importantes e suporte direto do Prof. Yann:\n\n"
        "👉 Junte-se agora: https://t.me/+0KMPSFwjfiZkM2Qx\n\n"
        "Depois, é só escolher uma das opções abaixo para continuar:"
    )

    botoes = [
        [
            InlineKeyboardButton(
                "🌐 Conhecer a plataforma",
                web_app=WebAppInfo(url="https://www.aulasdefrances.com"),
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Teste de nivelamento grátis",
                web_app=WebAppInfo(
                    url="https://aulasdefrances.com/teste-de-nivelamento-de-frances/"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ Sobre o Prof. Yann",
                web_app=WebAppInfo(
                    url="https://aulasdefrances.com/professor-nativo-de-frances-yann-amoussou/"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                "📅 Agendar Aula experimental grátis",
                web_app=WebAppInfo(
                    url="https://aulasdefrances.com/registro-alunos/"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                "🔑 Já sou Aluno – Fazer Login",
                web_app=WebAppInfo(
                    url="https://aulasdefrances.com/dashboard/bemvindo/"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                "📲 Falar com o Prof. Yann no WhatsApp",
                web_app=WebAppInfo(
                    url="https://wa.me/5562996263600"  # com DDI do Brasil (55)
                ),
            )
        ],
    ]

    teclado = InlineKeyboardMarkup(botoes)

    if update.message:
        await update.message.reply_text(
            texto_inicial,
            reply_markup=teclado,
            disable_web_page_preview=True,
        )


# Comando simples só pra testar se o bot está vivo
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Recebi /ping")
    await update.message.reply_text("Estou online! ✅")


def main():
    if not TOKEN:
        raise RuntimeError("TOKEN não encontrado. Configure a variável de ambiente TOKEN no Render.")

    # Inicia o servidor HTTP fake em uma thread separada
    http_thread = threading.Thread(target=start_dummy_http_server, daemon=True)
    http_thread.start()

    # Inicia o bot do Telegram
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))

    print("Bot rodando no Render...")
    app.run_polling()


if __name__ == "__main__":
    main()
