import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Configuración de rutas para cargar el entorno
base_dir = Path(__file__).resolve().parent.parent.parent
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)

def get_connection():
    """
    Establece y retorna una conexión con PostgreSQL. 
    Retorna None si la conexión falla.
    """
    try:
        return psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
    except Exception:
        # En producción, podrías loguear esto en un archivo, 
        # por ahora simplemente evitamos que el programa explote.
        return None