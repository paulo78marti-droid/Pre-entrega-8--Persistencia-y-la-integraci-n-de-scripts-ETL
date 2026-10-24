"""
Modulo de Transformacion (ETL)
Curso: Data Science II - Coderhouse

Limpia los datos de calidad del aire, normaliza nombres de columnas,
corrige valores atipicos negativos, realiza feature engineering basico
y genera una tabla analitica de resumen agrupado por nivel de calidad.
"""
from datetime import datetime
import pandas as pd


def clasificar_calidad_aire(pm25_valor):
    """
    Clasifica el nivel de calidad del aire segun la concentracion de PM2.5 (ug/m3)
    siguiendo estandares basicos de salud ambiental:
    - Buena: <= 35.4
    - Moderada: > 35.4 y <= 55.4
    - Danina: > 55.4
    """
    if pm25_valor <= 35.4:
        return "Buena"
    elif pm25_valor <= 55.4:
        return "Moderada"
    else:
        return "Danina"


def transform_air_quality_data(df_raw):
    """
    Transforma el DataFrame crudo de calidad del aire en dos conjuntos limpios:
    1. df_measurements: 500 mediciones individuales limpias con categorias y flags.
    2. df_summary: resumen analitico agregado por nivel de calidad del aire.
    """
    print(f"[TRANSFORM] Iniciando transformacion de {len(df_raw)} registros crudos...")

    df = df_raw.copy()

    # 1. Normalizacion de nombres de columnas a minusculas sin puntos
    column_mapping = {
        "PM2.5": "pm25",
        "PM10": "pm10",
        "NOx": "nox",
        "NO2": "no2",
        "SO2": "so2",
        "VOCs": "vocs",
        "CO": "co",
        "CO2": "co2",
        "CH4": "ch4",
        "Temperature": "temperature"
    }
    df = df.rename(columns=column_mapping)

    # 2. Asignar un identificador unico de medicion
    df["measurement_id"] = range(1, len(df) + 1)

    # 3. Tratamiento de nulos y tipos de datos
    # Verificamos si existen nulos y descartamos filas incompletas
    filas_con_nulos = df.isnull().any(axis=1).sum()
    if filas_con_nulos > 0:
        print(f"[TRANSFORM] Se detectaron {filas_con_nulos} filas con nulos; se procede a descartarlas.")
        df = df.dropna().copy()
    else:
        print("[TRANSFORM] No se encontraron valores nulos en el dataset.")

    # 4. Limpieza de datos: Correccion de concentraciones negativas
    # En sensores fisicos, valores negativos de gases suelen ser ruidos de calibracion.
    columnas_gases = ["pm25", "pm10", "nox", "no2", "so2", "vocs", "co", "co2", "ch4"]
    for col in columnas_gases:
        if (df[col] < 0).any():
            cantidad_negativos = (df[col] < 0).sum()
            print(f"[TRANSFORM] Corrigiendo {cantidad_negativos} valores negativos en '{col}' a 0.0")
            df[col] = df[col].clip(lower=0.0)

    # Redondeo general a 2 decimales para claridad y almacenamiento optimo
    todas_las_numericas = columnas_gases + ["temperature"]
    df[todas_las_numericas] = df[todas_las_numericas].round(2)

    # 5. Feature Engineering: Creacion de nuevas variables
    # a) Clasificacion del aire segun PM2.5
    df["quality_level"] = df["pm25"].apply(clasificar_calidad_aire)

    # b) Flag booleano de alta contaminacion (PM2.5 > 55.4 o CO2 > 500)
    df["is_high_pollution"] = (df["pm25"] > 55.4) | (df["co2"] > 500.0)

    # c) Timestamp de persistencia (trazabilidad)
    now = datetime.now()
    df["ingested_at"] = now

    # Columnas ordenadas para la tabla de mediciones
    cols_measurements = [
        "measurement_id", "pm25", "pm10", "nox", "no2", "so2",
        "vocs", "co", "co2", "ch4", "temperature",
        "quality_level", "is_high_pollution", "ingested_at"
    ]
    df_measurements = df[cols_measurements].copy()

    # 6. Agregacion Analitica: Resumen por nivel de calidad del aire
    df_summary = df.groupby("quality_level").agg(
        record_count=("measurement_id", "count"),
        avg_pm25=("pm25", "mean"),
        avg_pm10=("pm10", "mean"),
        avg_co2=("co2", "mean"),
        avg_temperature=("temperature", "mean"),
        max_pm25=("pm25", "max")
    ).reset_index()

    # Redondeos en el resumen
    df_summary["avg_pm25"] = df_summary["avg_pm25"].round(2)
    df_summary["avg_pm10"] = df_summary["avg_pm10"].round(2)
    df_summary["avg_co2"] = df_summary["avg_co2"].round(2)
    df_summary["avg_temperature"] = df_summary["avg_temperature"].round(2)
    df_summary["max_pm25"] = df_summary["max_pm25"].round(2)
    df_summary["ingested_at"] = now

    print(f"[TRANSFORM] Transformacion exitosa:")
    print(f"  • {len(df_measurements)} mediciones procesadas.")
    print(f"  • {len(df_summary)} grupos calculados en el resumen analitico.")

    return df_measurements, df_summary
