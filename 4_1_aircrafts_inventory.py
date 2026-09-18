import os
import random
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. Archivos de entrada y salida
INPUT_CSV = "aircraft_links.csv"
OUTPUT_CSV = "aircraft_master.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2. Cargar lista de URLs extraídas en el Paso 1
if not os.path.exists(INPUT_CSV):
    print(f"Error: No se encontró '{INPUT_CSV}'. Ejecuta primero el script del Paso 1.")
    exit()

df_links = pd.read_csv(INPUT_CSV)

# --- CORRECCIÓN DEL ERROR DE LECTURA (CHECKPOINT SEGURO) ---
# En lugar de usar pd.read_csv() que se rompe por las columnas variables,
# leemos directamente la primera columna (SLUG) como texto plano.
processed_slugs = set()
if os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0:
    with open(OUTPUT_CSV, "r", encoding="utf-8-sig", errors="ignore") as f:
        for line in f:
            # Tomamos el primer elemento antes de la primera coma
            parts = line.split(",")
            if parts:
                cleaned_slug = parts[0].replace('"', "").strip()
                if cleaned_slug and cleaned_slug != "SLUG":
                    processed_slugs.add(cleaned_slug)

aircraft_data = []
total = len(df_links)

print(
    f"Iniciando extracción detallada para {total} aeronaves ({len(processed_slugs)} ya procesadas)...\n"
)

# 3. Recorrer cada enlace
for index, row in df_links.iterrows():
    slug = str(row.get("SLUG")).strip()
    url = str(row.get("URL")).strip()

    # Saltar si ya se extrajo en una ejecución previa
    if slug in processed_slugs:
        continue

    print(f"[{index + 1}/{total}] Extrayendo datos de: {slug}")

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Diccionario base para esta aeronave
            row_data = {"SLUG": slug, "URL": url}

            # A. Extracción del Título Principal
            title_tag = soup.find("h1")
            row_data["NAME"] = title_tag.text.strip() if title_tag else ""

            # B. Extracción de tablas de especificaciones (<table class="spec">)
            spec_tables = soup.find_all("table", class_="spec")

            for table in spec_tables:
                rows = table.find_all("tr")
                for tr in rows:
                    td_label = tr.find("td", class_="l")
                    td_value = tr.find("td", class_="v")

                    if td_label and td_value:
                        key = td_label.text.strip().upper().replace(" ", "_")
                        val = td_value.text.strip()
                        row_data[key] = val

            aircraft_data.append(row_data)
            processed_slugs.add(slug)

        else:
            print(f"  --> Error {response.status_code} al acceder a {url}")

    except Exception as e:
        print(f"  --> Excepción en {slug}: {e}")

    # Guardar avances progresivos cada 50 registros (Checkpoint)
    if len(aircraft_data) >= 50:
        df_batch = pd.DataFrame(aircraft_data)
        file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
        df_batch.to_csv(
            OUTPUT_CSV,
            mode="a",
            header=not file_exists,
            index=False,
            encoding="utf-8-sig",
        )
        aircraft_data = []  # Limpiar lote guardado

    # Pausa fija de 1 segundo
    time.sleep(1)

# Guardar cualquier registro restante que haya quedado fuera del último lote
if aircraft_data:
    df_batch = pd.DataFrame(aircraft_data)
    file_exists = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
    df_batch.to_csv(
        OUTPUT_CSV,
        mode="a",
        header=not file_exists,
        index=False,
        encoding="utf-8-sig",
    )

print(f"\n Extracción técnica finalizada. Datos guardados en '{OUTPUT_CSV}'.")