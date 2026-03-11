# src/database/repos_horario_clase.py
from database.connection import get_connection

class ErrorGuardarHorarioClase(Exception):
    """Excepción personalizada para errores al guardar horario-clase"""
    pass

def guardar_horario_clase(id_horario: int, id_clase: int, aula: str = None) -> int:
    """
    Asigna un horario a una clase.
    Retorna el ID de la relación creada.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarHorarioClase("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que el horario existe
        cur.execute("SELECT id FROM horario WHERE id = %s", (id_horario,))
        if not cur.fetchone():
            raise ErrorGuardarHorarioClase(f"No existe un horario con ID {id_horario}")
        
        # Verificar que la clase existe
        cur.execute("SELECT id FROM clase WHERE id = %s", (id_clase,))
        if not cur.fetchone():
            raise ErrorGuardarHorarioClase(f"No existe una clase con ID {id_clase}")
        
        # Insertar la relación
        query = """
            INSERT INTO horario_clase (id_horario, id_clase, aula)
            VALUES (%s, %s, %s) RETURNING id;
        """
        cur.execute(query, (id_horario, id_clase, aula))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Horario asignado a clase correctamente con ID: {id_generado}")
        print(f"   Horario ID: {id_horario} - Clase ID: {id_clase}")
        if aula:
            print(f"   Aula: {aula}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "duplicate key" in str(e).lower() or "ak_horario_clase" in str(e):
            raise ErrorGuardarHorarioClase(f"El horario {id_horario} ya está asignado a la clase {id_clase}")
        elif "foreign key" in str(e).lower():
            raise ErrorGuardarHorarioClase(f"Error de referencia: {str(e)}")
        else:
            raise ErrorGuardarHorarioClase(f"Error en la base de datos: {str(e)}")