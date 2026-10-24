"""
Modulo de Extraccion (ETL)
Curso: Data Science II - Coderhouse

Descarga el dataset de Calidad del Aire desde Kaggle mediante la libreria kagglehub
y almacena una copia en la carpeta de datos crudos (patron Staging Area).
"""
import shutil
from pathlib import Path
import pandas as pd
from config import settings


def extract_air_quality_data():
    """
    Descarga el dataset 'srisyra02/air-quality-dataset' usando kagglehub.
    Guarda una copia en 'data/raw/air_quality_dataset.csv' (Staging Area).
    Si ocurre un problema de red o conexion, utiliza la copia local de respaldo si existe.
    
    Retorna:
        pd.DataFrame: DataFrame con los datos crudos extraidos.
    """
    print(f"[EXTRACT] Conectando con Kaggle para descargar: '{settings.KAGGLE_DATASET}'...")
    
    raw_file = settings.RAW_CSV_PATH

    try:
        import kagglehub
        # Descargar la version mas reciente desde Kaggle
        download_path = kagglehub.dataset_download(settings.KAGGLE_DATASET)
        download_dir = Path(download_path)
        
        # Localizar el archivo CSV dentro de la carpeta descargada
        csv_files = list(download_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No se encontro ningun archivo .csv en la descarga de Kaggle: {download_path}")
        
        source_csv = csv_files[0]
        print(f"[EXTRACT] Archivo descargado en cache: {source_csv}")

        # Patron Staging Area: Copiamos el archivo crudo a nuestra carpeta local data/raw/
        settings.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_csv, raw_file)
        print(f"[EXTRACT] Copia guardada en Staging Area: {raw_file}")

    except Exception as error:
        print(f"[ALERTA] No se pudo descargar desde Kaggle: {error}")
        if raw_file.exists():
            print(f"[EXTRACT] Utilizando copia de respaldo existente en: {raw_file}")
        else:
            raise RuntimeError(
                f"No se pudo descargar el dataset y no existe respaldo local en '{raw_file}'."
            ) from error

    # Lectura del archivo CSV crudo con Pandas
    df_raw = pd.read_csv(raw_file)
    print(f"[EXTRACT] Extraccion completada con exito: {len(df_raw)} filas y {len(df_raw.columns)} columnas.")
    return df_raw
