import os
import threading
import http.server
import socketserver
from datetime import datetime  # para registrar horário

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

    # --------- Informação extra para o admin --------- #
    # 1) Origem (payload do deep link: /start origem)
    payload = None
    if update.message and update.message.text:
        partes = update.message.text.split(maxsplit=1)
        if len(partes) > 1:
            payload = partes[1].strip()
    origem = payload if payload else "Não informada"

    # 2) Idioma do Telegram do usuário
    idioma = user.language_code if user.language_code else "desconhecido"

    # 3) Status: primeira vez ou recorrente (na memória do bot)
    known_users = context.bot_data.setdefault("known_users", set())
    primeira_vez = user.id not in known_users
    known_users.add(user.id)
    status = "Primeira vez" if primeira_vez else "Usuário recorrente"

    # 4) Link direto pro usuário (se tiver username)
    if user.username:
        link_usuario = f"https://t.me/{user.username}"
    else:
        link_usuario = "Sem username – responda direto ao chat no Telegram."

    # 5) Horário de início
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Notificação para o admin sempre que alguém iniciar o bot
    if ADMIN_CHAT_ID:
        resumo_inicio = (
            "🚀 Novo início de conversa com o bot\n\n"
            f"Usuário: {user.first_name} "
            f"{'(@' + user.username + ')' if user.username else ''}\n"
            f"ID: {user.id}\n"
            f"Idioma no Telegram: {idioma}\n"
            f"Origem (payload /start): {origem}\n"
            f"Status: {status}\n"
            f"Início (horário do servidor): {start_time}\n"
            f"Link: {link_usuario}"
        )
        print(f"Tentando enviar aviso de início para o admin ({ADMIN_CHAT_ID})")
        try:
            await context.bot.send_message(
                chat_id=int(ADMIN_CHAT_ID),
                text=resumo_inicio,
            )
        except Exception as e:
            print(f"Erro ao enviar aviso de início para o admin: {e}")

    # --------- Mensagem inicial para o usuário --------- #
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
                "📘 Ver Livro do professor",
                web_app=WebAppInfo(
                    url="https://aulasdefrances.com/#t7ymfy4g/1"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                "🎯 Prova DELF / DALF / DILF",
                callback_data="provas_delf_dalf_dilf",
            )
        ],
        [
            InlineKeyboardButton(
                "📅 Agendar Aula experimental grátis",
                callback_data="agendar_aula",
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
                url="https://wa.me/5562996263600",
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
            "✨ Sua aula experimental grátis é um momento exclusivo entre você e o Prof. Yann.\n\n"
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

        # Notificação automática para o admin
        if ADMIN_CHAT_ID:
            resumo = (
                "📥 Novo interesse em AULA EXPERIMENTAL\n\n"
                f"Usuário: {user.first_name} "
                f"{'(@' + user.username + ')' if user.username else ''}\n"
                f"ID: {user.id}"
            )
            print(f"Tentando enviar resumo de aula experimental para o admin ({ADMIN_CHAT_ID})")
            try:
                await context.bot.send_message(
                    chat_id=int(ADMIN_CHAT_ID),
                    text=resumo,
                )
            except Exception as e:
                print(f"Erro ao enviar resumo de aula experimental para o admin: {e}")

        return

    # 3) Menu de provas DELF/DALF/DILF – pergunta qual prova
    if query.data == "provas_delf_dalf_dilf":
        texto_exames = (
            "🎯 Que legal que você está de olho em certificação oficial de francês!\n\n"
            "Seu foco está em qual prova?\n\n"
            "🇫🇷 DELF – níveis A1 a B2\n"
            "🇫🇷 DALF – níveis C1 e C2\n"
            "🇫🇷 DILF – nível inicial A1.1\n\n"
            "Escolha uma opção:"
        )

        botoes_exames = [
            [InlineKeyboardButton("DELF", callback_data="exame_delf")],
            [InlineKeyboardButton("DALF", callback_data="exame_dalf")],
            [InlineKeyboardButton("DILF", callback_data="exame_dilf")],
        ]

        teclado_exames = InlineKeyboardMarkup(botoes_exames)

        await query.message.reply_text(
            texto_exames,
            reply_markup=teclado_exames,
        )
        return

    # 4) Escolha do exame → pergunta nível correspondente
    if query.data == "exame_delf":
        texto_nivel = (
            "Ótimo! 🇫🇷 Prova DELF.\n\n"
            "Qual nível é do seu interesse?\n\n"
            "A1 • A2 • B1 • B2"
        )

        botoes_nivel = [
            [InlineKeyboardButton("DELF A1", callback_data="nivel_delf_a1")],
            [InlineKeyboardButton("DELF A2", callback_data="nivel_delf_a2")],
            [InlineKeyboardButton("DELF B1", callback_data="nivel_delf_b1")],
            [InlineKeyboardButton("DELF B2", callback_data="nivel_delf_b2")],
        ]

        await query.message.reply_text(
            texto_nivel,
            reply_markup=InlineKeyboardMarkup(botoes_nivel),
        )
        return

    if query.data == "exame_dalf":
        texto_nivel = (
            "Perfeito! 🇫🇷 Prova DALF.\n\n"
            "Qual nível é do seu interesse?\n\n"
            "C1 • C2"
        )

        botoes_nivel = [
            [InlineKeyboardButton("DALF C1", callback_data="nivel_dalf_c1")],
            [InlineKeyboardButton("DALF C2", callback_data="nivel_dalf_c2")],
        ]

        await query.message.reply_text(
            texto_nivel,
            reply_markup=InlineKeyboardMarkup(botoes_nivel),
        )
        return

    if query.data == "exame_dilf":
        texto_nivel = (
            "Excelente! 🇫🇷 Prova DILF.\n\n"
            "Atualmente o foco é no nível inicial:\n\n"
            "A1.1 – primeira etapa para quem está começando do zero."
        )

        botoes_nivel = [
            [InlineKeyboardButton("DILF A1.1", callback_data="nivel_dilf_a11")],
        ]

        await query.message.reply_text(
            texto_nivel,
            reply_markup=InlineKeyboardMarkup(botoes_nivel),
        )
        return

    # 5) Nível escolhido → manda link + avisa o professor
    if query.data.startswith("nivel_"):
        niveis_map = {
            "nivel_delf_a1": ("DELF", "A1"),
            "nivel_delf_a2": ("DELF", "A2"),
            "nivel_delf_b1": ("DELF", "B1"),
            "nivel_delf_b2": ("DELF", "B2"),
            "nivel_dalf_c1": ("DALF", "C1"),
            "nivel_dalf_c2": ("DALF", "C2"),
            "nivel_dilf_a11": ("DILF", "A1.1"),
        }

        exame, nivel = niveis_map.get(query.data, ("Prova desconhecida", "Nível desconhecido"))

        texto_final = (
            "Perfeito! 🎓\n\n"
            f"Anotei que seu foco é na prova {exame} nível {nivel}.\n\n"
            "No link abaixo você encontra mais informações sobre as provas "
            "e como se preparar com o Prof. Yann:"
        )

        teclado_prova = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📚 Ver detalhes das provas",
                        web_app=WebAppInfo(
                            url="https://aulasdefrances.com/delf-dalf/"
                        ),
                    )
                ]
            ]
        )

        await query.message.reply_text(
            texto_final,
            reply_markup=teclado_prova,
            disable_web_page_preview=True,
        )

        # Notificação para o admin
        if ADMIN_CHAT_ID:
            resumo = (
                "📥 Novo interesse em PROVA OFICIAL\n\n"
                f"Usuário: {user.first_name} "
                f"{'(@' + user.username + ')' if user.username else ''}\n"
                f"ID: {user.id}\n"
                f"Prova: {exame}\n"
                f"Nível: {nivel}"
            )
            print(f"Tentando enviar resumo de prova para o admin ({ADMIN_CHAT_ID})")
            try:
                await context.bot.send_message(
                    chat_id=int(ADMIN_CHAT_ID),
                    text=resumo,
                )
            except Exception as e:
                print(f"Erro ao enviar resumo de prova para o admin: {e}")

        return

    # 6) Quando a pessoa escolhe um motivo para conhecer a plataforma
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
            "Perfeito! 🎯\n\n"
            f"O Prof. Yann já acompanhou muitos alunos cujo foco principal era: {motivo_texto}.\n"
            "Nossa plataforma tem toda a estrutura para que você aprenda de verdade, "
            "com materiais organizados, prática guiada e acompanhamento profissional.\n\n"
            "Quando quiser, toque no botão abaixo para abrir a plataforma.\n"
            "Se fizer sentido para você, aproveite e agende também a sua aula experimental grátis. ✨"
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
                "📥 Novo interesse em CONHECER A PLATAFORMA\n\n"
                f"Usuário: {user.first_name} "
                f"{'(@' + user.username + ')' if user.username else ''}\n"
                f"ID: {user.id}\n"
                f"Motivo: {motivo_texto}"
            )
            print(f"Tentando enviar resumo de motivo para o admin ({ADMIN_CHAT_ID})")
            try:
                await context.bot.send_message(
                    chat_id=int(ADMIN_CHAT_ID),
                    text=resumo,
                )
            except Exception as e:
                print(f"Erro ao enviar resumo de motivo para o admin: {e}")

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
