import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Lê o TOKEN da variável de ambiente (que vamos configurar no Render)
TOKEN = os.getenv("TOKEN")


# /start – mensagem inicial + botões
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_inicial = (
        "Bonjour! 🇫🇷\n\n"
        "Antes de começar, entre no grupo oficial da plataforma para receber avisos, conteúdos e suporte:\n"
        "👉 https://t.me/+0KMPSFwjfiZkM2Qx\n\n"
        "Depois, escolha uma opção abaixo:"
    )

    botoes = [
        [InlineKeyboardButton("🌐 Conhecer a plataforma", callback_data="menu1")],
        [InlineKeyboardButton("📊 Teste de nivelamento grátis", callback_data="menu2")],
        [InlineKeyboardButton("⭐ Sobre o Prof. Yann", callback_data="menu3")],
        [InlineKeyboardButton("📅 Agendar Aula experimental grátis", callback_data="menu4")],
        [InlineKeyboardButton("🔑 Já sou Aluno – Fazer Login", callback_data="menu5")],
    ]

    teclado = InlineKeyboardMarkup(botoes)

    if update.message:
        await update.message.reply_text(
            texto_inicial,
            reply_markup=teclado,
            disable_web_page_preview=True,
        )


# Handler dos cliques nos botões
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu1":
        texto = (
            "🇫🇷 Acesse agora a plataforma completa com 3.000+ livros, audiobooks, "
            "módulos A1-C2 e exercícios interativos! Comece sua jornada de imersão no francês:\n\n"
            "https://www.aulasdefrances.com"
        )

    elif query.data == "menu2":
        texto = (
            "📊 Teste seu francês agora e receba feedback personalizado do Prof. Yann! "
            "Avaliamos sua compreensão, pronúncia e escrita para criar um plano de estudos à sua medida:\n\n"
            "https://aulasdefrances.com/teste-de-nivelamento-de-frances/"
        )

    elif query.data == "menu3":
        texto = (
            "👨‍🏫 Conheça Prof. Yann: professor nativo francês com 10+ anos de experiência, "
            "especializado em imersão pedagógica e metodologia moderna. "
            "Saiba por que seus alunos adoram aprender com ele:\n\n"
            "https://aulasdefrances.com/professor-nativo-de-frances-yann-amoussou/"
        )

    elif query.data == "menu4":
        texto = (
            "✨ Aula grátis para conhecer Prof. Yann! Reserve seu horário, "
            "conheça sua metodologia e saia com um plano de estudos personalizado só para você:\n\n"
            "https://aulasdefrances.com/registro-alunos/"
        )

    elif query.data == "menu5":
        texto = (
            "🔑 Bem-vindo de volta! Acesse sua conta, visualize seu progresso, "
            "consulte materiais e acompanhe suas aulas agendadas:\n\n"
            "https://aulasdefrances.com/login-alunos/"
        )
    else:
        texto = "Ops, opção inválida. Tente novamente."

    # Envia a mensagem sem apagar o menu
    await query.message.reply_text(texto)


def main():
    if not TOKEN:
        raise RuntimeError("TOKEN não encontrado. Configure a variável de ambiente TOKEN no Render.")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_menu))

    print("Bot rodando no Render...")
    # Aqui o python-telegram-bot cuida do asyncio pra gente
    app.run_polling()


if __name__ == "__main__":
    main()

