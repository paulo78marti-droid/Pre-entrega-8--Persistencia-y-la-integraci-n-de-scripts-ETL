from datetime import datetime
import logging
from typing import Any, Dict, Tuple
import pandas as pd

from config import settings

logger = logging.getLogger(__name__)


def classify_wind(speed_kmh: float) -> str:
    """Clasifica la velocidad del viento según rangos basados en la escala Beaufort."""
    if speed_kmh < 12.0:
        return "Calma / Viento Leve"
    elif speed_kmh < 29.0:
        return "Brisa Moderada"
    elif speed_kmh < 50.0:
        return "Viento Fuerte"
    else:
        return "Temporal"


def transform_weather_data(raw_data: Dict[str, Any], city: str = settings.CITY_NAME) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Transforma y limpia los datos crudos de Open-Meteo.
    
    Retorna dos DataFrames:
    1. df_hourly: Registros horarios con tipos corregidos, nulos tratados y features creadas.
    2. df_daily: Resumen analítico agregado diario con KPIs climatológicos.
    """
    hourly = raw_data.get("hourly", {})
    if not hourly or "time" not in hourly:
        raise ValueError("Estructura JSON inválida: falta el bloque horario 'hourly.time'.")

    # 1. Construir DataFrame tabular inicial
    df_raw = pd.DataFrame({
        "timestamp_str": hourly.get("time", []),
        "temperature_c": hourly.get("temperature_2m", []),
        "humidity_pct": hourly.get("relative_humidity_2m", []),
        "precipitation_mm": hourly.get("precipitation", []),
        "wind_speed_kmh": hourly.get("wind_speed_10m", [])
    })

    logger.info("Filas recibidas sin procesar: %d", len(df_raw))

    # 2. Conversión y corrección de tipos
    df_clean = df_raw.copy()
    df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp_str"])
    df_clean["city"] = city

    # 3. Tratamiento de nulos y anomalías
    # Descartar filas con timestamp o temperatura faltante (datos irreparables)
    df_clean = df_clean.dropna(subset=["timestamp", "temperature_c"]).copy()

    # Imputación de precipitación nula por 0.0 (asunción segura en meteorología)
    df_clean["precipitation_mm"] = df_clean["precipitation_mm"].fillna(0.0)

    # Imputación de humedad nula con la mediana si existieran faltantes
    if df_clean["humidity_pct"].isnull().any():
        median_humidity = df_clean["humidity_pct"].median()
        df_clean["humidity_pct"] = df_clean["humidity_pct"].fillna(median_humidity)

    # Redondeos y consistencia numérica
    df_clean["temperature_c"] = df_clean["temperature_c"].round(2)
    df_clean["humidity_pct"] = df_clean["humidity_pct"].round(1)
    df_clean["precipitation_mm"] = df_clean["precipitation_mm"].round(2)
    df_clean["wind_speed_kmh"] = df_clean["wind_speed_kmh"].round(2)

    # 4. Feature Engineering
    df_clean["wind_category"] = df_clean["wind_speed_kmh"].apply(classify_wind)
    df_clean["is_rainy"] = df_clean["precipitation_mm"] > 0.0
    now_utc = datetime.utcnow()
    df_clean["ingested_at"] = now_utc

    # Eliminar duplicados temporales si existieran en la extracción
    df_clean = df_clean.drop_duplicates(subset=["city", "timestamp"]).copy()

    # Selección y orden de columnas para weather_hourly
    hourly_columns = [
        "city",
        "timestamp",
        "temperature_c",
        "humidity_pct",
        "precipitation_mm",
        "wind_speed_kmh",
        "wind_category",
        "is_rainy",
        "ingested_at"
    ]
    df_hourly = df_clean[hourly_columns].copy()

    # 5. Agregación diaria (Capa Analítica / Data Mart)
    df_clean["date"] = df_clean["timestamp"].dt.date
    df_daily = df_clean.groupby(["city", "date"]).agg(
        temp_min_c=("temperature_c", "min"),
        temp_max_c=("temperature_c", "max"),
        temp_avg_c=("temperature_c", "mean"),
        total_precipitation_mm=("precipitation_mm", "sum"),
        avg_wind_speed_kmh=("wind_speed_kmh", "mean"),
        rainy_hours_count=("is_rainy", "sum")
    ).reset_index()

    df_daily["temp_min_c"] = df_daily["temp_min_c"].round(2)
    df_daily["temp_max_c"] = df_daily["temp_max_c"].round(2)
    df_daily["temp_avg_c"] = df_daily["temp_avg_c"].round(2)
    df_daily["total_precipitation_mm"] = df_daily["total_precipitation_mm"].round(2)
    df_daily["avg_wind_speed_kmh"] = df_daily["avg_wind_speed_kmh"].round(2)
    df_daily["rainy_hours_count"] = df_daily["rainy_hours_count"].astype(int)
    df_daily["ingested_at"] = now_utc

    logger.info("Transformación completa: %d registros horarios, %d resúmenes diarios generados.", len(df_hourly), len(df_daily))

    return df_hourly, df_daily
