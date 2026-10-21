# 1. Importamos las herramientas
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 2. Cargamos la clave del archivo .env
load_dotenv()

# 3. Elegimos el modelo de IA ("latest" = la versión Flash más reciente)
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest")

# 4. Le hacemos una pregunta y mostramos la respuesta
respuesta = llm.invoke("Preséntate en una frase y explica qué es un almacén logístico.")
print(respuesta.text)