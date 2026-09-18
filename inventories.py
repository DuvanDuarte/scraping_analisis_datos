import random
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc

INVENTORIES_SECTIONS = {
    "air_forces": "https://www.globalmilitary.net/air_forces/",
    "armies": "https://www.globalmilitary.net/armies/",
    "air_bases": "https://www.globalmilitary.net/airbases/",
    "navies": "https://www.globalmilitary.net/navies/",
    "naval_bases": "https://www.globalmilitary.net/naval_bases/",
    "nuclear_forces": "https://www.globalmilitary.net/nuclear/",
}

PAGINATED_SECTIONS = ["air_bases", "naval_bases"]


def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return uc.Chrome(options=options, version_main=151, use_subprocess=True)


def parse_filtered_tables(html_content, single_table_only=False):
    """Extrae las filas filtrando tablas irrelevantes por estructura/columnas."""
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table")

    if not tables:
        return [], []

    if single_table_only:
        tables = [tables[0]]

    global_headers = []
    rows_data = []
    target_column_count = None

    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue

        # Detectar encabezados y definir el estándar de columnas esperadas
        if not global_headers:
            header_row = rows[0]
            headers_found = [
                " ".join(th.text.split())
                for th in header_row.find_all(["th", "td"])
            ]
            global_headers = [h for h in headers_found if h]
            target_column_count = len(global_headers)

        # FILTRO CLAVE: Si la tabla actual no coincide en número de columnas, es una tabla secundaria no deseada
        sample_row = rows[0].find_all(["td", "th"])
        if target_column_count and len(sample_row) != target_column_count:
            continue

        for row in rows:
            cols = row.find_all(["td", "th"])
            if not cols or len(cols) != target_column_count:
                continue

            row_values = [" ".join(col.text.split()) for col in cols]

            if row_values and any(row_values):
                first_cell = row_values[0].strip().lower()

                # Ignorar filas de encabezados repetidos
                if first_cell in ["#", "rank", "country", "base", "name"]:
                    continue

                cleaned_values = [
                    val if (val != "" and val != "—" and val != "-") else "0"
                    for val in row_values
                ]
                rows_data.append(cleaned_values)

    return global_headers, rows_data


def scrape_section(section_name, url, driver):
    print(f"\n[+] Procesando sección: {section_name.upper()}")
    print(f"    URL: {url}")

    try:
        driver.get(url)

        # 1. Espera activa para asegurar que Selenium detecte al menos una tabla cargada
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
        except Exception:
            print(
                f"    ⚠️ Tiempo de espera agotado cargando la tabla en {section_name}"
            )

        time.sleep(random.uniform(4, 6))

        all_rows_data = []
        global_headers = []

        # Estrategia 1: Paginación (Air Bases y Naval Bases)
        if section_name in PAGINATED_SECTIONS:
            print("    ▶ Extracción Paginada (Clics »)...")
            page_num = 1

            while True:
                time.sleep(2)
                headers, rows_data = parse_filtered_tables(
                    driver.page_source, single_table_only=False
                )

                if not global_headers and headers:
                    global_headers = headers

                if rows_data:
                    all_rows_data.extend(rows_data)

                try:
                    next_btn = driver.find_elements(
                        By.XPATH,
                        "//a[text()='»' or contains(text(), '»') or contains(@class, 'next')]",
                    )

                    if not next_btn or not next_btn[0].is_enabled():
                        break

                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        next_btn[0],
                    )
                    time.sleep(1)
                    next_btn[0].click()
                    page_num += 1
                    time.sleep(random.uniform(2.5, 4.0))

                except Exception:
                    break

            print(f"    ✓ Completadas {page_num} páginas en total.")

        # Estrategia 2: Scroll dinámico progresivo (Air Forces, Armies, Navies, Nuclear Forces)
        else:
            print("    ▶ Extracción por Scroll Progresivo con Filtro Estricto...")

            # Scroll en 4 partes para forzar a JavaScript a renderizar tablas continuas
            for i in range(1, 5):
                driver.execute_script(
                    f"window.scrollTo(0, (document.body.scrollHeight / 4) * {i});"
                )
                time.sleep(2)

            is_nuclear = section_name == "nuclear_forces"
            global_headers, all_rows_data = parse_filtered_tables(
                driver.page_source, single_table_only=is_nuclear
            )

        if not all_rows_data:
            print(
                f"    ❌ Error: No se extrajo ningún dato para {section_name}"
            )
            return

        num_cols = len(all_rows_data[0])
        if len(global_headers) != num_cols:
            global_headers = [f"Columna_{i+1}" for i in range(num_cols)]

        df = pd.DataFrame(all_rows_data, columns=global_headers)
        df = df.fillna("0")
        df.replace("", "0", inplace=True)

        output_file = f"inventory_{section_name}.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")

        print(
            f"    ✓ ¡ÉXITO COMPLETO! Guardado '{output_file}' con {len(df)} registros limpios."
        )

    except Exception as e:
        print(f"    ❌ Error inesperado en {section_name}: {e}")


def main():
    print("=" * 60)
    print("INICIANDO EXTRACCIÓN CON ESPERA ACTIVA Y FILTRADO ESTRUCTURAL")
    print("=" * 60)

    driver = create_driver()

    try:
        for section_name, url in INVENTORIES_SECTIONS.items():
            scrape_section(section_name, url, driver)
            time.sleep(random.uniform(3, 5))
    finally:
        try:
            driver.close()
            driver.quit()
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("¡PROCESO FINALIZADO! Todos los CSVs procesados correctamente.")
    print("=" * 60)


if __name__ == "__main__":
    main()