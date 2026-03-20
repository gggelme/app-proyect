# src/database/repos_horario.py
from database.connection import get_connection
from models.horario import Horario # Asegurate de quitar hora_fin también en el modelo Horario
from datetime import time

class ErrorGuardarHorario(Exception):
    """Excepción personalizada para errores al guardar horario"""
    pass

def guardar_horario(horario: Horario) -> int:
    """
    Guarda un nuevo horario en la base de datos (solo día y hora_init).
    Retorna el ID generado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarHorario("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Insertar el horario - SIN hora_fin
        query = """
            INSERT INTO horario (dia, hora_init)
            VALUES (%s, %s) RETURNING id;
        """
        cur.execute(query, (
            horario.dia,
            horario.hora_init
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
        else:
            raise ErrorGuardarHorario(f"Error en la base de datos: {str(e)}")

def obtener_todos_horarios():
    """Obtiene todos los horarios disponibles"""
    conn = get_connection()
    horarios = []
    
    try:
        cur = conn.cursor()
        # Quitamos hora_fin del SELECT
        cur.execute("SELECT id, dia, hora_init FROM horario ORDER BY dia, hora_init")
        
        for row in cur.fetchall():
            horarios.append({
                'id': row[0],
                'dia': row[1],
                'hora_init': str(row[2])
            })
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error obteniendo horarios: {e}")
    
    return horarios

# back/src/database/repos_horario.py

def obtener_horario_por_dia_y_hora(dia: str, hora: time) -> int:
    """
    Busca un horario existente por día y hora.
    Retorna el ID si existe, None si no.
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        query = """
            SELECT id FROM horario 
            WHERE dia = %s AND hora_init = %s
        """
        cur.execute(query, (dia, hora))
        
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return result[0] if result else None
        
    except Exception as e:
        print(f"Error al buscar horario: {e}")
        if conn:
            conn.close()
        return None