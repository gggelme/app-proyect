# src/database/connection.py
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Configuración de rutas para cargar el entorno
base_dir = Path(__file__).resolve().parent.parent.parent
env_path = base_dir / '.env'
print(f"Buscando .env en: {env_path}")  # Mensaje de depuración

if env_path.exists():
    print("✅ Archivo .env encontrado")
    load_dotenv(dotenv_path=env_path)
else:
    print(f"❌ Archivo .env no encontrado en: {env_path}")

def get_connection():
    """
    Establece y retorna una conexión con PostgreSQL. 
    Retorna None si la conexión falla.
    """
    try:
        print("Intentando conectar a PostgreSQL...")
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
        print("✅ Conexión establecida")
        return conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None