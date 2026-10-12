# Pipeline ETL Meteorológico con Persistencia en SQLAlchemy 2.0 y SQLite

Este proyecto implementa un flujo automatizado de extracción, transformación y carga (**ETL**) de datos meteorológicos obtenidos de la **API pública Open-Meteo**, con persistencia en una base de datos relacional analítica (**SQLite**) utilizando **SQLAlchemy 2.0**.

El diseño aplica los patrones de ingeniería de datos y persistencia del **Módulo 9 (Automatización y Patrones de Datos)**:
- **Staging Area:** Aislamiento de datos crudos antes de su procesamiento.
- **Transacciones ACID:** Garantía de atomicidad mediante context managers (`begin()` / `commit()` / `rollback()`).
- **Idempotencia:** Prevención estricta de duplicación de datos ante múltiples ejecuciones sucesivas (mediante cláusulas *UPSERT*).
- **Mapeo ORM Declarativo 2.0:** Definición moderna de esquemas utilizando `DeclarativeBase`, `Mapped` y `mapped_column`.

---

## 1. Arquitectura del Proyecto

```text
Pre-entrega 8- Persistencia y la integración de scripts ETL/
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuración centralizada (.env, rutas y parámetros)
│
├── data/
│   ├── raw/                 # Staging Area para datos crudos (JSON)
│   │   ├── .gitkeep
│   │   └── weather_raw_latest.json
│   └── weather_analytics.db # Base de datos analítica SQLite (generada al ejecutar)
│
├── sql/
│   └── create_tables.sql    # DDL explícito de creación de tablas e índices
│
├── src/
│   ├── __init__.py
│   ├── models.py            # Modelos ORM declarativos en SQLAlchemy 2.0
│   ├── extract.py           # Extracción con reintentos exponenciales y staging
│   ├── transform.py         # Limpieza, tipado, feature engineering y agregación
│   └── load.py              # Persistencia transaccional ACID e idempotente (UPSERT)
│
├── main.py                  # Orquestador del flujo ETL completo
├── verify_persistence.py    # Script de auditoría y consultas analíticas SQL
├── requirements.txt         # Dependencias del proyecto
├── .env.example             # Plantilla de variables de entorno
├── .gitignore               # Exclusión de archivos binarios, caches y secretos
└── README.md                # Documentación técnica del proyecto
```

---

## 2. Flujo del Pipeline (ETL)

```mermaid
flowchart LR
    A[Open-Meteo API] -->|GET con Backoff| B[Staging Area: data/raw/]
    B -->|Normalización y Tipado| C[Transformación & Feature Engineering]
    C -->|df_hourly / df_daily| D[Persistencia Transaccional SQLAlchemy 2.0]
    D -->|UPSERT Idempotente| E[(SQLite: weather_analytics.db)]
```

1. **Extracción (`src/extract.py`)**:
   - Consulta el endpoint de pronóstico y datos históricos de Open-Meteo para las coordenadas configuradas (por defecto: Buenos Aires, Lat: -34.61, Lon: -58.38).
   - Implementa reintentos automáticos con **backoff exponencial** ante respuestas HTTP transitorias (códigos 429, 500, 502, 503, 504) y *timeout* preventivo.
   - Aplica el patrón **Staging Area** guardando la respuesta cruda en `data/raw/weather_raw_latest.json`.

2. **Transformación (`src/transform.py`)**:
   - Conversión de marcas temporales a objetos `datetime`.
   - Limpieza y tratamiento justificado de valores nulos.
   - **Feature Engineering**: Clasificación de viento (`wind_category` según escala Beaufort) y bandera de lluvia (`is_rainy`).
   - **Agregación diaria**: Cálculo de KPIs meteorológicos diarios (`temp_min_c`, `temp_max_c`, `temp_avg_c`, `total_precipitation_mm`, `avg_wind_speed_kmh`, `rainy_hours_count`).

