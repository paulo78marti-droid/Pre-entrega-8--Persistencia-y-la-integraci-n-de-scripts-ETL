# Pipeline ETL de Calidad del Aire con SQLite y SQLAlchemy

**Curso:** Data Science II — Coderhouse  
**Entrega:** Pre-entrega — Persistencia y la integración de scripts ETL (Módulo 9, págs. 187 - 188)  
**Estudiante:** Paulo Martin  

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/paulo78marti-droid/Pre-entrega-8--Persistencia-y-la-integraci-n-de-scripts-ETL/blob/master/Pre-entrega_8_ETL.ipynb)

---

## 1. Descripción del Proyecto

El objetivo de esta pre-entrega es implementar un pipeline de datos automatizado que realice de punta a punta las tres etapas de un proceso **ETL (Extract, Transform, Load)** y persista los datos en una base de datos relacional local (**SQLite**) asegurando repetibilidad, manejo de errores y prevención de duplicados:

1. **Extracción (Extract):** Descarga el dataset de Calidad del Aire (`srisyra02/air-quality-dataset`) desde Kaggle mediante la librería `kagglehub` y almacena una copia en el área de transición (*Staging Area* en `data/raw/`).
2. **Transformación (Transform):** Utiliza **Pandas** para estandarizar nombres de columnas a snake_case, corregir valores físicos erróneos (ruidos negativos en sensores de gases), realizar *feature engineering* básico (clasificación de calidad del aire según concentración de PM2.5 y flag de alta contaminación) y calcular una tabla de resumen analítico agrupado.
3. **Carga y Persistencia (Load):** Almacena la información en una base de datos local **SQLite** utilizando el ORM **SQLAlchemy 2.0** (`Mapped` y `mapped_column`), implementando una lógica de **idempotencia** para evitar la inserción de registros duplicados si el script se vuelve a ejecutar.

---

## 2. Estructura del Repositorio

El proyecto está organizado de manera modular, separando responsabilidades:

```text
Pre-entrega 8- Persistencia y la integración de scripts ETL/
│
├── Pre-entrega_8_ETL.ipynb      # Cuaderno interactivo ejecutable paso a paso (y en Google Colab)
├── config/
│   ├── __init__.py
│   └── settings.py              # Parámetros de configuración, rutas del proyecto y BD
│
├── data/
│   ├── raw/                     # Área de transición (Staging Area) para datos crudos
│   │   ├── .gitkeep
│   │   └── air_quality_dataset.csv # Copia local de respaldo para ejecución sin conexión
│   └── air_quality.db           # Base de datos relacional SQLite (generada al ejecutar)
│
├── sql/
│   └── create_tables.sql        # Script DDL en SQL con sentencias CREATE TABLE e índices
│
├── src/
│   ├── __init__.py
│   ├── models.py                # Modelos de tablas con SQLAlchemy 2.0
│   ├── extract.py               # Extracción desde Kaggle con kagglehub y respaldo local
│   ├── transform.py             # Limpieza, saneamiento y agregación con Pandas
│   └── load.py                  # Carga en SQLite y lógica para evitar duplicados
│
├── main.py                      # Script principal que orquesta el pipeline completo
├── verify_persistence.py        # Script de auditoría con consultas SQL directas (SELECT)
├── requirements.txt             # Librerías y dependencias necesarias
├── .env.example                 # Variables de entorno y configuración de ejemplo
├── .gitignore                   # Archivos y bases de datos excluidos de Git
└── README.md                    # Documentación y guía de ejecución
```

---

## 3. Requisitos del Entorno

Para ejecutar este proyecto en tu computadora local necesitas:
- **Python 3.10 o superior**.
- Las dependencias listadas en `requirements.txt`:
  - `kagglehub`: descarga automatizada de datasets desde Kaggle.
  - `pandas`: lectura, limpieza, transformación y agregación de datos.
  - `sqlalchemy`: conexión ORM y persistencia en base de datos SQLite.
  - `python-dotenv`: gestión segura de configuraciones por variables de entorno.

---

