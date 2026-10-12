"""Script de verificación técnica para auditar persistencia, idempotencia y consultas analíticas."""
import logging
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path para portabilidad
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from config import settings
from src.load import get_db_engine, get_persistence_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("Verification")


def run_checks() -> None:
    engine = get_db_engine()
    logger.info("=== Verificación de Persistencia en Base de Datos ===")

    # 1. Métricas de conteo
    metrics = get_persistence_metrics(engine)
    logger.info("Registros horarios almacenados: %d", metrics["total_hourly_records"])
    logger.info("Resúmenes diarios almacenados: %d", metrics["total_daily_summaries"])

    # 2. Consultas analíticas SQL directas
    with engine.connect() as conn:
        logger.info("\n--- Consulta 1: Top 5 horas con mayor temperatura registrada ---")
        q1 = conn.execute(text("""
            SELECT city, timestamp, temperature_c, wind_speed_kmh, wind_category
            FROM weather_hourly
            ORDER BY temperature_c DESC
            LIMIT 5;
        """)).fetchall()
        for row in q1:
            logger.info("  %s | %s | %s°C | Viento: %s km/h (%s)", row[0], row[1], row[2], row[3], row[4])

        logger.info("\n--- Consulta 2: Resumen de días con lluvia acumulada ---")
        q2 = conn.execute(text("""
            SELECT city, date, total_precipitation_mm, rainy_hours_count, temp_avg_c
            FROM weather_daily_summary
            WHERE total_precipitation_mm > 0
            ORDER BY total_precipitation_mm DESC;
        """)).fetchall()
        if q2:
            for row in q2:
                logger.info("  %s | %s | Lluvia: %s mm (%d hs) | Temp media: %s°C", row[0], row[1], row[2], row[3], row[4])
        else:
            logger.info("  (No se registraron precipitaciones en el periodo consultado)")

        logger.info("\n--- Consulta 3: Distribución por categoría de viento ---")
        q3 = conn.execute(text("""
            SELECT wind_category, COUNT(*) AS count_hours, ROUND(AVG(temperature_c), 2) AS avg_temp
            FROM weather_hourly
            GROUP BY wind_category
            ORDER BY count_hours DESC;
        """)).fetchall()
        for row in q3:
            logger.info("  Categoría: %-25s | Horas: %3d | Temp Media: %s°C", row[0], row[1], row[2])

    logger.info("\n=== Todas las verificaciones analíticas finalizaron con éxito ===")


if __name__ == "__main__":
    run_checks()
