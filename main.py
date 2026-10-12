import logging
import sys
import time
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path para portabilidad
sys.path.insert(0, str(Path(__file__).resolve().parent))

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

# Configurar sistema de logging estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ETL_Pipeline")


def run_pipeline() -> None:
    """Orquestador principal del pipeline ETL meteorológico."""
    start_time = time.perf_counter()
    logger.info("==========================================================")
    logger.info("Iniciando Pipeline ETL Meteorológico con SQLAlchemy 2.0")
    logger.info("Ciudad: %s (Lat: %s, Lon: %s)", settings.CITY_NAME, settings.LATITUDE, settings.LONGITUDE)
    logger.info("Destino: %s", settings.DATABASE_URL)
    logger.info("==========================================================")

    try:
        # 1. Configuración del motor y creación de esquema relacional
        engine = get_db_engine()
        initialize_database(engine)

        # 2. Extracción (E)
        logger.info("[Paso 1/3] Extrayendo datos desde Open-Meteo...")
        raw_data = extract_weather_data()
        logger.info("-> Extracción exitosa.")

        # 3. Transformación (T)
        logger.info("[Paso 2/3] Transformando y limpiando datos meteorológicos...")
        df_hourly, df_daily = transform_weather_data(raw_data, city=settings.CITY_NAME)
        logger.info("-> Transformación exitosa.")

        # 4. Carga y Persistencia (L)
        logger.info("[Paso 3/3] Persistiendo datos en SQLite con transacciones ACID e idempotencia...")
        load_weather_hourly(engine, df_hourly)
        load_weather_daily_summary(engine, df_daily)
        logger.info("-> Carga exitosa.")

        # 5. Verificación de Integridad y Métricas
        metrics = get_persistence_metrics(engine)
        logger.info("==========================================================")
        logger.info("Métricas de Persistencia en Base de Datos:")
        logger.info(" - Total registros en 'weather_hourly': %d", metrics["total_hourly_records"])
        logger.info(" - Total registros en 'weather_daily_summary': %d", metrics["total_daily_summaries"])
        if metrics["latest_daily_summary"]:
            logger.info(" - Último resumen diario: %s", metrics["latest_daily_summary"])
        logger.info("==========================================================")

        elapsed = time.perf_counter() - start_time
        logger.info("Pipeline completado exitosamente en %.2f segundos.", elapsed)

    except Exception as exc:
        logger.critical("Error fatal durante la ejecución del pipeline: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
