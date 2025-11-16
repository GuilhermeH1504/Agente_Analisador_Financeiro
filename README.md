🤖 Agente de Análise Financeira (AI Finance Agent)
Um Agente de IA avançado construído com LangGraph para automatizar a leitura, processamento e análise de extratos financeiros em diversos formatos (PDF, CSV e OFX), fornecendo resumos e dicas de economia.

🌟 Funcionalidades
Leitura Multi-Formato: Processa extratos em PDF, CSV e OFX.

Análise Estruturada: Utiliza a biblioteca pandas (no caso do OFX) para estruturar transações.

Orquestração Inteligente: Emprega LangGraph para gerenciar o fluxo de trabalho de tomada de decisão, garantindo que o LLM chame a ferramenta correta no momento certo.

Consultoria Financeira: Gera resumos, totaliza receitas/despesas e oferece dicas de economia personalizadas.

Flexibilidade de LLM: Atualmente configurado para usar o Groq (para velocidade) ou Gemini (para inteligência).

🛠️ Tecnologias Utilizadas
O projeto é construído em Python e utiliza as seguintes bibliotecas principais:

LangChain / LangGraph: Orquestração do agente e fluxo de trabalho.

Groq / Gemini: Motores de Linguagem Grande (LLM) para raciocínio e análise.

PyPDFLoader / CSVLoader: Carregamento de dados PDF e CSV.

ofxparse / pandas: Leitura e estruturação de extratos OFX.

python-dotenv: Gerenciamento de chaves de API.

🚀 Instalação e Configuração
Siga estes passos para configurar e executar o agente em sua máquina.

1. Clonar o Repositório
Bash

git clone [SUA_URL_DO_REPOSITÓRIO]
cd [NOME_DO_SEU_REPOSITÓRIO]
2. Instalar Dependências
Crie e ative um ambiente virtual (opcional, mas recomendado) e instale as bibliotecas necessárias.

Bash

pip install -r requirements.txt
# Ou instale manualmente:
# pip install langchain-groq langchain-google-genai langgraph pydantic python-dotenv pandas ofxparse
3. Configurar Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto e adicione suas chaves de API:

# Se usar Groq (configuração atual do código)
GROQ_API_KEY="SUA_CHAVE_GROQ_AQUI"

# OU se for usar Gemini
# GOOGLE_API_KEY="SUA_CHAVE_GOOGLE_AQUI"
4. Configurar a Pasta de Extratos
O agente está configurado para ler arquivos em um diretório específico. Crie a pasta e coloque seus extratos lá:

# Crie esta pasta (ou ajuste o caminho na constante PASTA_EXTRATOS no código)
C:\Users\55319\Documents\extratos
💡 Como Usar
Execute o arquivo principal do projeto:

Bash

python seu_arquivo_principal.py # Troque pelo nome do seu arquivo, ex: main.py
Você verá o prompt de interação.

Inicie a Conversa: Peça ao agente para analisar seus arquivos.

Exemplo: Analise meus extratos bancários e me diga onde gastei mais este mês.

Agente e Tools: O agente reconhecerá a necessidade de dados e chamará as ferramentas (loader_pdf, loader_csv, ou loader_ofx).

Análise e Resumo: O LLM processará os dados retornados pelas tools e fornecerá o resumo e as dicas conforme o SYSTEM_PROMPT.

Encerrar: Digite sair ou quit para finalizar o programa.

🗺️ Estrutura do Grafo
O LangGraph orquestra o agente através de um fluxo de trabalho de três nós:

call_llm: O LLM recebe a pergunta, raciocina e decide: chamar uma tool ou dar a resposta final?

router: Função condicional que verifica a saída do LLM.

execute_tools: Executa a ferramenta solicitada (ex: loader_ofx) e devolve o resultado para o call_llm para análise.

👤 Contribuição
Contribuições são bem-vindas! Se você tiver sugestões, bug reports ou melhorias no processamento de arquivos, sinta-se à vontade para abrir uma Issue ou enviar um Pull Request.
