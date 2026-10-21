# Crea la base vectorial a partir de los PDF de la carpeta "documentos"
import shutil
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CARPETA_DOCUMENTOS = Path("documentos")
CARPETA_BASE = "base_vectorial"
TAMANO_LOTE = 50  # trozos que se envían a Google de cada vez

# 1. LEER: cargamos cada PDF página a página
paginas = []
for pdf in sorted(CARPETA_DOCUMENTOS.rglob("*.pdf")):
    for pagina in PyPDFLoader(str(pdf)).load():
        # Guardamos de dónde viene cada página (para poder citar la fuente)
        pagina.metadata = {
            "documento": pdf.name,
            "pagina": pagina.metadata["page"] + 1,  # PyPDF empieza a contar en 0
            "tipo": pdf.parent.name,                # "inventados" o "publicos"
        }
        paginas.append(pagina)
print(f"Páginas leídas: {len(paginas)}")

# 2. TROCEAR: fragmentos de ~1000 caracteres que se solapan 150
troceador = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
trozos = troceador.split_documents(paginas)
print(f"Trozos creados: {len(trozos)}")

# 3. EMBEDDINGS + BASE: borramos la base anterior y la creamos de cero
if Path(CARPETA_BASE).exists():
    shutil.rmtree(CARPETA_BASE)

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
base = Chroma(
    collection_name="transportes_rag",
    embedding_function=embeddings,
    persist_directory=CARPETA_BASE,
)

# Enviamos los trozos por lotes, con pausas, para no superar el límite gratuito
for inicio in range(0, len(trozos), TAMANO_LOTE):
    lote = trozos[inicio:inicio + TAMANO_LOTE]
    for intento in range(3):
        try:
            base.add_documents(lote)
            break
        except Exception as error:
            print(f"  Aviso: {error}. Espero 60 segundos y lo reintento...")
            time.sleep(60)
    else:
        raise SystemExit("No se pudo completar. Prueba de nuevo más tarde.")
    print(f"  Guardados {min(inicio + TAMANO_LOTE, len(trozos))} de {len(trozos)}")
    time.sleep(35)

print("Base vectorial creada.\n")

# 4. PRUEBA: buscamos los 3 trozos más parecidos a una pregunta
pregunta = "¿Cuánto cuesta enviar un palet a Baleares?"
print(f"Prueba de búsqueda: {pregunta}\n")
for trozo in base.similarity_search(pregunta, k=3):
    print(f"-> {trozo.metadata['documento']} (página {trozo.metadata['pagina']})")
    print(f"   {trozo.page_content[:150]}...\n")