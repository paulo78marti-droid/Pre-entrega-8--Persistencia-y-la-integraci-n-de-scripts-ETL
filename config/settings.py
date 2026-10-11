import os
from pathlib import Path
from dotenv import load_dotenv

# Ruta raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde el archivo .env si existe
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# Configuración de la API Open-Meteo
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.open-meteo.com/v1/forecast")
CITY_NAME = os.getenv("CITY_NAME", "Buenos Aires")
LATITUDE = float(os.getenv("LATITUDE", "-34.61"))
LONGITUDE = float(os.getenv("LONGITUDE", "-58.38"))
TIMEZONE = os.getenv("TIMEZONE", "America/Argentina/Buenos_Aires")

# Resiliencia HTTP
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
RETRY_BACKOFF_FACTOR = int(os.getenv("RETRY_BACKOFF_FACTOR", "2"))

# Rutas de datos
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Base de datos SQLite y SQLAlchemy 2.0
DB_FILE = DATA_DIR / "weather_analytics.db"
DEFAULT_DB_URL = f"sqlite:///{DB_FILE.as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
