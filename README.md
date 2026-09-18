Profe como el trabajo fue en grupo, lo que hizo mi compañero se ejecuta desde 0_main.py y lo que hice yo se ejecuta desde inventories.py

Los requerimientos son:

Estos valores son un recuento de todos nuestros archivos extraídos en scrapping, ya luego se explicara el Insight de la data extraída
1. Número de variables 
 88 columnas de datos

2. Cantidad de registros
 3253 filas de información

3. Cantidad de tablas
 11 tablas independientes

4. Insight de la data extraída
 Como información clave tenemos:
   - Se identifican únicamente 9 naciones con capacidad de ojivas nucleares, donde Rusia (5,420) y Estados Unidos (5,042) concentran más del 85% del arsenal atómico mundial.
   - Existe una alta correlación entre el presupuesto de defensa (liderado por EE. UU. con $920B) y la infraestructura operativa registrada en los catálogos de bases aéreas (150) y navales
    (161).
 Insight de cada archivo extraído:
   - paises_pilares.csv: Explica cómo se calcula el ranking de cada país, dividiendo su fuerza en áreas clave (fuerza terrestre, personal, etc.) y asignando una nota a cada una.
   - paises_detalles.csv: Es la ficha económica y geográfica. Sirve para entender el tamaño real de cada país: cuánta plata tiene (PIB), cuánto gasta en defensa, cuánta gente vive ahí y su
    extensión territorial.
   - global_military_rankings.csv: Es el ranking general. Muestra qué países son las potencias militares más fuertes del mundo, juntando en un solo puntaje sus tropas, aviones, barcos y
    presupuesto.
   - aircraft_master.csv: Es la ficha técnica de aviones y helicópteros. Detalla la ingeniería de cada nave: qué tan rápido vuela, cuánto pesa, cuántos motores tiene y qué distancia alcanza.
   - aircraft_links.csv: Es el historial de rastreo. Guarda las direcciones web de donde el código extrajo la información de los aviones para comprobar de dónde salieron los datos.
   - inventory_nuclear_forces.csv: Es el conteo de bombas atómicas. Muestra cuáles son los 9 países que tienen armas nucleares, cuántas ojivas poseen y cuántas están listas para usarse.
   - inventory_naval_bases.csv: Es el mapa de bases navales. Dice en qué parte del mundo están los puertos de guerra más importantes, quién los opera y cuántos barcos tienen estacionados
    ahí.
   - inventory_navies.csv: Es el inventario de barcos de guerra. Mide qué tan poderosa es la flota marina de cada país y desglosa cuántos barcos grandes, medianos y pequeños tienen.
   - inventory_air_bases.csv: Es el mapa de bases aéreas. Registra dónde están los aeródromos militares del mundo, cuántas pistas de aterrizaje tienen y cuántos aviones guardan.
   - inventory_armies.csv: Es el inventario del ejército de tierra. Mide la fuerza terrestre de cada país y cuenta cuántos tanques, vehículos blindados y cañones de artillería poseen.
   - inventory_air_forces.csv: Es el inventario de la fuerza aérea. Muestra qué tan potente es la aviación de cada país, cuántos aviones de combate tienen en total y si su flota creció o se
    redujo respecto al año anterior.
