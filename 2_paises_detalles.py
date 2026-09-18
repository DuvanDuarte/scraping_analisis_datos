import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. Configuración inicial
INPUT_CSV = "global_military_rankings.csv"
OUTPUT_CSV = "paises_detalles.csv"
BASE_URL = "https://globalmilitary.net/countries/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 2. Verificar que exista el archivo base
if not os.path.exists(INPUT_CSV):
    print(f"Error: No se encontró el archivo '{INPUT_CSV}'. Ejecuta primero el script principal.")
    exit()

df_paises = pd.read_csv(INPUT_CSV)
detalles_data = []

print(f"Iniciando extracción de detalles para {len(df_paises)} países...\n")

# 3. Recorrer cada país de la lista
for index, row in df_paises.iterrows():
    raw_slug = row.get("SLUG URL")
    nombre = row.get("NOMBRE")

    # Validar que exista el slug
    if pd.isna(raw_slug) or not str(raw_slug).strip():
        print(f"[{index + 1}/{len(df_paises)}] Saltando {nombre}: Sin slug válido.")
        continue
    
    slug = str(raw_slug).strip()
    full_url = f"{BASE_URL.rstrip('/')}/{slug}/"

    print(f"[{index + 1}/{len(df_paises)}] Extrayendo: {nombre} ({slug}) -> {full_url}")

    try:
        response = requests.get(full_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find_all('table')
            
            country_dict = {
                "SLUG URL": slug,
                "NOMBRE": nombre
            }
            
            for table in tables:
                # Omitir la tabla de pilares para no mezclar columnas
                header_text = table.text.lower()
                if "pillar" in header_text or "weight" in header_text:
                    continue

                rows = table.find_all('tr')
                for tr in rows:
                    cols = tr.find_all(['td', 'th'])
                    # Capturar tablas de formato Clave -> Valor (2 columnas)
                    if len(cols) == 2:
                        key = cols[0].text.strip().upper()
                        val = cols[1].text.strip()
                        
                        if key and key not in country_dict:
                            country_dict[key] = val
            
            detalles_data.append(country_dict)
            
        else:
            print(f"  --> Error {response.status_code} al acceder a {full_url}")

    except Exception as e:
        print(f"  --> Excepción al procesar {nombre}: {e}")

    # Pausa de 1 segundo entre peticiones para evitar bloqueos
    time.sleep(1)

# 4. Guardar resultados
if detalles_data:
    df_detalles = pd.DataFrame(detalles_data)
    df_detalles.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    
    print(f"\n¡Extracción finalizada con éxito!")
    print(f"Se procesaron {len(df_detalles)} países y se guardaron en '{OUTPUT_CSV}'.")
    print("\nColumnas generadas:")
    print(list(df_detalles.columns))
else:
    print("\nNo se pudo extraer ningún dato de detalles.")