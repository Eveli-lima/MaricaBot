# 🤖 MaricáBot: Bot de Telegram com IA (Gemini)

Este é um projeto de um bot para o Telegram que utiliza a API Google Gemini (Gemini) para atuar como um assistente virtual focado exclusivamente na cidade de Maricá, RJ.

O bot é projetado para responder perguntas sobre pontos turísticos, serviços locais (como os horários dos "vermelhinhos"), números de emergência e qualquer outra informação relevante sobre a cidade.

## 🚀 Como Funciona

Este bot não depende apenas do conhecimento genérico da IA. Ele utiliza uma técnica chamada **RAG (Retrieval-Augmented Generation)**.

1.  **Base de Conhecimento:** Criamos um arquivo de texto (`conhecimento_marica.txt`) que serve como a "memória" ou "cérebro" do bot com informações precisas e verificadas sobre Maricá.
2.  **Contextualização:** Quando um usuário faz uma pergunta (ex: "Qual o telefone da Defesa Civil?"), o código Python primeiro lê o arquivo `conhecimento_marica.txt`.
3.  **Geração Aumentada:** O script então envia um prompt para a IA Gemini que inclui:
    * Todo o conteúdo do arquivo de texto (o contexto).
    * Uma instrução de sistema (ex: "Responda *apenas* com base neste contexto").
    * A pergunta do usuário.
4.  **Resposta Precisa:** A IA, forçada a usar apenas o contexto fornecido, localiza a informação correta no texto e formula uma resposta em linguagem natural para o usuário.

## 🛠️ Tecnologias e Bibliotecas Utilizadas

* **Python 3.x**: A linguagem de programação principal.
* **`python-telegram-bot`**: A biblioteca mais popular para interagir com a API do Telegram de forma fácil.
* **`google-generativeai`**: A biblioteca oficial do Google para se comunicar com a API do Gemini.
* **`python-dotenv`**: Uma biblioteca essencial de segurança para carregar "segredos" (como tokens de API) a partir de um arquivo `.env` em vez de escrevê-los diretamente no código.

---

## ⚙️ Guia de Instalação e Configuração

Siga este passo a passo para rodar o bot em sua própria máquina.

### 1. Pré-requisitos

Antes de começar, você precisará de:
* **Python 3.7+** instalado em sua máquina.
* Um **Token de Bot do Telegram**: Crie um bot no Telegram falando com o **@BotFather** e guarde o token que ele fornecer.
* Uma **API Key do Google Gemini**: Crie sua chave no [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Baixe os Arquivos do Projeto

Baixe os arquivos (`bot.py`, `conhecimento_marica.txt`, etc.) para uma pasta em seu computador.

### 3. Crie um Ambiente Virtual (Recomendado)

É uma boa prática isolar as bibliotecas do seu projeto.

```bash
# Crie um ambiente virtual chamado 'venv'
python -m venv venv

# Ative o ambiente virtual
# No Windows:
.\venv\Scripts\activate

# No macOS/Linux:
source venv/bin/activate
```
### 4. Crie o arquivo requirements.txt

Na pasta do seu projeto, crie um arquivo chamado ```requirements.txt``` e cole o seguinte conteúdo nele:

```bash
python-telegram-bot
google-generativeai
python-dotenv
```
### 5. Instale as Bibliotecas

Com o ambiente virtual ativado, rode o seguinte comando para instalar todas as bibliotecas de uma vez:

```Bash
pip install -r requirements.txt
```
### 6. Configure suas Chaves de API (Segurança)

Para manter seus tokens seguros, nunca os escreva diretamente no código.

1. Crie um arquivo na pasta principal chamado .env (começando com um ponto).

2. Dentro do arquivo .env, cole o seguinte, substituindo pelos seus tokens:
- DICA IMPORTANTE: cole os TOKEN e a API a partir da segunda linha do arquivo .env, pois da primeira linha pode não funcionar.

    ```Bash
    TELEGRAM_TOKEN="SEU_TOKEN_AQUI_DO_BOTFATHER"
    GEMINI_API_KEY="SUA_API_KEY_AQUI_DO_GOOGLE_AI"
    ```

3. IMPORTANTE: Se você usa Git (como o GitHub), crie também um arquivo chamado .gitignore e adicione .env a ele. Isso evitará que seus segredos sejam enviados para a internet.

### 7. Personalize a Base de Conhecimento

Abra o arquivo ```conhecimento_marica.txt``` e adicione/edite as informações que você quer que seu bot saiba. Quanto mais detalhado este arquivo, mais inteligente será o seu bot.

### 8. Rode o Bot!

Finalmente, execute o script principal do bot:

```Bash

python bot.py
```

Se tudo estiver correto, você verá uma mensagem no seu terminal dizendo "Iniciando o bot...". Agora, abra o Telegram, encontre seu bot e comece a conversar!