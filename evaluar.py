# Evalúa el asistente con las preguntas de evaluacion/preguntas.csv
import csv
import time
from rag import responder, llm

JUEZ = """Eres un evaluador. Compara la RESPUESTA DEL ASISTENTE con la RESPUESTA CORRECTA.
- Es CORRECTO si contiene el dato correcto, aunque esté redactado distinto o añada detalles.
- Si la respuesta correcta es que no hay información, solo es CORRECTO si el asistente dice que no la encuentra.
Responde solo con una palabra: CORRECTO o INCORRECTO.

PREGUNTA: {pregunta}
RESPUESTA CORRECTA: {correcta}
RESPUESTA DEL ASISTENTE: {respuesta}"""


def con_reintentos(funcion, *args):
    """Si Google nos frena por el límite gratuito, espera y lo reintenta."""
    for intento in range(3):
        try:
            return funcion(*args)
        except Exception:
            print("   (límite alcanzado, espero 60 segundos...)")
            time.sleep(60)
    raise SystemExit("No se pudo completar la evaluación. Prueba más tarde.")


def juzgar(pregunta, correcta, respuesta):
    veredicto = llm.invoke(JUEZ.format(pregunta=pregunta, correcta=correcta, respuesta=respuesta)).text
    return "INCORRECTO" not in veredicto.upper()


with open("evaluacion/preguntas.csv", encoding="utf-8") as f:
    preguntas = list(csv.DictReader(f, delimiter=";"))

resultados = []
aciertos_respuesta = aciertos_busqueda = total_busqueda = 0

for n, fila in enumerate(preguntas, start=1):
    print(f"[{n}/{len(preguntas)}] {fila['pregunta']}")
    respuesta, trozos = con_reintentos(responder, fila["pregunta"])
    correcta = con_reintentos(juzgar, fila["pregunta"], fila["respuesta_correcta"], respuesta)

    # ¿Encontró la búsqueda alguno de los documentos esperados?
    busqueda = "-"
    if fila["documento_esperado"]:
        encontrados = [t.metadata["documento"] for t in trozos]
        esperados = fila["documento_esperado"].split("|")
        ok = any(doc.startswith(e) for doc in encontrados for e in esperados)
        busqueda = "SÍ" if ok else "NO"
        total_busqueda += 1
        aciertos_busqueda += ok

    aciertos_respuesta += correcta
    print(f"   Búsqueda: {busqueda} | Respuesta: {'CORRECTA' if correcta else 'INCORRECTA'}")
    resultados.append({**fila, "respuesta_asistente": respuesta, "busqueda_ok": busqueda,
                       "respuesta_ok": "SÍ" if correcta else "NO"})
    time.sleep(10)  # pausa para no superar el límite gratuito

# Guardamos el detalle (utf-8-sig para que Excel muestre bien las tildes)
with open("evaluacion/resultados.csv", "w", encoding="utf-8-sig", newline="") as f:
    escritor = csv.DictWriter(f, fieldnames=resultados[0].keys(), delimiter=";")
    escritor.writeheader()
    escritor.writerows(resultados)

print("\n===== RESULTADO =====")
print(f"Búsqueda: {aciertos_busqueda}/{total_busqueda} "
      f"({100 * aciertos_busqueda / total_busqueda:.0f} %) encontró el documento correcto")
print(f"Respuestas: {aciertos_respuesta}/{len(preguntas)} "
      f"({100 * aciertos_respuesta / len(preguntas):.0f} %) correctas")
print("Detalle guardado en evaluacion/resultados.csv")