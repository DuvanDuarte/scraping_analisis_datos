import subprocess
import sys

# Únicamente se instalan los paquetes externos requeridos
LIBRERIAS = [
    "requests",
    "beautifulsoup4",
    "pandas"
]

# Flujo secuencial de ejecución según el orden numérico de tu carpeta
ARCHIVOS = [
    "1_global_military_rankings.py",
    "2_paises_detalles.py",
    "3_paises_pilares.py",
    "4_0_aircraft_links.py",
    "4_1_aircrafts_inventory.py"
]

def instalar_dependencias():
    print("--- Verificando e instalando librerías requeridas ---")
    for libreria in LIBRERIAS:
        print(f"Garantizando presencia de: {libreria}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", libreria])
    print("Todas las librerías están instaladas y actualizadas.\n")

def ejecutar_scripts():
    for script in ARCHIVOS:
        print("=" * 50)
        print(f"Ejecutando: {script}")
        print("=" * 50)
        
        # subprocess.run bloquea el hilo principal hasta que el script secundario termine
        resultado = subprocess.run([sys.executable, script])
        
        if resultado.returncode != 0:
            print(f"\n[ERROR] Ocurrió un fallo en {script}. Se interrumpe el proceso.")
            sys.exit(1)
            
        print(f"Proceso {script} completado con éxito.\n")

if __name__ == "__main__":
    instalar_dependencias()
    ejecutar_scripts()
    print("¡Secuencia finalizada exitosamente para todos los archivos!")