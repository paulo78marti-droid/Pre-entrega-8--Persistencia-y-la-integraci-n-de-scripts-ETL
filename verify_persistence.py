"""
Script de Verificacion y Consultas SQL
Curso: Data Science II - Coderhouse
Pre-entrega: Persistencia y la integracion de scripts ETL

Ejecuta consultas SQL directas sobre la base de datos SQLite
para auditar y verificar que los datos fueron persistidos correctamente.
"""
import sys
from pathlib import Path
import pandas as pd

# Asegurar importacion desde la raiz
sys.path.append(str(Path(__file__).resolve().parent))

from sqlalchemy import text
from src.load import get_db_engine, get_persistence_metrics


def run_checks():
    engine = get_db_engine()

    print("=" * 65)
    print(" AUDITORIA Y VERIFICACION SQL DE DATOS EN SQLITE")
    print("=" * 65)

    # 1. Metricas generales de persistencia
    metricas = get_persistence_metrics(engine)
    print(f"Total registros en 'air_quality_measurements': {metricas['total_measurements']}")
    print(f"Total grupos en 'air_quality_summary':       {metricas['total_summary_groups']}")
    print("-" * 65)

    with engine.connect() as conn:
        # Consulta 1: Resumen analitico por nivel de calidad del aire
        print("\n[Consulta SQL 1] Resumen analitico consolidado (tabla 'air_quality_summary'):")
        df_resumen = pd.read_sql_query(
            "SELECT quality_level, record_count, avg_pm25, avg_pm10, avg_co2, avg_temperature, max_pm25 FROM air_quality_summary ORDER BY avg_pm25 ASC",
            conn
        )
        print(df_resumen.to_string(index=False))

        # Consulta 2: Top 5 mediciones con mayor nivel de PM2.5
        print("\n[Consulta SQL 2] 5 mediciones con niveles mas criticos de PM2.5:")
        df_top_pm = pd.read_sql_query("""
            SELECT measurement_id, pm25, pm10, co2, temperature, quality_level, is_high_pollution
            FROM air_quality_measurements
            ORDER BY pm25 DESC
            LIMIT 5;
        """, conn)
        print(df_top_pm.to_string(index=False))

        # Consulta 3: Comparativa segun flag de alta contaminacion
        print("\n[Consulta SQL 3] Mediciones segun condicion de alta contaminacion:")
        df_flag = pd.read_sql_query("""
            SELECT 
                CASE WHEN is_high_pollution = 1 THEN 'Si' ELSE 'No' END AS alta_contaminacion,
                COUNT(*) AS total_registros,
                ROUND(AVG(pm25), 2) AS pm25_promedio,
                ROUND(AVG(co2), 2) AS co2_promedio,
                ROUND(AVG(temperature), 2) AS temp_promedio
            FROM air_quality_measurements
            GROUP BY is_high_pollution;
        """, conn)
        print(df_flag.to_string(index=False))

    print("\n" + "=" * 65)
    print(" [OK] Verificacion SQL finalizada exitosamente.")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    run_checks()
