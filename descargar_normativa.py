# Descarga automática de normativa pública (BOE) para el proyecto Transportes RAG.
# Son documentos oficiales y de uso libre. Se guardan en documentos/publicos/

import urllib.request
from pathlib import Path

# 1. Carpeta de destino (se crea si no existe)
carpeta = Path("documentos/publicos")
carpeta.mkdir(parents=True, exist_ok=True)

# 2. Lista de documentos: nombre del archivo -> dirección web del PDF oficial
documentos = {
    "ley_31_1995_prevencion_riesgos_laborales.pdf":
        "https://www.boe.es/buscar/pdf/1995/BOE-A-1995-24292-consolidado.pdf",
    "rd_486_1997_lugares_de_trabajo.pdf":
        "https://www.boe.es/buscar/pdf/1997/BOE-A-1997-8669-consolidado.pdf",
    "rd_487_1997_manipulacion_manual_cargas.pdf":
        "https://www.boe.es/buscar/pdf/1997/BOE-A-1997-8670-consolidado.pdf",
    "rd_773_1997_equipos_proteccion_individual.pdf":
        "https://www.boe.es/buscar/pdf/1997/BOE-A-1997-12735-consolidado.pdf",
    "rd_1215_1997_equipos_de_trabajo.pdf":
        "https://www.boe.es/buscar/pdf/1997/BOE-A-1997-17824-consolidado.pdf",
}

# 3. Descargamos uno a uno
for nombre, url in documentos.items():
    destino = carpeta / nombre
    if destino.exists():
        print(f"Ya existe, lo salto: {nombre}")
        continue
    print(f"Descargando: {nombre} ...")
    # Nos identificamos como un navegador para que la web no rechace la descarga
    peticion = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(peticion, timeout=60) as respuesta:
        destino.write_bytes(respuesta.read())
    print(f"  OK ({destino.stat().st_size // 1024} KB)")

print("\nTerminado. Revisa la carpeta documentos/publicos")