3. **Carga y Persistencia (`src/load.py`)**:
   - Conexión vía `create_engine()` de SQLAlchemy 2.0.
   - Creación automática del esquema relacional si no existe (`Base.metadata.create_all()`).
   - Inserción de registros mediante **UPSERT** (`on_conflict_do_update`) sobre claves únicas `(city, timestamp)` y `(city, date)`, asegurando **idempotencia total**.
   - Manejo transaccional bajo estándar ACID (la transacción revierte automáticamente cualquier fallo sin dejar estados inconsistentes).

---

## 3. Modelo de Datos y Esquema DDL

El esquema analítico se compone de dos tablas optimizadas:

### Tabla `weather_hourly` (Mediciones Horarias)
| Columna | Tipo SQL | Restricción / Índice | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Clave subrogada de registro |
| `city` | `VARCHAR(50)` | `NOT NULL` | Nombre de la ciudad monitoreada |
| `timestamp` | `DATETIME` | `NOT NULL` | Marca temporal horaria de la medición |
| `temperature_c` | `REAL` | `NOT NULL` | Temperatura a 2 metros (°C) |
| `humidity_pct` | `REAL` | `NULLABLE` | Humedad relativa (%) |
| `precipitation_mm` | `REAL` | `NOT NULL DEFAULT 0.0` | Precipitación acumulada en la hora (mm) |
| `wind_speed_kmh` | `REAL` | `NOT NULL` | Velocidad del viento a 10 metros (km/h) |
| `wind_category` | `VARCHAR(30)` | `NOT NULL` | Categoría derivada del viento |
| `is_rainy` | `BOOLEAN` | `NOT NULL` | Flag booleano de presencia de lluvia |
| `ingested_at` | `DATETIME` | `NOT NULL` | Marca temporal de ingesta (UTC) |
| **Constraint** | `UNIQUE` | `(city, timestamp)` | Evita duplicidad de observaciones |

### Tabla `weather_daily_summary` (Data Mart Diario)
| Columna | Tipo SQL | Restricción / Índice | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Clave primaria |
| `city` | `VARCHAR(50)` | `NOT NULL` | Ciudad |
| `date` | `DATE` | `NOT NULL` | Fecha del día resumido |
| `temp_min_c` | `REAL` | `NOT NULL` | Temperatura mínima del día (°C) |
| `temp_max_c` | `REAL` | `NOT NULL` | Temperatura máxima del día (°C) |
| `temp_avg_c` | `REAL` | `NOT NULL` | Temperatura promedio del día (°C) |
| `total_precipitation_mm`| `REAL` | `NOT NULL` | Precipitación total acumulada (mm) |
| `avg_wind_speed_kmh` | `REAL` | `NOT NULL` | Velocidad promedio de viento (km/h) |
| `rainy_hours_count` | `INTEGER` | `NOT NULL` | Cantidad de horas con lluvia |
| `ingested_at` | `DATETIME` | `NOT NULL` | Fecha y hora de procesamiento |
| **Constraint** | `UNIQUE` | `(city, date)` | Evita duplicidad de resúmenes diarios |

El archivo SQL DDL independiente se encuentra disponible en [`sql/create_tables.sql`](sql/create_tables.sql).

---

## 4. Requisitos y Configuración del Entorno

### Requisitos previos
- Python 3.10 o superior (recomendado Python 3.11 / 3.12).
- Git instalado.

