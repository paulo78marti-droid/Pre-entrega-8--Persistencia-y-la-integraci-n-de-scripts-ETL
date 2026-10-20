# Pipeline ETL de Datos Meteorológicos con SQLite y SQLAlchemy

**Curso:** Data Science II — Coderhouse  
**Entrega:** Pre-entrega — Persistencia y la integración de scripts ETL (Módulo 9, pág. 187)  
**Estudiante:** Paulo Martin  

---

## 1. Descripción del Proyecto

El objetivo de esta pre-entrega es implementar un pipeline de datos automatizado que realice las tres etapas de un proceso **ETL (Extract, Transform, Load)**:

1. **Extracción (Extract):** Consume datos meteorológicos en tiempo real desde la API pública y gratuita de [Open-Meteo](https://open-meteo.com/) para la ciudad de Buenos Aires.
2. **Transformación (Transform):** Utiliza **Pandas** para limpiar valores nulos, convertir tipos de datos (fechas a `datetime`), generar nuevas variables útiles (*feature engineering*) y calcular un resumen analítico diario.
3. **Carga y Persistencia (Load):** Almacena la información de forma estructurada en una base de datos local **SQLite** utilizando el ORM **SQLAlchemy 2.0**, implementando una lógica para **evitar duplicados** si el script se ejecuta varias veces.

---

## 2. Estructura del Proyecto

El repositorio está organizado de forma modular para separar cada paso del proceso:

```text
Pre-entrega 8- Persistencia y la integración de scripts ETL/
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuración del proyecto (rutas, coordenadas y BD)
│
├── data/
│   ├── raw/                 # Carpeta para guardar los datos crudos de la API (Staging)
│   │   └── .gitkeep
│   └── weather_analytics.db # Base de datos local SQLite (se crea al ejecutar)
│
├── sql/
│   └── create_tables.sql    # Script DDL en SQL para la creación de tablas e índices
│
├── src/
│   ├── __init__.py
│   ├── models.py            # Modelos de tablas con SQLAlchemy 2.0
│   ├── extract.py           # Extracción desde la API Open-Meteo
│   ├── transform.py         # Limpieza, conversión de fechas y resumen con Pandas
│   └── load.py              # Carga en SQLite y lógica para no duplicar datos
│
├── main.py                  # Script principal que ejecuta el pipeline completo
├── verify_persistence.py    # Script para consultar y verificar los datos con SQL
├── requirements.txt         # Librerías necesarias para ejecutar el proyecto
├── .env.example             # Ejemplo de variables de configuración opcionales
├── .gitignore               # Archivos excluidos del repositorio (BD local y temporales)
└── README.md                # Documentación del proyecto
```

---

## 3. Requisitos del Entorno

Para ejecutar este proyecto necesitas:
- **Python 3.10 o superior** instalado.
- Las librerías indicadas en `requirements.txt`:
  - `requests` (para consultar la API)
  - `pandas` (para la limpieza y transformación de datos)
  - `sqlalchemy` (para interactuar y persistir en la base de datos)
  - `python-dotenv` (para leer variables de entorno si se configuran)

---

## 4. Pasos para Ejecutar

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/paulo78marti-droid/Pre-entrega-8--Persistencia-y-la-integraci-n-de-scripts-ETL.git
cd "Pre-entrega-8--Persistencia-y-la-integraci-n-de-scripts-ETL"
```

### Paso 2: Crear y activar un entorno virtual (recomendado)

**En Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**En Linux / Mac:**
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

**¿Qué verás en la consola?**
1. La conexión a SQLite y la verificación/creación de las tablas.
2. La descarga de datos de la API del clima y su guardado en `data/raw/weather_raw_latest.json`.
3. La limpieza y el cálculo del resumen diario con Pandas.
4. La inserción de las filas en la base de datos `data/weather_analytics.db`.
5. Un resumen con el total de registros almacenados.

### Paso 5: Probar la prevención de duplicados
Si vuelves a ejecutar:
```bash
python main.py
```
El script detectará automáticamente que esos datos ya existen en SQLite y no insertará filas duplicadas.

### Paso 6: Consultar la base de datos con SQL
Para auditar la base de datos y ver los datos guardados:
```bash
python verify_persistence.py
```
Este script ejecuta consultas SQL analíticas sobre la base de datos:
- Top 5 horas con mayor temperatura registrada.
- Días con registro de lluvias acumuladas.
- Horas acumuladas según la intensidad del viento.

---

## 5. Explicación del Flujo ETL

### 1. Extracción (`src/extract.py`)
- Realiza una petición `GET` con `requests` a la API de Open-Meteo pidiendo temperatura, humedad, lluvia y viento.
- Guarda una copia cruda del JSON en `data/raw/weather_raw_latest.json`. Esto sirve como **área de transición (staging)** para tener el respaldo exacto de lo recibido.
- Incluye control de excepciones: si no hay conexión a internet y existe un archivo previo en `data/raw/`, lo reutiliza para no cortar el flujo.

### 2. Transformación (`src/transform.py`)
- Pasa los datos JSON a un `DataFrame` de Pandas.
- Convierte la columna de fecha a tipo `datetime`.
- **Tratamiento de nulos:**
  - Descarta filas que no tengan fecha o temperatura (datos indispensables).
  - Rellena valores nulos de lluvia con `0.0 mm`.
  - Rellena valores nulos de humedad con la mediana de la columna.
- **Nuevas variables:**
  - `wind_category`: Clasifica el viento en *Leve*, *Moderado* o *Fuerte*.
  - `is_rainy`: Booleano (`True`/`False`) que indica si hubo precipitación.
- **Resumen diario:** Agrupa por fecha y calcula la temperatura mínima, máxima, promedio y la lluvia total de cada día.

### 3. Carga y Persistencia (`src/load.py` y `src/models.py`)
- Conecta con SQLite mediante `create_engine` de SQLAlchemy.
- Crea las tablas a partir de los modelos de SQLAlchemy 2.0.
- Guarda los datos usando `to_sql(..., if_exists="append")`.
- **Control de duplicados:** Antes de insertar, consulta los registros que ya existen en la base y únicamente inserta las filas nuevas.

---

## 6. Esquema de la Base de Datos (DDL)

El diseño cuenta con dos tablas en SQLite:

### Tabla: `weather_hourly` (Mediciones por hora)
| Campo | Tipo SQL | Descripción |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Identificador autoincremental |
| `city` | `VARCHAR(50)` | Nombre de la ciudad |
| `timestamp` | `DATETIME` | Fecha y hora de la medición |
| `temperature_c` | `REAL` | Temperatura en °C |
| `humidity_pct` | `REAL` | Porcentaje de humedad |
| `precipitation_mm` | `REAL` | Milímetros de lluvia |
| `wind_speed_kmh` | `REAL` | Velocidad del viento en km/h |
| `wind_category` | `VARCHAR(30)` | Categoría del viento (Leve, Moderado, Fuerte) |
| `is_rainy` | `BOOLEAN` | Si hubo lluvia (True/False) |
| `ingested_at` | `DATETIME` | Fecha y hora de carga |

### Tabla: `weather_daily_summary` (Resumen por día)
| Campo | Tipo SQL | Descripción |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY` | Identificador autoincremental |
| `city` | `VARCHAR(50)` | Nombre de la ciudad |
| `date` | `DATE` | Fecha del día |
| `temp_min_c` | `REAL` | Temperatura mínima del día |
| `temp_max_c` | `REAL` | Temperatura máxima del día |
| `temp_avg_c` | `REAL` | Temperatura promedio del día |
| `total_precipitation_mm` | `REAL` | Lluvia acumulada en el día |
| `avg_wind_speed_kmh` | `REAL` | Velocidad media del viento |
| `rainy_hours_count` | `INTEGER` | Cantidad de horas con lluvia |
| `ingested_at` | `DATETIME` | Fecha y hora de carga |

El script SQL nativo con las sentencias `CREATE TABLE` e índices se encuentra en [`sql/create_tables.sql`](sql/create_tables.sql).

---

## 7. Justificación de Decisiones Técnicas

- **¿Por qué SQLite?**  
  Porque es una base de datos relacional que funciona en un único archivo local (`.db`), sin necesidad de instalar ni configurar servidores externos, facilitando que cualquiera pueda clonar y ejecutar el proyecto sin problemas.

- **¿Por qué SQLAlchemy?**  
  Porque es la librería estándar en Python para interactuar con bases de datos relacionales, permitiendo crear tablas mediante código Python limpio y ejecutar consultas SQL de forma segura.

- **¿Por qué guardar una copia cruda (Staging)?**  
  Guardar el JSON original en `data/raw/` permite auditar los datos de origen tal como llegaron y garantiza poder volver a procesarlos ante cualquier cambio o fallo de conexión.
