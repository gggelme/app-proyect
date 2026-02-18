# database/repositorio_instrumento.py
from database.connection import get_connection
from models.instrumento import Instrumento

class ErrorGuardarInstrumento(Exception):
    """Excepción personalizada para errores al guardar instrumento"""
    pass

def guardar_instrumento(instrumento: Instrumento):
    conn = get_connection()
    if not conn:
        raise ErrorGuardarInstrumento("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar si ya existe un instrumento con ese nombre
        cur.execute("SELECT id FROM INSTRUMENTO WHERE nombre = %s", (instrumento.nombre,))
        if cur.fetchone():
            raise ErrorGuardarInstrumento(f"Ya existe un instrumento con el nombre '{instrumento.nombre}'")
        
        # Insertar incluyendo precio_hora
        query = "INSERT INTO INSTRUMENTO (nombre, precio_hora) VALUES (%s, %s) RETURNING id;"
        cur.execute(query, (instrumento.nombre, instrumento.precio_hora))
        
        instrumento_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        return instrumento_id
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            raise ErrorGuardarInstrumento(f"Ya existe un instrumento con el nombre '{instrumento.nombre}'")
        else:
            raise ErrorGuardarInstrumento(f"Error en la base de datos: {str(e)}")

def obtener_todos_instrumentos():
    conn = get_connection()
    instrumentos = []
    if not conn:
        return instrumentos
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, precio_hora FROM INSTRUMENTO ORDER BY nombre;")
        for row in cur.fetchall():
            instrumentos.append(Instrumento(id=row[0], nombre=row[1], precio_hora=row[2]))
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al obtener instrumentos: {e}")
    return instrumentos