## 4. Pasos para Ejecutar

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/paulo78marti-droid/Pre-entrega-8--Persistencia-y-la-integraci-n-de-scripts-ETL.git
cd "Pre-entrega-8--Persistencia-y-la-integraci-n-de-scripts-ETL"
```

### Paso 2: Crear y activar un entorno virtual (recomendado)

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**En Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar las dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar el Pipeline ETL
Ejecuta el script principal:
```bash
python main.py
```

**Salida esperada en consola:**
```text
=================================================================
 PIPELINE ETL: CALIDAD DEL AIRE (DATA SCIENCE II - CODERHOUSE)
 Fuente: Kaggle (srisyra02/air-quality-dataset)
 Destino: SQLite (air_quality.db)
=================================================================

[Paso 1/4] Inicializando base de datos SQLite...
[LOAD] Verificando esquema de tablas en SQLite...
[LOAD] Esquema de base de datos verificado y listo.

[Paso 2/4] Extrayendo datos desde Kaggle / Staging...
[EXTRACT] Conectando con Kaggle para descargar: 'srisyra02/air-quality-dataset'...
[EXTRACT] Copia guardada en Staging Area: data/raw/air_quality_dataset.csv
[EXTRACT] Extracción completada con éxito: 500 filas y 10 columnas.

[Paso 3/4] Limpiando datos y calculando resumen con Pandas...
[TRANSFORM] Iniciando transformación de 500 registros crudos...
[TRANSFORM] No se encontraron valores nulos en el dataset.
[TRANSFORM] Corrigiendo 1 valores negativos en 'nox' a 0.0
[TRANSFORM] Corrigiendo 1 valores negativos en 'no2' a 0.0
[TRANSFORM] Corrigiendo 2 valores negativos en 'so2' a 0.0
[TRANSFORM] Transformación exitosa:
  • 500 mediciones procesadas.
  • 3 grupos calculados en el resumen analítico.

[Paso 4/4] Guardando datos en SQLite (controlando duplicados)...
[LOAD] Se insertaron 500 nuevas mediciones en 'air_quality_measurements'.
[LOAD] Resumen analítico actualizado (3 categorías) en 'air_quality_summary'.

-----------------------------------------------------------------
 ESTADO DE PERSISTENCIA EN SQLITE:
  • Registros en 'air_quality_measurements': 500
  • Grupos en 'air_quality_summary':       3
-----------------------------------------------------------------
 [OK] Pipeline ETL ejecutado exitosamente.
