import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. Configuración inicial
INPUT_CSV = "global_military_rankings.csv"
OUTPUT_CSV = "paises_pilares.csv"
BASE_URL = "https://globalmilitary.net/countries/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2. Verificar que exista el archivo generado en el paso anterior
if not os.path.exists(INPUT_CSV):
    print(f"Error: No se encontró el archivo '{INPUT_CSV}'. Ejecuta primero el script principal.")
    exit()

df_paises = pd.read_csv(INPUT_CSV)
pilares_data = []

print(f"Iniciando extracción de pilares para {len(df_paises)} países...\n")

# 3. Recorrer cada país de la lista
for index, row in df_paises.iterrows():
    slug = row.get("SLUG URL")
    nombre = row.get("NOMBRE")

    # Validar que exista el enlace
    if pd.isna(slug) or not str(slug).strip():
        print(f"[{index + 1}/{len(df_paises)}] Saltando {nombre}: Sin slug válido.")
        continue
    
    # Limpiar espacios en blanco
    slug = str(slug).strip()

    # Construir la URL completa
    full_url = f"{BASE_URL.rstrip('/')}/{slug}/"

    print(f"[{index + 1}/{len(df_paises)}] Extrayendo: {nombre} ({slug}) -> {full_url}")

    try:
        response = requests.get(full_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            
            pilar_encontrado = False
            
            for table in tables:
                # Comprobar si la tabla es la de pilares verificando su contenido
                header_text = table.text.lower()
                if "pillar" in header_text or "weight" in header_text:
                    rows = table.find_all('tr')[1:]  # Omitir cabecera
                    
                    for tr in rows:
                        cols = tr.find_all('td')
                        if len(cols) >= 4:
                            pilares_data.append({
                                "SLUG URL": slug,
                                "Pillar": cols[0].text.strip(),
                                "Weight": cols[1].text.strip(),
                                "Score": cols[2].text.strip(),
                                "Basis": cols[3].text.strip()
                            })
                    pilar_encontrado = True
                    break  # Detener búsqueda tras hallar la tabla correcta
            
            if not pilar_encontrado:
                print(f"  --> No se encontró la tabla de pilares para {nombre}.")
        else:
            print(f"  --> Error {response.status_code} al acceder a {full_url}")

    except Exception as e:
        print(f"  --> Excepción al procesar {nombre}: {e}")

    # Pausa de 1 segundo entre peticiones para no saturar el servidor
    time.sleep(1)

# 4. Guardar resultados en el CSV final
if pilares_data:
    df_pilares = pd.DataFrame(pilares_data)
    df_pilares.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n¡Extracción finalizada con éxito!")
    print(f"Se extrajeron {len(df_pilares)} registros y se guardaron en '{OUTPUT_CSV}'.")
    print("\nMuestra de los primeros registros:")
    print(df_pilares.head(7))
else:
    print("\nNo se pudo extraer ningún dato de pilares.")