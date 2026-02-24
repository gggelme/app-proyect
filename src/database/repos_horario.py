# src/database/repos_horario.py
from database.connection import get_connection
from models.horario import Horario
from datetime import time

class ErrorGuardarHorario(Exception):
    """Excepción personalizada para errores al guardar horario"""
    pass

def guardar_horario(horario: Horario) -> int:
    """
    Guarda un nuevo horario en la base de datos.
    Retorna el ID generado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarHorario("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Insertar el horario
        query = """
            INSERT INTO horario (dia, hora_init, hora_fin)
            VALUES (%s, %s, %s) RETURNING id;
        """
        cur.execute(query, (
            horario.dia,
            horario.hora_init,
            horario.hora_fin
        ))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Horario guardado correctamente con ID: {id_generado}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "duplicate key" in str(e).lower() or "ak_dia_hora" in str(e):
            raise ErrorGuardarHorario(f"Ya existe un horario para {horario.dia} a las {horario.hora_init}")
        elif "not null" in str(e).lower():
            raise ErrorGuardarHorario(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarHorario(f"Error en la base de datos: {str(e)}")
        


# En repos_horario.py
def obtener_todos_horarios():
    """Obtiene todos los horarios disponibles"""
    conn = get_connection()
    horarios = []
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, dia, hora_init, hora_fin FROM horario ORDER BY dia, hora_init")
        
        for row in cur.fetchall():
            horarios.append({
                'id': row[0],
                'dia': row[1],
                'hora_init': str(row[2]),
                'hora_fin': str(row[3])
            })
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error obteniendo horarios: {e}")
    
    return horarios