```

### Paso 5: Probar la prevención de duplicados (Idempotencia)
Si vuelves a ejecutar el script:
```bash
python main.py
```
El pipeline consultará la base de datos, identificará que las 500 mediciones ya fueron cargadas y **no duplicará registros**:
```text
[LOAD] Todas las mediciones ya existen en la base de datos. Ninguna fila duplicada.
```

### Paso 6: Auditar la base de datos con consultas SQL
Para consultar y verificar que los datos se almacenaron correctamente:
```bash
python verify_persistence.py
```
Este script ejecuta consultas SQL analíticas con `SELECT`:
- Resumen consolidado por nivel de calidad del aire.
- Top 5 mediciones con mayor concentración de partículas PM2.5.
- Agrupación según la condición de alta contaminación (`is_high_pollution`).

---

## 5. Explicación del Flujo ETL

### 1. Extracción (`src/extract.py`)
- Se conecta a la API de Kaggle con `kagglehub.dataset_download("srisyra02/air-quality-dataset")`.
- Aplica el patrón de **Staging Area**: guarda una copia del CSV original en `data/raw/air_quality_dataset.csv`.
- Manejo de excepciones: si no hay conexión a internet o falla la descarga, el script utiliza automáticamente la copia local en `data/raw/` sin detener el pipeline.

### 2. Transformación (`src/transform.py`)
- **Estandarización de columnas:** Renombra variables como `PM2.5` a `pm25`, `NOx` a `nox`, etc.
- **Identificador único:** Crea la columna `measurement_id` (1 a 500) para trazabilidad.
- **Saneamiento físico:** Los sensores químicos a veces registran valores negativos por descalibración; estos valores se truncan a `0.0`.
- **Feature Engineering:**
  - `quality_level`: Clasificación según PM2.5 (*Buena* $\le 35.4$, *Moderada* $\le 55.4$, *Dañina* $> 55.4$).
  - `is_high_pollution`: Indicador booleano de alerta (`True` si `pm25 > 55.4` o `co2 > 500.0`).
  - `ingested_at`: Marca de tiempo de la carga.
- **Agregación analítica:** Agrupa por `quality_level` calculando la cantidad de mediciones, promedios de PM2.5, PM10, CO2, temperatura y máximo de PM2.5.

### 3. Carga y Persistencia (`src/load.py` y `src/models.py`)
- Utiliza **SQLAlchemy 2.0** para interactuar con SQLite mediante objetos Python y sentencias seguras.
- Crea las tablas automáticamente mediante `Base.metadata.create_all(engine)`.
- **Control de Duplicados:** Antes de insertar en `air_quality_measurements`, consulta los `measurement_id` existentes y solo inserta filas nuevas. Para `air_quality_summary`, actualiza el consolidado para reflejar siempre el estado actual.

---

## 6. Esquema de Persistencia y DDL

Las tablas diseñadas en SQLite son:

### Tabla: `air_quality_measurements` (Mediciones individuales limpias)
| Columna | Tipo SQL | Restricción | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | ID interno de base de datos |
| `measurement_id` | `INTEGER` | `UNIQUE NOT NULL` | Identificador de medición de origen |
| `pm25` | `REAL` | `NOT NULL` | Material particulado fino ($\mu g/m^3$) |
| `pm10` | `REAL` | `NOT NULL` | Material particulado grueso ($\mu g/m^3$) |
| `nox` | `REAL` | `NOT NULL` | Óxidos de nitrógeno |
| `no2` | `REAL` | `NOT NULL` | Dióxido de nitrógeno |
| `so2` | `REAL` | `NOT NULL` | Dióxido de azufre |
| `vocs` | `REAL` | `NOT NULL` | Compuestos orgánicos volátiles |
| `co` | `REAL` | `NOT NULL` | Monóxido de carbono |
| `co2` | `REAL` | `NOT NULL` | Dióxido de carbono |
| `ch4` | `REAL` | `NOT NULL` | Metano |
| `temperature` | `REAL` | `NOT NULL` | Temperatura ambiente (°C) |
| `quality_level` | `VARCHAR(30)` | `NOT NULL` | Calidad de aire (Buena, Moderada, Dañina) |
| `is_high_pollution` | `BOOLEAN` | `NOT NULL` | Flag de alta contaminación (True/False) |
| `ingested_at` | `DATETIME` | `NOT NULL` | Fecha y hora de procesamiento ETL |

### Tabla: `air_quality_summary` (Data Mart / Resumen agregado)
| Columna | Tipo SQL | Restricción | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | ID interno de base de datos |
| `quality_level` | `VARCHAR(30)` | `UNIQUE NOT NULL` | Categoría de calidad del aire |
| `record_count` | `INTEGER` | `NOT NULL` | Cantidad de mediciones en la categoría |
| `avg_pm25` | `REAL` | `NOT NULL` | Promedio de PM2.5 en la categoría |
| `avg_pm10` | `REAL` | `NOT NULL` | Promedio de PM10 en la categoría |
| `avg_co2` | `REAL` | `NOT NULL` | Promedio de CO2 en la categoría |
| `avg_temperature` | `REAL` | `NOT NULL` | Promedio de temperatura |
| `max_pm25` | `REAL` | `NOT NULL` | Concentración máxima de PM2.5 |
| `ingested_at` | `DATETIME` | `NOT NULL` | Fecha y hora de procesamiento ETL |

El archivo SQL nativo con las sentencias DDL correspondientes se encuentra en [`sql/create_tables.sql`](sql/create_tables.sql).

---

## 7. Justificación de Decisiones Técnicas (Nivel Inicial)

- **¿Por qué SQLite?**  
  Es un motor relacional embebido que almacena toda la base de datos en un solo archivo (`.db`). No requiere configurar servidores ni credenciales complejas, lo que garantiza que cualquier evaluador pueda clonar el repositorio y ejecutar el proyecto inmediatamente.
- **¿Por qué SQLAlchemy 2.0?**  
  Permite definir el modelo de datos como clases de Python (`Mapped` y `mapped_column`), evitando errores de tipeo en sentencias SQL manuales y gestionando conexiones seguras.
- **¿Por qué Staging Area?**  
  Aislar los datos crudos en `data/raw/` permite auditar el dato original ante cualquier duda y permite volver a procesar el dataset sin depender de descargas reiteradas.
- **¿Por qué prevenir duplicados?**  
  En entornos reales, los procesos automáticos pueden ejecutarse periódicamente o reintentarse tras una caída. La idempotencia asegura que volver a correr el script no infle las métricas ni corrompa la base de datos.
