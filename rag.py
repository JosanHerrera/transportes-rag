# El "cerebro" del asistente: busca en los documentos y responde citando la fuente
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# 1. Conectamos con la base vectorial que creamos en la fase 2
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
base = Chroma(
    collection_name="transportes_rag",
    embedding_function=embeddings,
    persist_directory="base_vectorial",
)

# 2. La IA que redacta la respuesta (temperature=0: respuestas precisas, sin "creatividad")
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)

# 3. Las instrucciones que recibe la IA en cada pregunta
INSTRUCCIONES = """Eres el asistente interno de Transportes RAG S.L., una empresa logística.
Responde en español usando SOLO la información de los fragmentos de abajo.

Reglas:
- Si la respuesta no está en los fragmentos, responde exactamente:
  "No encuentro esa información en los documentos de la empresa." No inventes nada.
- Después de cada dato, indica la fuente así: [nombre_del_documento.pdf, página N].
- Sé claro y breve. Si haces un cálculo, muestra cómo lo haces.

FRAGMENTOS:
{contexto}

PREGUNTA: {pregunta}
"""


def responder(pregunta, k=5):
    """Busca los k trozos más parecidos y pide a la IA que responda con ellos."""
    trozos = base.similarity_search(pregunta, k=k)
    contexto = "\n\n".join(
        f"[{t.metadata['documento']}, página {t.metadata['pagina']}]\n{t.page_content}"
        for t in trozos
    )
    respuesta = llm.invoke(INSTRUCCIONES.format(contexto=contexto, pregunta=pregunta))
    return respuesta.text, trozos


# 4. Modo prueba: preguntas por la terminal
if __name__ == "__main__":
    print("Asistente de Transportes RAG. Escribe 'salir' para terminar.\n")
    while True:
        pregunta = input("Pregunta: ").strip()
        if pregunta.lower() == "salir":
            break
        if not pregunta:
            continue
        texto, trozos = responder(pregunta)
        print(f"\n{texto}\n")
        print("Trozos consultados:")
        for t in trozos:
            print(f"  - {t.metadata['documento']} (página {t.metadata['pagina']})")
        print()