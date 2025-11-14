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
    CallbackQueryHandler,
)

# Lê o TOKEN da variável de ambiente (Render -> Environment -> TOKEN)
TOKEN = os.getenv("TOKEN")

# Chat ID do admin (seu ID pessoal ou de um grupo/canal)
# Configure no Render -> Environment -> ADMIN_CHAT_ID
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


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
                callback_data="conhecer_plataforma",
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
                callback_data="agendar_aula",  # <--- AGORA VAI PARA UM FLUXO COM TEXTO
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
                url="https://wa.me/5562996263600",  # <--- SEM WebAppInfo
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


# Handler para os botões de callback
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    # 1) Quando a pessoa clica em "🌐 Conhecer a plataforma"
    if query.data == "conhecer_plataforma":
        texto_pergunta = (
            "Legal! 😄\n\n"
            "Quer aprender francês principalmente para:\n\n"
            "1️⃣ Trabalho\n"
            "2️⃣ Viagem\n"
            "3️⃣ Estudo / intercâmbio\n"
            "4️⃣ Interesse pessoal\n\n"
            "Escolha uma opção:"
        )

        botoes_motivo = [
            [InlineKeyboardButton("1️⃣ Trabalho", callback_data="motivo_trabalho")],
            [InlineKeyboardButton("2️⃣ Viagem", callback_data="motivo_viagem")],
            [InlineKeyboardButton("3️⃣ Estudo / intercâmbio", callback_data="motivo_estudo")],
            [InlineKeyboardButton("4️⃣ Interesse pessoal", callback_data="motivo_pessoal")],
        ]

        teclado_motivo = InlineKeyboardMarkup(botoes_motivo)

        await query.message.reply_text(
            texto_pergunta,
            reply_markup=teclado_motivo,
        )
        return

    # 2) Fluxo da Aula experimental
    if query.data == "agendar_aula":
        texto_aula = (
            "✨ Sua *aula experimental grátis* é um momento exclusivo entre você e o Prof. Yann.\n\n"
            "Para deixar tudo organizado, você vai:\n"
            "1️⃣ Criar seu cadastro\n"
            "2️⃣ Verificar sua conta\n"
            "3️⃣ Escolher o dia e horário que encaixam melhor na sua rotina\n\n"
            "Esse passo a passo é importante porque o prof. reserva um horário só para você, "
            "e queremos garantir que é uma pessoa real falando com a gente — não um robô 🤖.\n\n"
            "Assim, ele consegue preparar a aula com cuidado e te entregar uma experiência realmente personalizada."
        )

        teclado_cadastro = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✨ Criar meu cadastro",
                        web_app=WebAppInfo(
                            url="https://aulasdefrances.com/registro-alunos/"
                        ),
                    )
                ]
            ]
        )

        await query.message.reply_text(
            texto_aula,
            reply_markup=teclado_cadastro,
            disable_web_page_preview=True,
        )
        return

    # 3) Quando a pessoa escolhe um motivo
    if query.data.startswith("motivo_"):
        motivos_map = {
            "motivo_trabalho": "Trabalho",
            "motivo_viagem": "Viagem",
            "motivo_estudo": "Estudo / intercâmbio",
            "motivo_pessoal": "Interesse pessoal",
        }

        motivo_texto = motivos_map.get(query.data, "Outro")

        # Mensagem para o usuário
        texto_usuario = (
            f"Perfeito! 🎯\n\n"
            f"Vou te mostrar a plataforma pensando em *{motivo_texto}*.\n\n"
            f"Quando quiser, toque no botão abaixo para abrir a plataforma:"
        )

        botao_abrir_plataforma = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🌐 Abrir plataforma",
                        web_app=WebAppInfo(
                            url="https://www.aulasdefrances.com"
                        ),
                    )
                ]
            ]
        )

        await query.message.reply_text(
            texto_usuario,
            reply_markup=botao_abrir_plataforma,
            disable_web_page_preview=True,
        )

        # Resumo para o admin (se estiver configurado)
        if ADMIN_CHAT_ID:
            resumo = (
                "📥 *Novo interesse registrado*\n\n"
                f"*Usuário:* {user.first_name} "
                f"{'(@' + user.username + ')' if user.username else ''}\n"
                f"*ID:* `{user.id}`\n"
                f"*Motivo:* {motivo_texto}"
            )

            try:
                await context.bot.send_message(
                    chat_id=int(ADMIN_CHAT_ID),
                    text=resumo,
                    parse_mode="Markdown",
                )
            except Exception as e:
                print(f"Erro ao enviar resumo para o admin: {e}")

        return


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
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot rodando no Render...")
    app.run_polling()


if __name__ == "__main__":
    main()
