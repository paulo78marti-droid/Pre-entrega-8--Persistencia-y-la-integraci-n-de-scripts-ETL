import os
from pathlib import Path
from dotenv import load_dotenv

# Ruta principal del proyecto (directorio raíz)
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables del archivo .env si está disponible
load_dotenv(dotenv_path=BASE_DIR / ".env")

# 1. Configuración de la API del Clima (Open-Meteo)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.open-meteo.com/v1/forecast")
CITY_NAME = os.getenv("CITY_NAME", "Buenos Aires")
LATITUDE = float(os.getenv("LATITUDE", "-34.61"))
LONGITUDE = float(os.getenv("LONGITUDE", "-58.38"))
TIMEZONE = os.getenv("TIMEZONE", "America/Argentina/Buenos_Aires")

# 2. Rutas de carpetas del proyecto
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

# Crear carpetas si no existen
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# 3. Base de Datos SQLite (usando SQLAlchemy)
DB_FILE = DATA_DIR / "weather_analytics.db"
DEFAULT_DB_URL = f"sqlite:///{DB_FILE.as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
