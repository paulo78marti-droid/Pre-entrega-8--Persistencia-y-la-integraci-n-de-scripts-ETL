"""
Script de Verificación y Consultas SQL
Curso: Data Science II - Coderhouse

Permite consultar directamente la base de datos SQLite con SQL
para auditar los datos persistidos por el pipeline.
"""
import sys
from pathlib import Path

# Permitir importar módulos de src y config
sys.path.append(str(Path(__file__).resolve().parent))

from sqlalchemy import text
from src.load import get_db_engine, get_persistence_metrics


def run_checks():
    engine = get_db_engine()

    print("=" * 60)
    print(" VERIFICACIÓN DE DATOS PERSISTIDOS EN SQLITE")
    print("=" * 60)

    # 1. Conteo total de registros
    metricas = get_persistence_metrics(engine)
    print(f"Total filas en 'weather_hourly':        {metricas['total_hourly_records']}")
    print(f"Total filas en 'weather_daily_summary': {metricas['total_daily_summaries']}")
    print("-" * 60)

    with engine.connect() as conn:
        # Consulta 1: Top 5 horas más calurosas
        print("\n[Consulta 1] 5 horas con mayor temperatura registrada:")
        q1 = conn.execute(text("""
            SELECT timestamp, temperature_c, wind_speed_kmh, wind_category
            FROM weather_hourly
            ORDER BY temperature_c DESC
            LIMIT 5;
        """)).fetchall()

        for fila in q1:
            print(f"  • {fila[0]} -> {fila[1]}°C | Viento: {fila[2]} km/h ({fila[3]})")

        # Consulta 2: Días con precipitaciones
        print("\n[Consulta 2] Días con registro de lluvias:")
        q2 = conn.execute(text("""
            SELECT date, total_precipitation_mm, rainy_hours_count, temp_avg_c
            FROM weather_daily_summary
            WHERE total_precipitation_mm > 0
            ORDER BY total_precipitation_mm DESC;
        """)).fetchall()

        if q2:
            for fila in q2:
                print(f"  • Fecha: {fila[0]} | Lluvia: {fila[1]} mm ({fila[2]} hs) | Temp Promedio: {fila[3]}°C")
        else:
            print("  (Sin días con precipitaciones registradas)")

        # Consulta 3: Agrupación por categoría de viento
        print("\n[Consulta 3] Horas acumuladas por categoría de viento:")
        q3 = conn.execute(text("""
            SELECT wind_category, COUNT(*) AS horas, ROUND(AVG(temperature_c), 2) AS temp_prom
            FROM weather_hourly
            GROUP BY wind_category
            ORDER BY horas DESC;
        """)).fetchall()

        for fila in q3:
            print(f"  • Viento {fila[0]:<10}: {fila[1]:<4} horas registradas (Temp Prom: {fila[2]}°C)")

    print("\n" + "=" * 60)
    print(" Verificación SQL finalizada con éxito.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_checks()
