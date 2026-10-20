"""
Módulo de Carga y Persistencia (ETL)
Curso: Data Science II - Coderhouse

Conecta con SQLite usando SQLAlchemy, crea las tablas si no existen
y guarda los datos evitando duplicados si el script se vuelve a ejecutar.
"""
import pandas as pd
from sqlalchemy import create_engine, text
from config import settings
from src.models import Base


def get_db_engine():
    """Crea y retorna la conexión con la base de datos SQLite."""
    return create_engine(settings.DATABASE_URL)


def initialize_database(engine):
    """Crea las tablas en la base de datos si aún no existen."""
    print("[LOAD] Verificando tablas en SQLite...")
    Base.metadata.create_all(engine)
    print("[LOAD] Tablas listas.")


def load_weather_hourly(engine, df_hourly):
    """
    Inserta las mediciones horarias en 'weather_hourly'.
    Comprueba qué timestamps ya existen para no duplicar datos.
    """
    if df_hourly.empty:
        print("[LOAD] df_hourly no contiene datos.")
        return 0

    ciudad = df_hourly["city"].iloc[0]

    # Consultar qué fechas y horas ya están en la base de datos
    with engine.connect() as conn:
        query = text("SELECT timestamp FROM weather_hourly WHERE city = :city")
        filas = conn.execute(query, {"city": ciudad}).fetchall()
        timestamps_existentes = set(pd.to_datetime(f[0]) for f in filas)

    # Filtrar solo los registros que aún no se guardaron
    df_nuevos = df_hourly[~pd.to_datetime(df_hourly["timestamp"]).isin(timestamps_existentes)].copy()

    # Guardar en SQLite
    if not df_nuevos.empty:
        df_nuevos.to_sql("weather_hourly", con=engine, if_exists="append", index=False)
        print(f"[LOAD] Se insertaron {len(df_nuevos)} nuevos registros horarios.")
        return len(df_nuevos)
    else:
        print("[LOAD] Todos los datos horarios ya existen en la base. Ninguno duplicado.")
        return 0


def load_weather_daily_summary(engine, df_daily):
    """
    Inserta los resúmenes diarios en 'weather_daily_summary'.
    Comprueba qué fechas ya existen para no duplicar registros.
    """
    if df_daily.empty:
        print("[LOAD] df_daily no contiene datos.")
        return 0

    ciudad = df_daily["city"].iloc[0]

    # Consultar qué fechas ya tienen resumen guardado
    with engine.connect() as conn:
        query = text("SELECT date FROM weather_daily_summary WHERE city = :city")
        filas = conn.execute(query, {"city": ciudad}).fetchall()
        fechas_existentes = set(str(f[0])[:10] for f in filas)

    # Filtrar solo los días nuevos
    df_nuevos = df_daily[~df_daily["date"].astype(str).isin(fechas_existentes)].copy()

    # Guardar en SQLite
    if not df_nuevos.empty:
        df_nuevos.to_sql("weather_daily_summary", con=engine, if_exists="append", index=False)
        print(f"[LOAD] Se insertaron {len(df_nuevos)} nuevos resúmenes diarios.")
        return len(df_nuevos)
    else:
        print("[LOAD] Todos los resúmenes diarios ya existen en la base. Ninguno duplicado.")
        return 0


def get_persistence_metrics(engine):
    """Retorna el total de filas guardadas en cada tabla."""
    with engine.connect() as conn:
        total_horarios = conn.execute(text("SELECT COUNT(*) FROM weather_hourly")).scalar()
        total_diarios = conn.execute(text("SELECT COUNT(*) FROM weather_daily_summary")).scalar()

    return {
        "total_hourly_records": total_horarios or 0,
        "total_daily_summaries": total_diarios or 0
    }
