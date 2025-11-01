import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import os
from dotenv import load_dotenv
import json

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# --- Configuração ---
# Puxa os tokens do ambiente. O .get() retorna 'None' se não encontrar.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TELEGRAM_TOKEN:
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


# Instrução de sistema para a IA
instrucao_sistema = (
    "Você é o 'MaricáBot', um assistente virtual focado exclusivamente na cidade de Maricá, RJ. "
    "Sua única função é responder perguntas sobre turismo, serviços e informações locais de Maricá. "
    "Responda em formato HTML, mas use APENAS as tags <b>, <i>, <u>, <code>. Não use <p> ou <div>."
    "Se a pergunta não for sobre Maricá, recuse educadamente e lembre o usuário do seu propósito."
)

model = genai.GenerativeModel(
    'gemini-2.5-flash', # Usando o modelo que você definiu
    system_instruction=instrucao_sistema 
)

# Configura a API do Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Tenta carregar a base de conhecimento
try:
    # Usa 'utf-8-sig' para ignorar o "BOM" invisível
    with open('conhecimento.json', 'r', encoding='utf-8-sig') as f:
        CONHECIMENTO_MARICA = json.load(f)
    logger.info("Base de conhecimento 'conhecimento.json' carregada com sucesso.")
except FileNotFoundError:
    logger.error("ERRO: Arquivo 'conhecimento.json' não encontrado!")
    CONHECIMENTO_MARICA = {} # Começa com um dicionário vazio se falhar
except json.JSONDecodeError:
    logger.error("ERRO: O arquivo 'conhecimento.json' tem um erro de sintaxe!")
    CONHECIMENTO_MARICA = {}


# --- Funções do Bot ---

# Função para o comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem de boas-vindas quando o comando /start é emitido."""
    user = update.effective_user
    await update.message.reply_html(
        f"Olá, {user.mention_html()}! 👋\n\nEu sou o MaricáBot, seu assistente virtual para a cidade."
    )

# 
# --- ESTA É A FUNÇÃO ATUALIZADA ---
# 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lida com mensagens de texto, usando a base de conhecimento local (RAG)"""
    user_message = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    # --- Lógica do RAG (Atualizada) ---
    contexto_para_ia = json.dumps(CONHECIMENTO_MARICA, indent=2, ensure_ascii=False)

    # Montamos o "mega-prompt" para a IA
    prompt_para_ia = (
        f"**Contexto (armazenado em JSON):**\n"
        f"--- INÍCIO DO CONTEXTO ---\n"
        f"{contexto_para_ia}\n"
        f"--- FIM DO CONTEXTO ---\n\n"
        f"**Regra:** Use *apenas* as informações do contexto acima para responder.\n"
        f"**Pergunta do Usuário:** {user_message}\n\n"
        f"**Resposta (em formato HTML, usando <a> para links e <b>, <i>, <code>, <u> para formatação. Não use <p> ou <br>):**" # Instrução reforçada
    )
    # --- Fim da Lógica do RAG ---

    try:
        response = model.generate_content(prompt_para_ia)

        if response.candidates and response.candidates[0].content.parts:
            
            raw_text = response.text
            cleaned_text = raw_text.replace("<p>", "").replace("</p>", "\n")
            cleaned_text = cleaned_text.replace("<br>", "\n").replace("<br />", "\n")
            
            await update.message.reply_text(
                cleaned_text, # <--- Enviamos o texto limpo
                parse_mode='HTML' # Mantenha em HTML, é mais seguro!
            )
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

