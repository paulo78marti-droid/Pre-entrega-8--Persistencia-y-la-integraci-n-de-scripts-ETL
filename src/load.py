"""
Módulo de Carga y Persistencia (ETL)
Conecta a la base de datos SQLite con SQLAlchemy, crea tablas y persiste los datos
evitando duplicados si el script se ejecuta múltiples veces.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from config import settings
from src.models import Base


def get_db_engine():
    """
    Crea y retorna el motor de conexión (Engine) de SQLAlchemy.
    """
    return create_engine(settings.DATABASE_URL)


def initialize_database(engine):
    """
    Crea las tablas en la base de datos SQLite si todavía no existen.
    Utiliza los modelos definidos en src/models.py.
    """
    print("[DB] Verificando esquema de tablas en SQLite...")
    Base.metadata.create_all(engine)
    print("[DB] Tablas verificadas exitosamente.")


def load_weather_hourly(engine, df_hourly):
    """
    Carga registros horarios en la tabla 'weather_hourly'.
    Para evitar duplicados, consulta qué marcas de tiempo ya existen
    y solo inserta las filas nuevas.
    """
    if df_hourly.empty:
        print("[LOAD] df_hourly está vacío. Nada que cargar.")
        return 0

    ciudad = df_hourly["city"].iloc[0]

    # 1. Consultar marcas de tiempo ya guardadas en la base de datos
    with engine.connect() as conn:
        query = text("SELECT timestamp FROM weather_hourly WHERE city = :city")
        resultado = conn.execute(query, {"city": ciudad}).fetchall()
        timestamps_existentes = set(pd.to_datetime(fila[0]) for fila in resultado)

    # 2. Filtrar únicamente las filas que no están en la base de datos
    df_nuevos = df_hourly[~pd.to_datetime(df_hourly["timestamp"]).isin(timestamps_existentes)].copy()

    # 3. Insertar filas nuevas usando to_sql de pandas
    if not df_nuevos.empty:
        df_nuevos.to_sql("weather_hourly", con=engine, if_exists="append", index=False)
        print(f"[LOAD] Se insertaron {len(df_nuevos)} nuevos registros en 'weather_hourly'.")
        return len(df_nuevos)
    else:
        print("[LOAD] Todos los registros horarios ya estaban en la base de datos. Ninguno duplicado.")
        return 0


def load_weather_daily_summary(engine, df_daily):
    """
    Carga resúmenes diarios en la tabla 'weather_daily_summary'.
    Evita duplicar resúmenes de fechas que ya fueron cargadas previamente.
    """
    if df_daily.empty:
        print("[LOAD] df_daily está vacío. Nada que cargar.")
        return 0

    ciudad = df_daily["city"].iloc[0]

    # 1. Consultar fechas que ya tienen resumen guardado
    with engine.connect() as conn:
        query = text("SELECT date FROM weather_daily_summary WHERE city = :city")
        resultado = conn.execute(query, {"city": ciudad}).fetchall()
        fechas_existentes = set(str(fila[0])[:10] for fila in resultado)

    # 2. Filtrar fechas nuevas
    df_nuevos = df_daily[~df_daily["date"].astype(str).isin(fechas_existentes)].copy()

    # 3. Insertar resúmenes nuevos
    if not df_nuevos.empty:
        df_nuevos.to_sql("weather_daily_summary", con=engine, if_exists="append", index=False)
        print(f"[LOAD] Se insertaron {len(df_nuevos)} nuevos resúmenes en 'weather_daily_summary'.")
        return len(df_nuevos)
    else:
        print("[LOAD] Todos los resúmenes diarios ya existían en la base de datos. Ninguno duplicado.")
        return 0


def get_persistence_metrics(engine):
    """
    Consulta métricas simples para verificar el estado de la base de datos.
    """
    with engine.connect() as conn:
        total_horarios = conn.execute(text("SELECT COUNT(*) FROM weather_hourly")).scalar()
        total_diarios = conn.execute(text("SELECT COUNT(*) FROM weather_daily_summary")).scalar()

    return {
        "total_hourly_records": total_horarios or 0,
        "total_daily_summaries": total_diarios or 0
    }
