import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://globalmilitary.net/countries/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Conectando con la página...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    
    if tables:
        countries_data = []
        
        for table in tables:
            rows = table.find_all('tr')[1:]
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 7:
                    country_cell = cols[1]
                    
                    # 1. Extraer el enlace (<a>) y la abreviación (slug de la URL)
                    link_tag = country_cell.find('a')
                    if link_tag and 'href' in link_tag.attrs:
                        full_url = link_tag['href']
                        # Extrae la última parte de la URL (e.g., 'usa' de '/countries/usa/')
                        url_slug = full_url.strip('/').split('/')[-1]
                        country_name = link_tag.text.strip()
                    else:
                        url_slug = None
                        country_name = country_cell.text.strip()

                    # 2. Extraer el código ISO (letras en negrita/span dentro de la celda)
                    # Se buscan etiquetas de texto antes del enlace (como <span>, <b>, <strong>)
                    iso_tag = country_cell.find(['span', 'b', 'strong'])
                    if iso_tag:
                        iso_code = iso_tag.text.strip()
                    else:
                        # Si no hay etiqueta separada, tomamos la primera palabra como ISO
                        text_parts = country_cell.text.strip().split()
                        iso_code = text_parts[0] if text_parts else ""

                    data = {
                        "Rank": cols[0].text.strip(),
                        "CODIGO ISO": iso_code,
                        "NOMBRE": country_name,
                        "SLUG URL": url_slug,
                        "Power Index": cols[2].text.strip(),
                        "Aircraft": cols[3].text.strip(),
                        "Warships": cols[4].text.strip(),
                        "Active Troops": cols[5].text.strip(),
                        "Defense Budget": cols[6].text.strip()
                    }
                    countries_data.append(data)
        
        df = pd.DataFrame(countries_data)
        df.to_csv("global_military_rankings.csv", index=False, encoding="utf-8-sig")
        
        print("\n¡Extracción exitosa!")
        print("Muestra de los primeros 5 países:")
        print(df[["Rank", "CODIGO ISO", "NOMBRE", "SLUG URL"]].head())
    else:
        print("Error: No se encontró ninguna tabla en la página.")
else:
    print(f"Error al acceder a la web. Código de estado: {response.status_code}")