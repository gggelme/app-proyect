# src/database/repos_clase.py
from typing import Dict, List, Optional

from database.connection import get_connection
from models.clase import Clase

class ErrorGuardarClase(Exception):
    """Excepción personalizada para errores al guardar clase"""
    pass

def guardar_clase(clase: Clase) -> int:
    """
    Guarda una nueva clase en la base de datos.
    Retorna el ID generado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarClase("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que el profesor existe
        cur.execute("SELECT id FROM profesor WHERE id = %s", (clase.id_profesor,))
        if not cur.fetchone():
            raise ErrorGuardarClase(f"No existe un profesor con ID {clase.id_profesor}")
        
        # Insertar la clase (incluyendo duracion)
        query = """
            INSERT INTO clase (nombre_clase, id_profesor, duracion)
            VALUES (%s, %s, %s) RETURNING id;
        """
        cur.execute(query, (
            clase.nombre_clase,
            clase.id_profesor,
            clase.duracion  # Nueva columna
        ))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Clase guardada correctamente con ID: {id_generado}")
        print(f"   Nombre: {clase.nombre_clase}")
        print(f"   Profesor ID: {clase.id_profesor}")
        if clase.duracion:
            print(f"   Duración: {clase.duracion} minutos")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "foreign key" in str(e).lower():
            raise ErrorGuardarClase(f"El profesor con ID {clase.id_profesor} no existe")
        elif "not null" in str(e).lower():
            raise ErrorGuardarClase(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarClase(f"Error en la base de datos: {str(e)}")

# Si tenés otras funciones en el repositorio (como obtener_todas_clases, etc.),
# actualizalas también para incluir el campo duracion


# En repos_clase.py (agregar)
def obtener_todas_clases():
    """Obtiene todas las clases sin horarios"""
    conn = get_connection()
    clases = []
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                c.id,
                c.nombre_clase,
                p.nomb_apel as profesor_nombre
            FROM clase c
            JOIN profesor pr ON c.id_profesor = pr.id
            JOIN persona p ON pr.id_persona = p.id
            ORDER BY c.nombre_clase
        """
        cur.execute(query)
        
        for row in cur.fetchall():
            clases.append({
                'id': row[0],
                'nombre_clase': row[1],
                'profesor_nombre': row[2]
            })
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error obteniendo clases: {e}")
    
    return clases