# ============================================================================
# IMPORTAÇÕES DE BIBLIOTECAS
# ============================================================================

import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import CSVLoader
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Sequence, Literal, Annotated, List
from langchain_core.tools import tool, BaseTool
from langchain_core.messages import BaseMessage, ToolMessage
from dotenv import load_dotenv
import os
import json
import pandas as pd
import ofxparse
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================

logging.basicConfig(
    filename="AIFinance.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)                                                                                                                                                                                                                                                                                                                                                 

# ============================================================================
# CONSTANTES
# ============================================================================

PASTA_EXTRATOS = 'C:\\Users\\55319\\Documents\\extratos'

# ============================================================================
# DEFINIÇÃO DO ESTADO DO AGENTE
# ============================================================================

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# ============================================================================
# FERRAMENTAS (TOOLS) - Funções que o LLM pode chamar
# ============================================================================

@tool
def loader_pdf(file_path: str = PASTA_EXTRATOS) -> list:
    """Carrega um extrato em formato PDF e retorna o conteúdo do extrato.
        Args:
            file_path: str = Caminho do diretorio onde estão os extratos.
        Returns:
            str: O conteúdo do extrato em formato de texto.
    """
    try:
        extratos = []
        for file in os.listdir(file_path):
            if file.endswith(".pdf"):
                caminho = os.path.join(file_path, file)
                logging.info(f"Processando arquivo. '{file}'")
                loader = PyPDFLoader(caminho)
                pages = loader.load()

                texto_extrato = "\n".join(p.page_content for p in pages)
                extratos.append(texto_extrato)
                print(extratos)

        if extratos:
            return "\n\n".join(extratos)
        if not extratos:
            logging.error(f"Nenhum arquivo foi encontrado")

    except FileNotFoundError:
        logging.error(f"Caminho do arquivo PDF não localizado.{file_path}")

@tool
def loader_csv(file_path: str = PASTA_EXTRATOS) -> str:
    """Carrega arquivos CSV e retorna o conteúdo como texto."""
    try:
        extrato_csv = []
        for file in os.listdir(file_path):
            if file.endswith(".csv"):
                caminho = os.path.join(file_path, file)
                logging.info(f"Processando arquivo CSV: '{file}'")
                loader = CSVLoader(caminho)
                docs = loader.load()
                csv = "\n".join(p.page_content for p in docs)
                extrato_csv.append(csv)

        if extrato_csv:
            return "\n\n".join(extrato_csv)
        else:
            logging.warning("Nenhum arquivo CSV encontrado.")
            return "Nenhum arquivo CSV encontrado."

    except Exception as e:
        logging.error(f"Erro ao processar CSV: {e}")
        return str(e)
        
@tool
def loader_ofx(file_path: str = PASTA_EXTRATOS):
    """Carrega um extrato em formato OFX e retorna o conteúdo do extrato."""
    try:
        if not os.path.exists(file_path):
            logging.error(f"Pasta não encontrada: {file_path}")
            print(f"❌ Pasta não encontrada: {file_path}")
            return None

        arquivos = os.listdir(file_path)
        print(f"📂 Arquivos encontrados na pasta: {arquivos}")

        df = pd.DataFrame()
        arquivos_ofx = [a for a in arquivos if a.lower().endswith(".ofx")]

        if not arquivos_ofx:
            logging.warning("Nenhum arquivo OFX encontrado.")
            print("⚠️ Nenhum arquivo OFX encontrado.")
            return None

        for arquivo in arquivos_ofx:
            caminho = os.path.join(file_path, arquivo)
            logging.info(f"Processando arquivo OFX: '{arquivo}'")
            print(f"🔄 Lendo arquivo: {arquivo}")

            with open(caminho, encoding='UTF-8') as ofx_file:
                ofx = ofxparse.OfxParser.parse(ofx_file)

            transactions_data = []
            for account in ofx.accounts:
                for transaction in account.statement.transactions:
                    transactions_data.append({
                        "Data": transaction.date,
                        "Valor": transaction.amount,
                        "Descrição": transaction.memo,
                        "ID": transaction.id,
                    })

            if transactions_data:
                df_temp = pd.DataFrame(transactions_data)
                df_temp["Data"] = df_temp["Data"].apply(lambda x: x.date())
                df_temp["Valor"] = df_temp["Valor"].astype(float)
                df = pd.concat([df, df_temp], ignore_index=True)

        if not df.empty:
            print("✅ Arquivos processados com sucesso:")
            print(df.head())
            return df.to_string(index=False)
        else:
            logging.warning("Nenhuma transação processada.")
            print("⚠️ Nenhuma transação encontrada nos arquivos.")
            return None

    except FileNotFoundError as e:
        logging.error(f"Erro ao processar arquivo OFX: {e}")
        print(f"❌ Erro: {e}")
    except Exception as e:
        logging.error(f"Erro inesperado ao processar arquivo OFX: {e}")
        print(f"❌ Erro inesperado: {e}")


# ============================================================================
# FUNÇÕES DO GRAFO DE ESTADO (State Graph)
# ============================================================================

def call_llm(state: AgentState) -> AgentState:
    print(">call_llm")
    llm = ChatGroq(
        model= "openai/gpt-oss-20b",
        groq_api_key='(SUA CHAVE API AQUI)'
    )

    SYSTEM_PROMPT = SystemMessage(
        "Você é um **assistente financeiro inteligente**. Seu papel é ajudar o usuário a entender e organizar suas finanças pessoais ou empresariais.\n\n"
        "### Suas tarefas:\n"
        "1. Identifique o tipo de extrato (PDF, CSV ou OFX) e chame a ferramenta correspondente.\n"
        "2. Extraia os dados e organize em um **DataFrame Pandas**, com as colunas:\n"
        "   - Data\n"
        "   - Descrição\n"
        "   - Valor\n"
        "   - Categoria (ex: Alimentação, Transporte, Terceiros, Lazer, etc)\n"
        "3. Gere um **resumo financeiro** contendo:\n"
        "   - Total de receitas e despesas\n"
        "   - Total por categoria\n"
        "   - Dicas de economia e padrões observados\n\n"
        "### Regras importantes:\n"
        "- Sempre chame as ferramentas (`loader_pdf`, `loader_csv`, `loader_ofx`) quando necessário.\n"
        "- Se não houver dados disponíveis, informe claramente o usuário.\n"
        "- Use um tom analítico e amigável, como um consultor financeiro.\n"
        "- Retorne os resultados de forma legível e organizada (tabelas, listas, resumo textual)."
        "- Não precisa retornar os extras nas respostas"
    )
    TOOLS: List[BaseTool] = [loader_pdf, loader_csv, loader_ofx]
    llm_with_tools = llm.bind_tools(TOOLS)
    messages_to_llm = [SYSTEM_PROMPT] + state["messages"]
    llm_result = llm_with_tools.invoke(messages_to_llm)

    return {
        "messages": llm_result
    }

def execute_tools(state: AgentState) -> AgentState:
    """Executa as ferramentas chamadas pelo LLM"""

    print("> tool node")
    
    llm_response = state["messages"][-1]
    if not isinstance(llm_response, AIMessage) or not getattr(
        llm_response, "tool_calls", None
    ):
        return state

    tools_map = {
        "loader_pdf": loader_pdf,
        "loader_csv": loader_csv,
        "loader_ofx": loader_ofx
    }

    tool_messages = []
    for call in llm_response.tool_calls:
        name, args, id = call["name"], call["args"], call["id"]

        try:
            if name in tools_map:
                content = tools_map[name].invoke(args)
                status = "success"
            else:
                content = f"Ferramenta '{name}' não encontrada"
                status = "error"
        except (KeyError, IndexError, FileNotFoundError, ValueError) as error:
            content = f"Erro ao executar ferramenta: '{error}'"
            status = "error"

        tool_message = ToolMessage(content=str(content), tool_call_id=id, status=status)
        tool_messages.append(tool_message)

    return {
        "messages": tool_messages
    }

def router(state: AgentState) -> Literal["execute_tools", "END"]:
    """Roteia para o próximo nó baseado na última mensagem"""
    print("> router")
    llm_response = state["messages"][-1]

    if getattr(llm_response, "tool_calls", None):
        return "execute_tools"
    return "END"

# ============================================================================
# CONSTRUÇÃO DO GRAFO DE ESTADO
# ============================================================================

builder = StateGraph(AgentState)

builder.add_node("call_llm", call_llm)
builder.add_node("execute_tools", execute_tools)

builder.set_entry_point("call_llm")

builder.add_conditional_edges(
    "call_llm",
    router,
    {
        "execute_tools": "execute_tools",
        "END": END
    }
)

builder.add_edge("execute_tools", "call_llm")

graph = builder.compile()
graph.get_graph().draw_mermaid_png(output_file_path="ark.png")

# ============================================================================
# PROGRAMA PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    while True:
        user_input = input("👤 Você: ")

        if user_input.lower() in ['q', 'quit', 'sair']:
            logging.info("Encerrando call com a llm")
            print("Ate mais")
            break

        initial_state = {"messages":[HumanMessage(content=user_input)]}

        result = graph.invoke(initial_state)

        print("-" * 20)
        final_answer = result['messages'][-1].content
        print(f"🤖 AI: {final_answer}")

