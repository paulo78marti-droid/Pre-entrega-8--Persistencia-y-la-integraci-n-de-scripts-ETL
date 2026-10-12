"""
====================================================================
Pipeline ETL Meteorológico
Pre-entrega: Persistencia y la integración de scripts ETL
Curso: Coderhouse - Data Science II
====================================================================
Este script orquesta el flujo completo de:
1. Extracción de datos desde la API pública de Open-Meteo.
2. Transformación y limpieza de datos usando Pandas.
3. Carga y persistencia en una base de datos local SQLite con SQLAlchemy.
====================================================================
"""
import sys
from pathlib import Path

# Asegurar que Python reconozca las carpetas del proyecto
sys.path.append(str(Path(__file__).resolve().parent))

from config import settings
from src.extract import extract_weather_data
from src.transform import transform_weather_data
from src.load import (
    get_db_engine,
    initialize_database,
    load_weather_hourly,
    load_weather_daily_summary,
    get_persistence_metrics
)


def run_pipeline():
    """
    Función principal que ejecuta secuencialmente todas las etapas del ETL.
    """
    print("=" * 65)
    print(" INICIANDO PIPELINE ETL DE CLIMA (Coderhouse Data Science II)")
    print(f" Ciudad: {settings.CITY_NAME}")
    print(f" Base de Datos: {settings.DATABASE_URL}")
    print("=" * 65)

    try:
        # Paso 1: Configurar la base de datos y crear tablas
        print("\n[PASO 1] Conectando a SQLite y verificando tablas...")
        engine = get_db_engine()
        initialize_database(engine)

        # Paso 2: Extracción (E)
        print("\n[PASO 2] Extrayendo datos de la API pública...")
        raw_data = extract_weather_data()
        print("-> Extracción completada.")

        # Paso 3: Transformación (T)
        print("\n[PASO 3] Limpiando datos y calculando agregaciones...")
        df_hourly, df_daily = transform_weather_data(raw_data, city=settings.CITY_NAME)
        print("-> Transformación completada.")

        # Paso 4: Carga y Persistencia (L)
        print("\n[PASO 4] Cargando datos en la base de datos local SQLite...")
        load_weather_hourly(engine, df_hourly)
        load_weather_daily_summary(engine, df_daily)
        print("-> Carga completada.")

        # Paso 5: Métricas de control
        print("\n[PASO 5] Verificando métricas de persistencia...")
        metricas = get_persistence_metrics(engine)
        print("-" * 65)
        print(" RESUMEN EN BASE DE DATOS:")
        print(f"  - Total registros en 'weather_hourly': {metricas['total_hourly_records']}")
        print(f"  - Total resúmenes en 'weather_daily_summary': {metricas['total_daily_summaries']}")
        print("-" * 65)

        print("\n¡Pipeline ETL finalizado con éxito!")

    except Exception as error:
        print(f"\n[ERROR] Ocurrió un problema durante la ejecución: {error}")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
