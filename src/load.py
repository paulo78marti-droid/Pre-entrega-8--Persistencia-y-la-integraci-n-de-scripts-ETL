import logging
from typing import Dict, Any, List
import pandas as pd
from sqlalchemy import create_engine, Engine, text, select, func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

from config import settings
from src.models import Base, WeatherHourly, WeatherDailySummary

logger = logging.getLogger(__name__)


def get_db_engine(database_url: str = settings.DATABASE_URL) -> Engine:
    """Crea y retorna el Engine de SQLAlchemy 2.0 con pool y conexión segura."""
    return create_engine(database_url, echo=False)


def initialize_database(engine: Engine) -> None:
    """
    Inicializa el esquema de la base de datos creando las tablas e índices
    declarados en Base.metadata si no existen.
    """
    logger.info("Verificando/creando tablas e índices en la base de datos...")
    Base.metadata.create_all(engine)
    logger.info("Esquema relacional verificado exitosamente.")


def load_weather_hourly(engine: Engine, df_hourly: pd.DataFrame) -> int:
    """
    Carga registros horarios en la tabla 'weather_hourly' de manera IDEMPOTENTE.
    Utiliza SQLite UPSERT (ON CONFLICT (city, timestamp) DO UPDATE) para evitar duplicados.
    Se ejecuta dentro de una transacción gestionada.
    """
    if df_hourly.empty:
        logger.warning("df_hourly está vacío. No hay registros para cargar.")
        return 0

    records: List[Dict[str, Any]] = df_hourly.to_dict(orient="records")

    # En SQLAlchemy 2.0, ejecutamos el UPSERT en lotes para máxima eficiencia
    stmt = sqlite_upsert(WeatherHourly).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["city", "timestamp"],
        set_={
            "temperature_c": stmt.excluded.temperature_c,
            "humidity_pct": stmt.excluded.humidity_pct,
            "precipitation_mm": stmt.excluded.precipitation_mm,
            "wind_speed_kmh": stmt.excluded.wind_speed_kmh,
            "wind_category": stmt.excluded.wind_category,
            "is_rainy": stmt.excluded.is_rainy,
            "ingested_at": stmt.excluded.ingested_at,
        }
    )

    with engine.begin() as conn:
        result = conn.execute(upsert_stmt)
        rowcount = result.rowcount

    logger.info("Persistencia completada en 'weather_hourly': %d filas procesadas/actualizadas.", len(records))
    return rowcount


def load_weather_daily_summary(engine: Engine, df_daily: pd.DataFrame) -> int:
    """
    Carga resúmenes diarios agregados en la tabla 'weather_daily_summary' de manera IDEMPOTENTE.
    Utiliza SQLite UPSERT (ON CONFLICT (city, date) DO UPDATE) para evitar duplicados.
    """
    if df_daily.empty:
        logger.warning("df_daily está vacío. No hay resúmenes para cargar.")
        return 0

    records: List[Dict[str, Any]] = df_daily.to_dict(orient="records")

    stmt = sqlite_upsert(WeatherDailySummary).values(records)
    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["city", "date"],
        set_={
            "temp_min_c": stmt.excluded.temp_min_c,
            "temp_max_c": stmt.excluded.temp_max_c,
            "temp_avg_c": stmt.excluded.temp_avg_c,
            "total_precipitation_mm": stmt.excluded.total_precipitation_mm,
            "avg_wind_speed_kmh": stmt.excluded.avg_wind_speed_kmh,
            "rainy_hours_count": stmt.excluded.rainy_hours_count,
            "ingested_at": stmt.excluded.ingested_at,
        }
    )

    with engine.begin() as conn:
        result = conn.execute(upsert_stmt)
        rowcount = result.rowcount

    logger.info("Persistencia completada en 'weather_daily_summary': %d resúmenes procesados/actualizados.", len(records))
    return rowcount


def get_persistence_metrics(engine: Engine) -> Dict[str, Any]:
    """
    Consulta métricas de control y verificación de la base de datos persistida.
    """
    with Session(engine) as session:
        hourly_count = session.scalar(select(func.count(WeatherHourly.id)))
        daily_count = session.scalar(select(func.count(WeatherDailySummary.id)))
        
        # Muestra del último registro diario
        last_daily = session.scalars(
            select(WeatherDailySummary).order_by(WeatherDailySummary.date.desc()).limit(1)
        ).first()

    return {
        "total_hourly_records": hourly_count,
        "total_daily_summaries": daily_count,
        "latest_daily_summary": last_daily
    }
