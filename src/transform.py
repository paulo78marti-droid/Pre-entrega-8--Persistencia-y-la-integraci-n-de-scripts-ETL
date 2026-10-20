"""
Módulo de Transformación (ETL)
Curso: Data Science II - Coderhouse

Limpia los datos del clima, ajusta tipos de datos, realiza feature engineering básico
y genera un resumen diario de métricas climáticas.
"""
from datetime import datetime
import pandas as pd
from config import settings


def clasificar_viento(velocidad):
    """Clasifica la velocidad del viento en categorías simples."""
    if velocidad < 15.0:
        return "Leve"
    elif velocidad < 30.0:
        return "Moderado"
    else:
        return "Fuerte"


def transform_weather_data(raw_data, city=settings.CITY_NAME):
    """
    Transforma el diccionario JSON crudo de la API en dos DataFrames:
    1. df_hourly: mediciones horarias limpias con nuevas columnas.
    2. df_daily: resumen diario agrupado (mín, máx, promedio, lluvia total).
    """
    hourly = raw_data.get("hourly", {})
    if not hourly:
        raise ValueError("El JSON no contiene el nodo 'hourly'.")

    # 1. Crear DataFrame a partir de las listas del JSON
    df = pd.DataFrame({
        "timestamp": hourly.get("time", []),
        "temperature_c": hourly.get("temperature_2m", []),
        "humidity_pct": hourly.get("relative_humidity_2m", []),
        "precipitation_mm": hourly.get("precipitation", []),
        "wind_speed_kmh": hourly.get("wind_speed_10m", [])
    })

    print(f"[TRANSFORM] Filas recibidas de la API: {len(df)}")

    # 2. Conversión de tipos de datos
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["city"] = city

    # 3. Limpieza de datos y manejo de valores nulos
    # Eliminamos registros sin fecha o temperatura (datos críticos)
    df = df.dropna(subset=["timestamp", "temperature_c"]).copy()

    # Si falta la lluvia, asumimos 0 mm
    df["precipitation_mm"] = df["precipitation_mm"].fillna(0.0)

    # Si falta humedad, completamos con la mediana
    if df["humidity_pct"].isnull().any():
        mediana_humedad = df["humidity_pct"].median()
        df["humidity_pct"] = df["humidity_pct"].fillna(mediana_humedad)

    # Redondeo de variables numéricas a 2 decimales
    df["temperature_c"] = df["temperature_c"].round(2)
    df["precipitation_mm"] = df["precipitation_mm"].round(2)
    df["wind_speed_kmh"] = df["wind_speed_kmh"].round(2)

    # 4. Feature Engineering (creación de nuevas variables)
    df["wind_category"] = df["wind_speed_kmh"].apply(clasificar_viento)
    df["is_rainy"] = df["precipitation_mm"] > 0.0
    df["ingested_at"] = datetime.now()

    # Evitamos filas duplicadas en el mismo timestamp
    df = df.drop_duplicates(subset=["city", "timestamp"]).copy()

    # Ordenar columnas de la tabla horaria
    columnas_horarias = [
        "city", "timestamp", "temperature_c", "humidity_pct",
        "precipitation_mm", "wind_speed_kmh", "wind_category",
        "is_rainy", "ingested_at"
    ]
    df_hourly = df[columnas_horarias].copy()

    # 5. Agregación analítica por día (Data Mart / Resumen)
    df["date"] = df["timestamp"].dt.date

    df_daily = df.groupby(["city", "date"]).agg(
        temp_min_c=("temperature_c", "min"),
        temp_max_c=("temperature_c", "max"),
        temp_avg_c=("temperature_c", "mean"),
        total_precipitation_mm=("precipitation_mm", "sum"),
        avg_wind_speed_kmh=("wind_speed_kmh", "mean"),
        rainy_hours_count=("is_rainy", "sum")
    ).reset_index()

    # Redondeos en el resumen diario
    df_daily["temp_min_c"] = df_daily["temp_min_c"].round(2)
    df_daily["temp_max_c"] = df_daily["temp_max_c"].round(2)
    df_daily["temp_avg_c"] = df_daily["temp_avg_c"].round(2)
    df_daily["total_precipitation_mm"] = df_daily["total_precipitation_mm"].round(2)
    df_daily["avg_wind_speed_kmh"] = df_daily["avg_wind_speed_kmh"].round(2)
    df_daily["rainy_hours_count"] = df_daily["rainy_hours_count"].astype(int)
    df_daily["ingested_at"] = datetime.now()

    print(f"[TRANSFORM] Datos procesados: {len(df_hourly)} filas horarias y {len(df_daily)} días resumidos.")
    return df_hourly, df_daily
