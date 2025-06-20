
🩺 Dr. Chicó – Assistente Médico de Anestesiologia com LLM + RAG
Um projeto de IA generativa para suporte à decisão clínica, voltado para anestesiologistas.

📌 Descrição
Dr. Chicó é um assistente inteligente desenvolvido com Modelos de Linguagem de Grande Escala (LLM) e RAG (Retrieval-Augmented Generation). Ele permite consultas médicas baseadas em documentos (como protocolos, artigos científicos, guias PDF, dados estruturados) com linguagem natural, oferecendo respostas precisas e contextualizadas para profissionais da anestesiologia.

🧠 Tecnologias Utilizadas
LangChain – Framework para conectar LLMs com fontes externas

FAISS – Indexação vetorial para recuperação de documentos

HuggingFace Transformers – Embeddings e modelos de linguagem

Streamlit – Interface web interativa

PyMuPDF / Pandas – Leitura de arquivos PDF, CSV, Excel

Groq API ou OpenAI API – Backend LLM

Python 3.10+

⚙️ Funcionalidades
Upload de arquivos (PDF, CSV, Excel) via sidebar

Extração automática de textos e criação de base vetorial

Perguntas em linguagem natural com categorização por tema

Histórico de conversas e opção de "Nova Conversa"

Exportação do histórico em .txt ou .json
