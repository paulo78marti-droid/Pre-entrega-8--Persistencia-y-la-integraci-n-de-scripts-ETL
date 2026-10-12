import json
import logging
import time
from typing import Any, Dict, Optional
import requests

from config import settings

logger = logging.getLogger(__name__)


def get_with_retries(
    url: str,
    params: Dict[str, Any],
    max_retries: int = settings.MAX_RETRIES,
    backoff_factor: int = settings.RETRY_BACKOFF_FACTOR,
    timeout: int = settings.REQUEST_TIMEOUT
) -> requests.Response:
    """
    Realiza una petición HTTP GET implementando backoff exponencial y timeout.
    Distingue errores transitorios (5xx, 429) de errores permanentes (4xx).
    """
    delay = 1
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Realizando petición a %s (Intento %d/%d)...", url, attempt, max_retries)
            response = requests.get(url, params=params, timeout=timeout)

            # Éxito
            if response.status_code == 200:
                return response

            # Errores transitorios que ameritan reintento (Rate Limit o error de servidor)
            if response.status_code in (429, 500, 502, 503, 504):
                logger.warning(
                    "Error HTTP transitorio %d. Reintentando en %d segundos...",
                    response.status_code,
                    delay
                )
                time.sleep(delay)
                delay *= backoff_factor
            else:
                # Errores cliente (400, 401, 404, etc.) son permanentes
                logger.error("Error permanente del cliente HTTP %d: %s", response.status_code, response.text)
                response.raise_for_status()

        except (requests.ConnectionError, requests.Timeout) as exc:
            logger.warning("Fallo de red o timeout (%s). Reintentando en %d s...", exc, delay)
            if attempt == max_retries:
                raise
            time.sleep(delay)
            delay *= backoff_factor

    raise RuntimeError(f"Se superó el límite de {max_retries} reintentos al consultar {url}")


def extract_weather_data(
    latitude: float = settings.LATITUDE,
    longitude: float = settings.LONGITUDE,
    timezone: str = settings.TIMEZONE,
    past_days: int = 7,
    forecast_days: int = 3,
    save_raw: bool = True
) -> Dict[str, Any]:
    """
    Extrae datos meteorológicos desde la API pública Open-Meteo.
    Implementa el patrón Staging Area guardando los datos crudos en data/raw/.
    Si la conexión falla, intenta cargar desde el archivo en staging para reproducibilidad.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": timezone,
        "past_days": past_days,
        "forecast_days": forecast_days,
    }

    cache_file = settings.RAW_DATA_DIR / "weather_raw_latest.json"

    try:
        response = get_with_retries(settings.API_BASE_URL, params=params)
        data = response.json()

        # Validación básica de estructura de respuesta
        if "hourly" not in data or "time" not in data["hourly"]:
            raise ValueError("La respuesta de la API no contiene el nodo 'hourly.time' esperado.")

        # Guardar en Staging Area
        if save_raw:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Datos crudos persistidos en Staging: %s", cache_file)

        return data

    except Exception as exc:
        logger.error("Error durante la extracción en vivo de la API: %s", exc)
        if cache_file.exists():
            logger.warning("Recuperando datos crudos desde respaldo local en staging: %s", cache_file)
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        raise
