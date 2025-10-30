import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# --- Configuração ---
# Puxa os tokens do ambiente. O .get() retorna 'None' se não encontrar.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_TOKEN:
    # Use 'logger.error' se o logger já estiver definido, 
    # ou 'print' se for antes da configuração do logger.
    print("ERRO: Variável de ambiente TELEGRAM_TOKEN não encontrada.")
    exit() # Para o script

if not GEMINI_API_KEY:
    print("ERRO: Variável de ambiente GEMINI_API_KEY não encontrada.")
    exit() # Para o script

# Configura o logging (bom para depuração)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# model = genai.GenerativeModel('gemini-2.5-flash')
instrucao_sistema = (
    "Você é o 'MaricáBot', um assistente virtual focado exclusivamente na cidade de Maricá, RJ. "
    "Sua única função é responder perguntas sobre turismo, serviços e informações locais de Maricá. "
    "Se a pergunta não for sobre Maricá, recuse educadamente e lembre o usuário do seu propósito."
)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=instrucao_sistema 
)

# Configura a API do Gemini
genai.configure(api_key=GEMINI_API_KEY)

try:
    with open('conhecimento_marica.txt', 'r', encoding='utf-8') as f:
        CONHECIMENTO_MARICA = f.read()
    logger.info("Base de conhecimento 'conhecimento_marica.txt' carregada.")
except FileNotFoundError:
    logger.error("ERRO: Arquivo 'conhecimento_marica.txt' não encontrado!")
    CONHECIMENTO_MARICA = "Nenhuma informação local encontrada."


# --- Funções do Bot ---

# Função para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem de boas-vindas quando o comando /start é emitido."""
    user = update.effective_user
    await update.message.reply_html(
        f"Olá, {user.mention_html()}! 👋\n\nEu sou um bot com IA. Envie-me qualquer pergunta!"
    )

# Função para lidar com mensagens de texto (aqui está a IA)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lida com mensagens de texto, usando a base de conhecimento local (RAG)"""
    user_message = update.message.text
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # --- Lógica do RAG ---
    # Montamos um "mega-prompt" para a IA
    prompt_para_ia = (
        f"**Contexto da Cidade de Maricá:**\n"
        f"--- INÍCIO DO CONTEXTO ---\n"
        f"{CONHECIMENTO_MARICA}\n"
        f"--- FIM DO CONTEXTO ---\n\n"
        f"**Regra:** Use *apenas* as informações do contexto acima para responder.\n"
        f"**Pergunta do Usuário:** {user_message}\n\n"
        f"**Resposta:**"
    )
    # --- Fim da Lógica do RAG ---

    try:
        # Nota: Não estamos usando o 'chat.send_message()' aqui
        # Estamos usando o 'generate_content' para enviar um prompt único
        # Isso evita que o "contexto" fique no histórico para sempre
        response = model.generate_content(prompt_para_ia)
        
        # Verificação de segurança (como fizemos antes)
        if response.candidates and response.candidates[0].content.parts:
            await update.message.reply_text(response.text)
        else:
            logger.warning(f"Resposta da IA bloqueada. Feedback: {response.prompt_feedback}")
            await update.message.reply_text("Não consegui gerar uma resposta para isso. Tente perguntar de outra forma.")
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem (RAG): {e}")
        await update.message.reply_text("Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.")

# --- Função Principal para Iniciar o Bot ---
def main() -> None:
    """Inicia o bot."""
    # Cria o 'Application' e passa o token do bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Adiciona 'handlers' para diferentes comandos e mensagens
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Inicia o bot (ele fica "ouvindo" por novas mensagens)
    logger.info("Iniciando o bot...")
    application.run_polling()

if __name__ == "__main__":
    main()