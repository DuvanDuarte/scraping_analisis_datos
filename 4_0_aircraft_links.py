import os
import random
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. Configuración inicial
BASE_URL = "https://globalmilitary.net/aircraft/"
OUTPUT_CSV = "aircraft_links.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

all_links = []
page = 1

print("Iniciando la recolección de enlaces de aeronaves...\n")

# 2. Bucle dinámico por páginas
for page in range(1, 17):
    # Si la primera página no lleva parámetro, usamos BASE_URL directa; de la 2 en adelante usamos ?page=N
    target_url = BASE_URL if page == 1 else f"{BASE_URL}?page={page}"

    print(f"[Página {page}] Consultando: {target_url}")

    try:
        response = requests.get(target_url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Buscar todas las tarjetas de la página actual
            cards = soup.find_all("a", class_="accard")

            # Criterio de parada: si no hay tarjetas, alcanzamos el final
            if not cards:
                print(
                    f"\nNo se encontraron más tarjetas en la página {page}. Fin de la recolección."
                )
                break

            # Extraer enlaces de cada tarjeta
            links_page_count = 0
            for card in cards:
                href = card.get("href")
                if href:
                    href = href.strip()
                    # Construir URL completa si es una ruta relativa
                    full_url = (
                        f"https://globalmilitary.net{href}"
                        if href.startswith("/")
                        else href
                    )

                    # Obtener slug limpio de la URL
                    slug = href.strip("/").split("/")[-1]

                    all_links.append(
                        {
                            "SLUG": slug,
                            "URL": full_url,
                            "PAGE_FOUND": page,
                        }
                    )
                    links_page_count += 1

            print(f"  --> {links_page_count} enlaces extraídos.")

        elif response.status_code == 404:
            print(
                f"\nPágina {page} no encontrada (Error 404). Fin del paginador."
            )
            break
        else:
            print(
                f"  --> Error HTTP {response.status_code} al acceder a la página {page}."
            )
            break

    except Exception as e:
        print(f"  --> Excepción en la página {page}: {e}")
        break

    # Pausa humana aleatoria entre 1.5 y 3.0 segundos para evitar detección
    sleep_time = random.uniform(1.5, 3.0)
    time.sleep(sleep_time)

    page += 1

# 3. Guardar resultados
if all_links:
    df_links = pd.DataFrame(all_links)
    # Eliminar duplicados en caso de que alguna tarjeta se repita
    df_links.drop_duplicates(subset=["URL"], inplace=True)

    df_links.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n¡Proceso finalizado!")
    print(
        f"Se recolectaron {len(df_links)} enlaces únicos y se guardaron en '{OUTPUT_CSV}'."
    )
    print("\nMuestra de los primeros registros:")
    print(df_links.head())
else:
    print("\nNo se pudo extraer ningún enlace.")