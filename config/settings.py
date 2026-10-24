import os
from pathlib import Path
from dotenv import load_dotenv

# Ruta principal del proyecto (directorio raiz)
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables del archivo .env si esta disponible
load_dotenv(dotenv_path=BASE_DIR / ".env")

# 1. Configuracion del Dataset en Kaggle
KAGGLE_DATASET = os.getenv("KAGGLE_DATASET", "srisyra02/air-quality-dataset")
CSV_FILENAME = "air_quality_dataset.csv"

# 2. Rutas de carpetas del proyecto
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

# Crear carpetas si no existen
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Ruta del archivo CSV en el area de transicion (Staging Area)
RAW_CSV_PATH = RAW_DATA_DIR / CSV_FILENAME

# 3. Base de Datos SQLite (usando SQLAlchemy)
DB_FILE = DATA_DIR / "air_quality.db"
DEFAULT_DB_URL = f"sqlite:///{DB_FILE.as_posix()}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
