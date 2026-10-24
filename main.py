"""
Script Principal del Pipeline ETL
Curso: Data Science II - Coderhouse
Pre-entrega: Persistencia y la integracion de scripts ETL

Ejecuta el flujo completo de automatizacion:
1. Conectar y preparar la base de datos SQLite con SQLAlchemy 2.0.
2. Extraccion del dataset de Calidad del Aire (Kaggle / Staging).
3. Transformacion y limpieza con Pandas (correccion de negativos, categorias y resumen).
4. Carga y persistencia en SQLite evitando duplicados.
5. Reporte de metricas persistidas.
"""
import sys
from pathlib import Path

# Asegurar que Python reconozca la raiz del proyecto
sys.path.append(str(Path(__file__).resolve().parent))

from config import settings
from src.extract import extract_air_quality_data
from src.transform import transform_air_quality_data
from src.load import (
    get_db_engine,
    initialize_database,
    load_air_quality_measurements,
    load_air_quality_summary,
    get_persistence_metrics
)


def run_pipeline():
    print("=" * 65)
    print(" PIPELINE ETL: CALIDAD DEL AIRE (DATA SCIENCE II - CODERHOUSE)")
    print(f" Fuente: Kaggle ({settings.KAGGLE_DATASET})")
    print(f" Destino: SQLite ({settings.DB_FILE.name})")
    print("=" * 65)

    try:
        # Paso 1: Inicializar la base de datos local
        print("\n[Paso 1/4] Inicializando base de datos SQLite...")
        engine = get_db_engine()
        initialize_database(engine)

        # Paso 2: Extraccion (Extract)
        print("\n[Paso 2/4] Extrayendo datos desde Kaggle / Staging...")
        df_raw = extract_air_quality_data()

        # Paso 3: Transformacion (Transform)
        print("\n[Paso 3/4] Limpiando datos y calculando resumen con Pandas...")
        df_measurements, df_summary = transform_air_quality_data(df_raw)

        # Paso 4: Carga y Persistencia (Load)
        print("\n[Paso 4/4] Guardando datos en SQLite (controlando duplicados)...")
        load_air_quality_measurements(engine, df_measurements)
        load_air_quality_summary(engine, df_summary)

        # Metricas finales de persistencia
        metricas = get_persistence_metrics(engine)
        print("\n" + "-" * 65)
        print(" ESTADO DE PERSISTENCIA EN SQLITE:")
        print(f"  • Registros en 'air_quality_measurements': {metricas['total_measurements']}")
        print(f"  • Grupos en 'air_quality_summary':       {metricas['total_summary_groups']}")
        print("-" * 65)
        print(" [OK] Pipeline ETL ejecutado exitosamente.\n")

    except Exception as error:
        print(f"\n[ERROR] Ocurrio una falla en el pipeline: {error}")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
