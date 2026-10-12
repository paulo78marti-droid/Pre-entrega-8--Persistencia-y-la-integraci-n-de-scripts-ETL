"""
====================================================================
Script de Verificación y Consultas SQL
Pre-entrega: Persistencia y la integración de scripts ETL
Curso: Coderhouse - Data Science II
====================================================================
Permite auditar el contenido de la base de datos SQLite y realizar
consultas analíticas directas sobre los datos persistidos.
====================================================================
"""
import sys
from pathlib import Path

# Permitir importar módulos de src y config
sys.path.append(str(Path(__file__).resolve().parent))

from sqlalchemy import text
from src.load import get_db_engine, get_persistence_metrics


def run_checks():
    engine = get_db_engine()

    print("=" * 65)
    print(" VERIFICACIÓN DE PERSISTENCIA Y CONSULTAS SQL")
    print("=" * 65)

    # 1. Conteo general de registros
    metricas = get_persistence_metrics(engine)
    print(f"Registros horarios almacenados: {metricas['total_hourly_records']}")
    print(f"Resúmenes diarios almacenados:  {metricas['total_daily_summaries']}")
    print("-" * 65)

    with engine.connect() as conn:
        # Consulta 1: Horas más calurosas
        print("\n Consulta 1: Top 5 horas con mayor temperatura registrada")
        q1 = conn.execute(text("""
            SELECT city, timestamp, temperature_c, wind_speed_kmh, wind_category
            FROM weather_hourly
            ORDER BY temperature_c DESC
            LIMIT 5;
        """)).fetchall()

        for fila in q1:
            print(f"  {fila[0]} | {fila[1]} | {fila[2]}°C | Viento: {fila[3]} km/h ({fila[4]})")

        # Consulta 2: Días con lluvia
        print("\n Consulta 2: Días con lluvia acumulada")
        q2 = conn.execute(text("""
            SELECT city, date, total_precipitation_mm, rainy_hours_count, temp_avg_c
            FROM weather_daily_summary
            WHERE total_precipitation_mm > 0
            ORDER BY total_precipitation_mm DESC;
        """)).fetchall()

        if q2:
            for fila in q2:
                print(f"  {fila[0]} | {fila[1]} | Lluvia: {fila[2]} mm ({fila[3]} hs) | Temp media: {fila[4]}°C")
        else:
            print("  (No se registraron precipitaciones en los días consultados)")

        # Consulta 3: Agrupación por tipo de viento
        print("\n Consulta 3: Horas por categoría de viento")
        q3 = conn.execute(text("""
            SELECT wind_category, COUNT(*) AS total_horas, ROUND(AVG(temperature_c), 2) AS temp_promedio
            FROM weather_hourly
            GROUP BY wind_category
            ORDER BY total_horas DESC;
        """)).fetchall()

        for fila in q3:
            print(f"  Categoría: {fila[0]:<20} | Total Horas: {fila[1]:<4} | Temp Promedio: {fila[2]}°C")

    print("\n" + "=" * 65)
    print(" Verificación completada exitosamente.")
    print("=" * 65)


if __name__ == "__main__":
    run_checks()
