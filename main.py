"""
Script Principal del Pipeline ETL
Curso: Data Science II - Coderhouse

Ejecuta el flujo completo:
1. Conexión y preparación de la base de datos SQLite.
2. Extracción de datos climáticos desde la API Open-Meteo.
3. Transformación y limpieza con Pandas.
4. Carga y persistencia sin duplicados.
5. Resumen de registros guardados.
"""
import sys
from pathlib import Path

# Asegurar que Python reconozca la raíz del proyecto
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


def main():
    print("=" * 60)
    print(" INICIO DEL PIPELINE ETL - DATA SCIENCE II")
    print(f" Ciudad: {settings.CITY_NAME}")
    print(f" Base de Datos: SQLite ({settings.DB_FILE.name})")
    print("=" * 60)

    try:
        # 1. Preparar la Base de Datos
        print("\n[1/4] Inicializando base de datos SQLite...")
        engine = get_db_engine()
        initialize_database(engine)

        # 2. Extracción (Extract)
        print("\n[2/4] Extrayendo datos desde la API del clima...")
        raw_data = extract_weather_data()

        # 3. Transformación (Transform)
        print("\n[3/4] Limpiando datos y calculando métricas con Pandas...")
        df_hourly, df_daily = transform_weather_data(raw_data, city=settings.CITY_NAME)

        # 4. Carga (Load)
        print("\n[4/4] Guardando datos en SQLite (evitando duplicados)...")
        load_weather_hourly(engine, df_hourly)
        load_weather_daily_summary(engine, df_daily)

        # Resumen final
        metricas = get_persistence_metrics(engine)
        print("\n" + "-" * 60)
        print(" ESTADO DE LA BASE DE DATOS:")
        print(f"  • Registros horarios en 'weather_hourly': {metricas['total_hourly_records']}")
        print(f"  • Días resumidos en 'weather_daily_summary': {metricas['total_daily_summaries']}")
        print("-" * 60)
        print(" ¡Pipeline ETL ejecutado con éxito!\n")

    except Exception as error:
        print(f"\n[ERROR] Ocurrió un fallo en el pipeline: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
