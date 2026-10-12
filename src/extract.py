"""
Módulo de Extracción (ETL)
Consume la API pública de clima Open-Meteo y guarda una copia cruda (Staging Area).
"""
import json
import requests
from config import settings


def extract_weather_data():
    """
    Realiza una petición GET a la API Open-Meteo para obtener datos meteorológicos.
    Aplica el patrón Staging Area guardando el archivo JSON en 'data/raw/'.
    Si no hay conexión a internet, recurre al último archivo guardado localmente.
    """
    url = settings.API_BASE_URL
    params = {
        "latitude": settings.LATITUDE,
        "longitude": settings.LONGITUDE,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": settings.TIMEZONE,
        "past_days": 7,       # Datos de los últimos 7 días
        "forecast_days": 3    # Pronóstico de los próximos 3 días
    }

    cache_file = settings.RAW_DATA_DIR / "weather_raw_latest.json"

    print(f"[EXTRACT] Consultando API Open-Meteo para {settings.CITY_NAME}...")

    try:
        # Petición HTTP con timeout para evitar bloqueos
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()  # Lanza excepción si el código no es 200 OK
        data = response.json()

        # Validar que la respuesta tenga el bloque horario esperado
        if "hourly" not in data or "time" not in data["hourly"]:
            raise ValueError("El JSON recibido no contiene el campo 'hourly.time'.")

        # Patrón Staging: Guardar datos crudos en la carpeta raw
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[EXTRACT] Datos crudos guardados correctamente en Staging: {cache_file.name}")
        return data

    except requests.RequestException as error:
        print(f"[ALERTA] Error al consultar la API en vivo: {error}")

        # Si falla internet o la API, usamos la copia local si existe
        if cache_file.exists():
            print(f"[EXTRACT] Cargando datos desde copia de respaldo local (Staging): {cache_file.name}")
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)

        # Si no hay respaldo, relanzamos el error
        raise error
