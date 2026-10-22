# Interfaz web del asistente (se ejecuta con: streamlit run app.py)
import streamlit as st
from rag import responder

st.set_page_config(page_title="Asistente Transportes RAG", page_icon="🚚")

st.title("🚚 Asistente de Transportes RAG S.L.")
st.caption("Pregunta sobre tarifas, plazos, almacén, devoluciones o prevención de riesgos. "
           "Cada respuesta cita el documento y la página de donde sale.")

# --- Barra lateral: aviso y preguntas de ejemplo ---
pregunta = None
with st.sidebar:
    st.header("Sobre este proyecto")
    st.info("Transportes RAG S.L. es una empresa **ficticia** y sus documentos son inventados, "
            "salvo la normativa pública del BOE. Proyecto de portfolio.")
    st.subheader("Preguntas de ejemplo")
    ejemplos = [
        "¿Cuánto cuesta enviar un palet a Baleares?",
        "¿Qué hago si mi paquete llega dañado?",
        "¿Cuántos días de vacaciones tengo al año?",
        "¿Qué mercancías peligrosas no se aceptan?",
    ]
    for ejemplo in ejemplos:
        if st.button(ejemplo):
            pregunta = ejemplo
    st.divider()
    if st.button("Borrar conversación"):
        st.session_state.mensajes = []

# --- Memoria de la conversación ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []


def mostrar_fuentes(fuentes):
    with st.expander(f"Ver fuentes consultadas ({len(fuentes)})"):
        for f in fuentes:
            st.markdown(f"**{f['documento']}**, página {f['pagina']}")
            st.caption(f["extracto"])


# Pintamos los mensajes anteriores
for m in st.session_state.mensajes:
    with st.chat_message(m["rol"]):
        st.markdown(m["texto"])
        if m.get("fuentes"):
            mostrar_fuentes(m["fuentes"])

# --- Nueva pregunta (escrita o pulsando un ejemplo) ---
escrita = st.chat_input("Escribe tu pregunta...")
pregunta = escrita or pregunta

if pregunta:
    st.session_state.mensajes.append({"rol": "user", "texto": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en los documentos..."):
            try:
                texto, trozos = responder(pregunta)
            except Exception:
                texto, trozos = ("Ahora mismo no puedo responder: se ha alcanzado el límite "
                                 "de uso gratuito de la IA. Inténtalo en un minuto."), []
        st.markdown(texto)

        # Quitamos fuentes repetidas (mismo documento y página)
        fuentes, vistas = [], set()
        for t in trozos:
            clave = (t.metadata["documento"], t.metadata["pagina"])
            if clave not in vistas:
                vistas.add(clave)
                fuentes.append({"documento": clave[0], "pagina": clave[1],
                                "extracto": t.page_content[:300] + "..."})
        if fuentes:
            mostrar_fuentes(fuentes)

    st.session_state.mensajes.append({"rol": "assistant", "texto": texto, "fuentes": fuentes})