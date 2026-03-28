# database/repos_clase_edicion.py
from database.connection import get_connection
from typing import Dict, List, Optional

class ErrorActualizarClase(Exception):
    """Excepción para errores al actualizar clase"""
    pass

class ErrorEliminarClase(Exception):
    """Excepción para errores al eliminar clase"""
    pass

def obtener_todas_clases_completas() -> List[Dict]:
    """
    Obtiene todas las clases con su información completa
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                c.id,
                c.nombre_clase,
                c.duracion,
                pr.id as profesor_id,
                p.nomb_apel as profesor_nombre,
                COUNT(DISTINCT ac.id) as cantidad_inscripciones
            FROM clase c
            JOIN profesor pr ON c.id_profesor = pr.id
            JOIN persona p ON pr.id_persona = p.id
            LEFT JOIN alumno_clase ac ON c.id = ac.id_clase
            GROUP BY c.id, c.nombre_clase, c.duracion, pr.id, p.nomb_apel
            ORDER BY c.nombre_clase
        """
        cur.execute(query)
        
        clases = []
        for row in cur.fetchall():
            clases.append({
                'id': row[0],
                'nombre_clase': row[1],
                'duracion': row[2],
                'profesor_id': row[3],
                'profesor_nombre': row[4],
                'cantidad_inscripciones': row[5]
            })
        
        cur.close()
        conn.close()
        return clases
        
    except Exception as e:
        print(f"❌ Error al obtener clases completas: {e}")
        if conn:
            conn.close()
        return []

def actualizar_clase(id_clase: int, nombre_clase: Optional[str] = None, duracion: Optional[int] = None) -> bool:
    """
    Actualiza una clase existente.
    Retorna True si se actualizó correctamente.
    """
    conn = get_connection()
    if not conn:
        raise ErrorActualizarClase("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Construir la consulta dinámicamente según los campos proporcionados
        updates = []
        params = []
        
        if nombre_clase is not None:
            updates.append("nombre_clase = %s")
            params.append(nombre_clase)
        
        if duracion is not None:
            updates.append("duracion = %s")
            params.append(duracion)
        
        if not updates:
            return True  # No hay nada que actualizar
        
        params.append(id_clase)
        query = f"""
            UPDATE clase 
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id
        """
        
        cur.execute(query, params)
        resultado = cur.fetchone()
        
        if resultado:
            conn.commit()
            print(f"✅ Clase {id_clase} actualizada correctamente")
            cur.close()
            conn.close()
            return True
        else:
            raise ErrorActualizarClase(f"No existe una clase con ID {id_clase}")
            
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise ErrorActualizarClase(f"Error al actualizar clase: {str(e)}")

def eliminar_clase(id_clase: int) -> Dict:
    """
    Elimina una clase y todas sus inscripciones asociadas.
    Retorna un diccionario con el resultado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorEliminarClase("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que la clase existe
        cur.execute("SELECT nombre_clase FROM clase WHERE id = %s", (id_clase,))
        clase = cur.fetchone()
        if not clase:
            raise ErrorEliminarClase(f"No existe una clase con ID {id_clase}")
        
        nombre_clase = clase[0]
        
        # Contar inscripciones antes de eliminar
        cur.execute("SELECT COUNT(*) FROM alumno_clase WHERE id_clase = %s", (id_clase,))
        cantidad_inscripciones = cur.fetchone()[0]
        
        # Eliminar todas las inscripciones asociadas en alumno_clase
        cur.execute("DELETE FROM alumno_clase WHERE id_clase = %s", (id_clase,))
        inscripciones_eliminadas = cur.rowcount
        
        # Eliminar la clase
        cur.execute("DELETE FROM clase WHERE id = %s", (id_clase,))
        
        conn.commit()
        
        resultado = {
            'success': True,
            'message': f'Clase "{nombre_clase}" eliminada correctamente',
            'inscripciones_eliminadas': inscripciones_eliminadas,
            'total_afectado': inscripciones_eliminadas + 1
        }
        
        print(f"✅ Clase {id_clase} eliminada con {inscripciones_eliminadas} inscripciones")
        
        cur.close()
        conn.close()
        return resultado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise ErrorEliminarClase(f"Error al eliminar clase: {str(e)}")