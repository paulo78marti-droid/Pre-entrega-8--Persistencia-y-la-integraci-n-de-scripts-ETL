"""
Módulo de Transformación (ETL)
Limpia, corrige tipos de datos, realiza feature engineering y calcula agregaciones diarias.
"""
from datetime import datetime
import pandas as pd
from config import settings


def classify_wind(velocidad_kmh):
    """
    Función simple para clasificar la velocidad del viento.
    """
    if velocidad_kmh < 12.0:
        return "Calma / Viento Leve"
    elif velocidad_kmh < 29.0:
        return "Brisa Moderada"
    elif velocidad_kmh < 50.0:
        return "Viento Fuerte"
    else:
        return "Temporal"


def transform_weather_data(raw_data, city=settings.CITY_NAME):
    """
    Transforma los datos crudos del clima en dos DataFrames listos para guardar:
    1. df_hourly: Mediciones detalladas por hora.
    2. df_daily: Resumen diario agregado con métricas (mín, máx, promedio).
    """
    hourly = raw_data.get("hourly", {})
    if not hourly:
        raise ValueError("No se encontraron datos en el nodo 'hourly'.")

    # 1. Crear el DataFrame inicial con los datos crudos
    df = pd.DataFrame({
        "timestamp_str": hourly.get("time", []),
        "temperature_c": hourly.get("temperature_2m", []),
        "humidity_pct": hourly.get("relative_humidity_2m", []),
        "precipitation_mm": hourly.get("precipitation", []),
        "wind_speed_kmh": hourly.get("wind_speed_10m", [])
    })

    print(f"[TRANSFORM] Filas crudas recibidas: {len(df)}")

    # 2. Corregir tipos de datos
    df["timestamp"] = pd.to_datetime(df["timestamp_str"])
    df["city"] = city

    # 3. Limpieza y tratamiento de valores nulos
    # Si falta la fecha o la temperatura, descartamos esas filas (datos no confiables)
    df = df.dropna(subset=["timestamp", "temperature_c"])

    # Si falta la precipitación, asumimos que no llovió (0.0 mm)
    df["precipitation_mm"] = df["precipitation_mm"].fillna(0.0)

    # Si faltara la humedad, rellenamos con la mediana
    if df["humidity_pct"].isnull().any():
        mediana_humedad = df["humidity_pct"].median()
        df["humidity_pct"] = df["humidity_pct"].fillna(mediana_humedad)

    # Redondear números a 2 decimales para prolijidad
    df["temperature_c"] = df["temperature_c"].round(2)
    df["precipitation_mm"] = df["precipitation_mm"].round(2)
    df["wind_speed_kmh"] = df["wind_speed_kmh"].round(2)

    # 4. Feature Engineering (Crear nuevas columnas útiles)
    df["wind_category"] = df["wind_speed_kmh"].apply(classify_wind)
    df["is_rainy"] = df["precipitation_mm"] > 0.0
    df["ingested_at"] = datetime.now()

    # Eliminar posibles duplicados de la misma hora en la misma ciudad
    df = df.drop_duplicates(subset=["city", "timestamp"]).copy()

    # Seleccionar las columnas en el orden deseado para la tabla horaria
    columnas_horarias = [
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
    df_hourly = df[columnas_horarias].copy()

    # 5. Agregación diaria (Creación de tabla analítica / resumen)
    df["date"] = df["timestamp"].dt.date

    df_daily = df.groupby(["city", "date"]).agg(
        temp_min_c=("temperature_c", "min"),
        temp_max_c=("temperature_c", "max"),
        temp_avg_c=("temperature_c", "mean"),
        total_precipitation_mm=("precipitation_mm", "sum"),
        avg_wind_speed_kmh=("wind_speed_kmh", "mean"),
        rainy_hours_count=("is_rainy", "sum")
    ).reset_index()

    # Redondeos de los cálculos diarios
    df_daily["temp_min_c"] = df_daily["temp_min_c"].round(2)
    df_daily["temp_max_c"] = df_daily["temp_max_c"].round(2)
    df_daily["temp_avg_c"] = df_daily["temp_avg_c"].round(2)
    df_daily["total_precipitation_mm"] = df_daily["total_precipitation_mm"].round(2)
    df_daily["avg_wind_speed_kmh"] = df_daily["avg_wind_speed_kmh"].round(2)
    df_daily["rainy_hours_count"] = df_daily["rainy_hours_count"].astype(int)
    df_daily["ingested_at"] = datetime.now()

    print(f"[TRANSFORM] Transformación completada: {len(df_hourly)} registros horarios y {len(df_daily)} resúmenes diarios.")
    return df_hourly, df_daily
