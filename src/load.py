"""
Modulo de Carga y Persistencia (ETL)
Curso: Data Science II - Coderhouse

Conecta con SQLite mediante SQLAlchemy 2.0, inicializa las tablas
y persiste las mediciones y el resumen analitico, asegurando la prevencion de duplicados.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from config import settings
from src.models import Base


def get_db_engine():
    """Crea y retorna el Engine de SQLAlchemy conectado a SQLite."""
    return create_engine(settings.DATABASE_URL)


def initialize_database(engine):
    """Crea las tablas en la base de datos si aun no existen (DDL automatizado)."""
    print("[LOAD] Verificando esquema de tablas en SQLite...")
    Base.metadata.create_all(engine)
    print("[LOAD] Esquema de base de datos verificado y listo.")


def load_air_quality_measurements(engine, df_measurements):
    """
    Inserta las mediciones individuales en la tabla 'air_quality_measurements'.
    Implementa logica de idempotencia para evitar registros duplicados basandose
    en el identificador unico 'measurement_id'.
    """
    if df_measurements.empty:
        print("[LOAD] El DataFrame de mediciones esta vacio.")
        return 0

    # Consultar los identificadores que ya existen en la base de datos
    with engine.connect() as conn:
        query = text("SELECT measurement_id FROM air_quality_measurements")
        filas = conn.execute(query).fetchall()
        ids_existentes = set(f[0] for f in filas)

    # Filtrar solo registros que no esten cargados previamente
    df_nuevos = df_measurements[~df_measurements["measurement_id"].isin(ids_existentes)].copy()

    if not df_nuevos.empty:
        df_nuevos.to_sql("air_quality_measurements", con=engine, if_exists="append", index=False)
        print(f"[LOAD] Se insertaron {len(df_nuevos)} nuevas mediciones en 'air_quality_measurements'.")
        return len(df_nuevos)
    else:
        print("[LOAD] Todas las mediciones ya existen en la base de datos. Ninguna fila duplicada.")
        return 0


def load_air_quality_summary(engine, df_summary):
    """
    Carga el resumen analitico en la tabla 'air_quality_summary'.
    Para mantener la coherencia analitica y evitar duplicidad de grupos,
    actualiza la tabla con los valores consolidados mas recientes.
    """
    if df_summary.empty:
        print("[LOAD] El DataFrame de resumen esta vacio.")
        return 0

    with engine.begin() as conn:
        # Limpieza previa del resumen para asegurar que refleje el calculo consolidado actual
        conn.execute(text("DELETE FROM air_quality_summary"))
        df_summary.to_sql("air_quality_summary", con=conn, if_exists="append", index=False)

    print(f"[LOAD] Resumen analitico actualizado ({len(df_summary)} categorias) en 'air_quality_summary'.")
    return len(df_summary)


def get_persistence_metrics(engine):
    """
    Consulta y retorna las metricas de persistencia de la base de datos.
    """
    with engine.connect() as conn:
        total_mediciones = conn.execute(
            text("SELECT COUNT(*) FROM air_quality_measurements")
        ).scalar()
        total_resumen = conn.execute(
            text("SELECT COUNT(*) FROM air_quality_summary")
        ).scalar()

    return {
        "total_measurements": total_mediciones or 0,
        "total_summary_groups": total_resumen or 0
    }
