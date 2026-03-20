# src/database/repos_horario_clase.py
from database.connection import get_connection

class ErrorGuardarHorarioClase(Exception):
    """Excepción personalizada para errores al guardar horario-clase"""
    pass

def guardar_horario_clase(id_horario: int, id_clase: int, aula: str = None) -> int:
    """
    Asigna un horario a una clase.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarHorarioClase("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar existencia del horario
        cur.execute("SELECT id FROM horario WHERE id = %s", (id_horario,))
        if not cur.fetchone():
            raise ErrorGuardarHorarioClase(f"No existe un horario con ID {id_horario}")
        
        # Verificar existencia de la clase
        cur.execute("SELECT id FROM clase WHERE id = %s", (id_clase,))
        if not cur.fetchone():
            raise ErrorGuardarHorarioClase(f"No existe una clase con ID {id_clase}")
        
        # El resto del código se mantiene igual ya que la tabla horario_clase no cambió
        query = """
            INSERT INTO horario_clase (id_horario, id_clase, aula)
            VALUES (%s, %s, %s) RETURNING id;
        """
        cur.execute(query, (id_horario, id_clase, aula))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Horario ID {id_horario} asignado a Clase ID {id_clase}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise ErrorGuardarHorarioClase(f"Error en la base de datos: {str(e)}")