### Paso 1: Clonar el repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd "Pre-entrega 8- Persistencia y la integración de scripts ETL"
```

### Paso 2: Crear y activar entorno virtual

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno (opcional)
Copiar la plantilla de configuración `.env.example` a `.env`:
```bash
cp .env.example .env
```
*(Si no se crea `.env`, el sistema utilizará automáticamente los valores seguros por defecto definidos en `config/settings.py`)*.

---

## 5. Pasos para Ejecutar

### Ejecución del Pipeline ETL
Para ejecutar el flujo completo de ingesta, transformación y carga en la base de datos:
```bash
python main.py
```

**Salida esperada en consola:**
```text
2026-10-11 09:49:25 [INFO] ETL_Pipeline: ==========================================================
2026-10-11 09:49:25 [INFO] ETL_Pipeline: Iniciando Pipeline ETL Meteorológico con SQLAlchemy 2.0
2026-10-11 09:49:25 [INFO] ETL_Pipeline: Ciudad: Buenos Aires (Lat: -34.61, Lon: -58.38)
2026-10-11 09:49:25 [INFO] ETL_Pipeline: Destino: sqlite:///.../data/weather_analytics.db
2026-10-11 09:49:25 [INFO] ETL_Pipeline: ==========================================================
2026-10-11 09:49:25 [INFO] src.load: Verificando/creando tablas e índices en la base de datos...
2026-10-11 09:49:25 [INFO] src.load: Esquema relacional verificado exitosamente.
2026-10-11 09:49:25 [INFO] ETL_Pipeline: [Paso 1/3] Extrayendo datos desde Open-Meteo...
2026-10-11 09:49:26 [INFO] src.extract: Datos crudos persistidos en Staging: .../data/raw/weather_raw_latest.json
2026-10-11 09:49:26 [INFO] ETL_Pipeline: -> Extracción exitosa.
2026-10-11 09:49:26 [INFO] ETL_Pipeline: [Paso 2/3] Transformando y limpiando datos meteorológicos...
2026-10-11 09:49:26 [INFO] src.transform: Transformación completa: 240 registros horarios, 10 resúmenes diarios generados.
2026-10-11 09:49:26 [INFO] ETL_Pipeline: -> Transformación exitosa.
2026-10-11 09:49:26 [INFO] ETL_Pipeline: [Paso 3/3] Persistiendo datos en SQLite con transacciones ACID e idempotencia...
2026-10-11 09:49:26 [INFO] src.load: Persistencia completada en 'weather_hourly'...
2026-10-11 09:49:26 [INFO] src.load: Persistencia completada en 'weather_daily_summary'...
2026-10-11 09:49:26 [INFO] ETL_Pipeline: -> Carga exitosa.
2026-10-11 09:49:26 [INFO] ETL_Pipeline: ==========================================================
2026-10-11 09:49:26 [INFO] ETL_Pipeline: Métricas de Persistencia en Base de Datos:
2026-10-11 09:49:26 [INFO] ETL_Pipeline:  - Total registros en 'weather_hourly': 240
2026-10-11 09:49:26 [INFO] ETL_Pipeline:  - Total registros en 'weather_daily_summary': 10
2026-10-11 09:49:26 [INFO] ETL_Pipeline: ==========================================================
2026-10-11 09:49:26 [INFO] ETL_Pipeline: Pipeline completado exitosamente en 1.84 segundos.
```

### Auditoría y Consultas Analíticas
Para verificar el estado de la base de datos persistida y ejecutar consultas analíticas sobre los datos:
```bash
python verify_persistence.py
```

---

## 6. Demostración de Idempotencia y Manejo de Errores

### Prueba de Idempotencia
Si se ejecuta `python main.py` múltiples veces seguidas:
1. El script detecta los registros existentes mediante la restricción única `(city, timestamp)` y `(city, date)`.
2. Se ejecuta un `UPSERT` actualizando métricas sin generar duplicados.
3. El conteo de registros se mantiene estable y consistente.

### Tolerancia a Fallos de Red
Si la conexión a la API se interrumpe o falla:
1. El script activa el protocolo de **reintentos con backoff exponencial** (hasta 5 intentos).
2. Si la conexión sigue caída, `src/extract.py` recurre de forma resiliente al último archivo guardado en el área de **Staging** (`data/raw/weather_raw_latest.json`), permitiendo que el pipeline complete la carga y transformación.
