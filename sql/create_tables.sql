-- ====================================================================
-- Script DDL: Creacion de tablas para la Base de Datos SQLite
-- Proyecto: Pipeline ETL de Calidad del Aire (Air Quality Dataset)
-- Curso: Coderhouse - Data Science II
-- Pre-entrega: Persistencia y la integracion de scripts ETL
-- ====================================================================

-- 1. Tabla de mediciones individuales (Datos limpios y transformados)
CREATE TABLE IF NOT EXISTS air_quality_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL UNIQUE,
    pm25 REAL NOT NULL,
    pm10 REAL NOT NULL,
    nox REAL NOT NULL,
    no2 REAL NOT NULL,
    so2 REAL NOT NULL,
    vocs REAL NOT NULL,
    co REAL NOT NULL,
    co2 REAL NOT NULL,
    ch4 REAL NOT NULL,
    temperature REAL NOT NULL,
    quality_level VARCHAR(30) NOT NULL,
    is_high_pollution BOOLEAN NOT NULL,
    ingested_at DATETIME NOT NULL
);

-- Indices para acelerar consultas analiticas por nivel de calidad y concentracion PM2.5
CREATE INDEX IF NOT EXISTS idx_air_quality_level 
ON air_quality_measurements (quality_level);

CREATE INDEX IF NOT EXISTS idx_air_quality_pm25 
ON air_quality_measurements (pm25);


-- 2. Tabla de resumen analitico (Agregacion / Data Mart)
-- Consolida metricas clave agrupadas por categoria de calidad del aire.
CREATE TABLE IF NOT EXISTS air_quality_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quality_level VARCHAR(30) NOT NULL UNIQUE,
    record_count INTEGER NOT NULL,
    avg_pm25 REAL NOT NULL,
    avg_pm10 REAL NOT NULL,
    avg_co2 REAL NOT NULL,
    avg_temperature REAL NOT NULL,
    max_pm25 REAL NOT NULL,
    ingested_at DATETIME NOT NULL
);

-- Indice para consultas rapidas sobre la tabla resumen
CREATE INDEX IF NOT EXISTS idx_air_summary_quality 
ON air_quality_summary (quality_level);
