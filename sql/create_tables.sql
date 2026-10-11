-- ====================================================================
-- DDL: Creación de tablas para la Base de Datos Analítica Meteorológica
-- Motor: SQLite (compatible con SQLAlchemy 2.0)
-- ====================================================================

-- 1. Tabla de mediciones horarias detalladas
CREATE TABLE IF NOT EXISTS weather_hourly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature_c REAL NOT NULL,
    humidity_pct REAL,
    precipitation_mm REAL NOT NULL DEFAULT 0.0,
    wind_speed_kmh REAL NOT NULL,
    wind_category VARCHAR(30) NOT NULL,
    is_rainy BOOLEAN NOT NULL,
    ingested_at DATETIME NOT NULL,
    CONSTRAINT uq_city_timestamp UNIQUE (city, timestamp)
);

-- Índices para optimización de consultas analíticas
CREATE INDEX IF NOT EXISTS idx_weather_hourly_city_time 
ON weather_hourly (city, timestamp);

-- 2. Tabla de resumen agregado diario (Data Mart / capa analítica)
CREATE TABLE IF NOT EXISTS weather_daily_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    temp_min_c REAL NOT NULL,
    temp_max_c REAL NOT NULL,
    temp_avg_c REAL NOT NULL,
    total_precipitation_mm REAL NOT NULL DEFAULT 0.0,
    avg_wind_speed_kmh REAL NOT NULL,
    rainy_hours_count INTEGER NOT NULL DEFAULT 0,
    ingested_at DATETIME NOT NULL,
    CONSTRAINT uq_city_date UNIQUE (city, date)
);

-- Índice para consultas por fecha y ciudad
CREATE INDEX IF NOT EXISTS idx_weather_daily_city_date 
ON weather_daily_summary (city, date);
