import streamlit as st
import pandas as pd
import json
from PyPDF2 import PdfReader
from langchain.docstore.document import Document
from agente import gerar_resposta, base_vetorial

# ===============================
# Inicializar sessão
# ===============================
if "chat_historico" not in st.session_state:
    st.session_state["chat_historico"] = []

if "pergunta_exemplo" not in st.session_state:
    st.session_state["pergunta_exemplo"] = None

# ===============================
# Funções auxiliares
# ===============================
def carregar_texto_pdf(uploaded_pdf):
    reader = PdfReader(uploaded_pdf)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    return texto

def carregar_texto_csv(uploaded_csv):
    df = pd.read_csv(uploaded_csv)
    return df.to_string()

def carregar_texto_excel(uploaded_excel):
    df = pd.read_excel(uploaded_excel)
    return df.to_string()

def exportar_historico_txt(historico):
    return "\n".join(f"{role.upper()}: {msg}" for role, msg in historico)

def exportar_historico_json(historico):
    return json.dumps(historico, indent=2, ensure_ascii=False)

def exibir_conversa():
    for role, msg in st.session_state["chat_historico"]:
        with st.chat_message(role):
            st.markdown(msg)

# ===============================
# Sidebar – Upload, Exemplos e Exportação
# ===============================
st.sidebar.title("🩺 Dr. Chicó – Assistente Médico")

st.sidebar.markdown("""
Converse com o **Dr. Chicó**, assistente de IA especializado em anestesiologia.

💬 Temas sugeridos:
- Técnicas anestésicas
- Reações fisiológicas
- Riscos e complicações
- Casos clínicos
""")

# Categorias de perguntas
with st.sidebar.expander("💡 Conceitos Básicos", expanded=False):
    st.markdown("Exemplos sobre conceitos fundamentais de anestesia.")
    if st.button("O que é anestesia geral?"):
        st.session_state["pergunta_exemplo"] = "O que é anestesia geral e como ela funciona?"
    if st.button("Tipos de anestesia"):
        st.session_state["pergunta_exemplo"] = "Qual a diferença entre anestesia geral, regional e local?"

with st.sidebar.expander("⚠️ Complicações", expanded=False):
    st.markdown("Questões sobre riscos e efeitos adversos.")
    if st.button("Complicações comuns"):
        st.session_state["pergunta_exemplo"] = "Quais são as complicações mais comuns na anestesia?"

with st.sidebar.expander("📎 Fontes e Estudo", expanded=False):
    st.markdown("Entenda de onde vem o conhecimento do assistente.")
    if st.button("Fontes de dados"):
        st.session_state["pergunta_exemplo"] = "Quais as fontes de dados que utiliza para responder?"

# Upload de arquivo
st.sidebar.markdown("### 📎 Adicionar Documento")
TIPOS_SUPORTADOS = {
    "application/pdf": carregar_texto_pdf,
    "text/csv": carregar_texto_csv,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": carregar_texto_excel,
    "application/vnd.ms-excel": carregar_texto_excel,
}
uploaded_file = st.sidebar.file_uploader("Envie um arquivo (PDF, CSV, Excel)", type=["pdf", "csv", "xlsx"])
if uploaded_file:
    try:
        if uploaded_file.type in TIPOS_SUPORTADOS:
            texto = TIPOS_SUPORTADOS[uploaded_file.type](uploaded_file)
            if texto.strip():
                base_vetorial.add_documents([Document(page_content=texto)])
                st.sidebar.success("✅ Documento adicionado à base de conhecimento.")
            else:
                st.sidebar.warning("⚠️ O arquivo não contém texto reconhecível.")
        else:
            st.sidebar.error("❌ Formato de arquivo não suportado.")
    except Exception as e:
        st.sidebar.error(f"Erro ao processar o arquivo: {e}")

# Exportação do histórico
with st.sidebar.expander("📤 Exportar Histórico"):
    if st.button("⬇️ Exportar como .txt"):
        txt = exportar_historico_txt(st.session_state["chat_historico"])
        st.download_button("Baixar .txt", txt, file_name="chat_irineu.txt")
    if st.button("⬇️ Exportar como .json"):
        js = exportar_historico_json(st.session_state["chat_historico"])
        st.download_button("Baixar .json", js, file_name="chat_irineu.json")

# ===============================
# Título principal
# ===============================
st.title("👨‍⚕️ Dr. Chicó - O Assistente Médico Inteligente")
st.markdown("Converse com o assistente de IA sobre **temas médicos confiáveis**, com base em documentos técnicos.")

# ===============================
# Botão de nova conversa
# ===============================
if st.button("🔄 Nova Conversa"):
    st.session_state["chat_historico"] = []
    st.session_state["pergunta_exemplo"] = None
    st.success("✅ Nova conversa iniciada.")

# ===============================
# Entrada do usuário
# ===============================
entrada_usuario = st.chat_input("Digite sua pergunta médica aqui...")
pergunta = entrada_usuario or st.session_state["pergunta_exemplo"]

# ===============================
# Processa nova pergunta
# ===============================
if pergunta and (
    len(st.session_state["chat_historico"]) == 0 or
    st.session_state["chat_historico"][-1] != ("user", pergunta)
):
    st.session_state["chat_historico"].append(("user", pergunta))
    historico_formatado = [
        f"{'Usuário' if role == 'user' else 'Assistente'}: {msg}"
        for role, msg in st.session_state["chat_historico"]
    ]
    try:
        resposta = gerar_resposta(pergunta, historico_formatado)
        st.session_state["chat_historico"].append(("assistant", resposta))
    except Exception as e:
        st.session_state["chat_historico"].append(("assistant", f"Erro ao gerar resposta: {e}"))
    st.session_state["pergunta_exemplo"] = None

# ===============================
# Renderiza o histórico do chat
# ===============================
exibir_conversa()
