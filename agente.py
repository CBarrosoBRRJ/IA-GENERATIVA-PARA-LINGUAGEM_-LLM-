from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings

import os, yaml, fitz


# ================================
# Configuração
# ================================

CONFIG_FILE = "config.yaml"
with open(CONFIG_FILE, "r") as file:
    config = yaml.safe_load(file)

os.environ["GROQ_API_KEY"] = config["api_key"]["key"]

modelo_llm = ChatGroq(
    model=config["model"]["name"],  
    temperature=config["model"].get("temperature", 0.7),
    groq_api_key=config["api_key"]["key"]
)

print(f"✅ Usando modelo: {config['model']['name']}")



modelo_embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")



# ======================
# CARREGAR PDFs
# ======================
def carregar_documentos_pdf(pasta="data"):
    documentos = []
    if not os.path.exists(pasta):
        raise FileNotFoundError(f"Pasta '{pasta}' não encontrada.")
    
    for nome_arquivo in os.listdir(pasta):
        if nome_arquivo.lower().endswith(".pdf"):
            caminho = os.path.join(pasta, nome_arquivo)
            try:
                doc_pdf = fitz.open(caminho)
                conteudo = "".join([pagina.get_text() for pagina in doc_pdf])
                if conteudo.strip():
                    documentos.append(Document(
                        page_content=conteudo,
                        metadata={"fonte": nome_arquivo}
                    ))
                    print(f"📄 Documento carregado: {nome_arquivo}")
                else:
                    print(f"⚠️ Documento vazio: {nome_arquivo}")
            except Exception as e:
                print(f"❌ Erro ao ler '{nome_arquivo}': {e}")
    
    return documentos

documentos = carregar_documentos_pdf()

if not documentos:
    raise ValueError("❌ Nenhum documento carregado. Verifique a pasta 'data/'.")


# ======================
# CRIAR BASE VETORIAL
# ======================

print("🔍 Gerando embeddings e base vetorial...")
base_vetorial = FAISS.from_documents(documentos, modelo_embedding)

# ======================
# PROMPT
# ======================

template_prompt = """
Você é um assistente médico. Use o seguinte contexto extraído da base para responder:

{melhores_praticas}

Histórico da Conversa:
{historico}

Pergunta Atual: {mensagem}
"""

prompt = PromptTemplate(
    input_variables=['mensagem', 'melhores_praticas', 'historico'],
    template=template_prompt
)

cadeia = LLMChain(llm=modelo_llm, prompt=prompt)

# ======================
# FUNÇÃO PRINCIPAL
# ======================

def gerar_resposta(mensagem, conversa_historico):
    """
    Gera resposta com base no histórico e na base vetorial.
    
    Parâmetros:
    - mensagem: str -> pergunta atual.
    - conversa_historico: list[str] -> histórico da conversa.

    Retorna:
    - resposta: str
    """
    try:
        docs = base_vetorial.similarity_search(mensagem, k=10)
        melhores_praticas = [f"[Fonte: {d.metadata.get('fonte', 'desconhecida')}]\n{d.page_content[:1000]}" for d in docs]

        historico_formatado = "\n".join(conversa_historico)

        resposta = cadeia.run(
            mensagem=mensagem,
            melhores_praticas="\n\n".join(melhores_praticas),
            historico=historico_formatado
        )

        return resposta
    
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"
