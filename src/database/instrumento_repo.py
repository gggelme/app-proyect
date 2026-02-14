from database.connection import get_connection
from models.instrumento import Instrumento

def guardar_instrumento(instrumento: Instrumento):
    conn = get_connection()
    if not conn: return None
    
    try:
        cur = conn.cursor()
        query = "INSERT INTO INSTRUMENTO (nombre) VALUES (%s) RETURNING id;"
        cur.execute(query, (instrumento.nombre,))
        
        instrumento_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        return instrumento_id
    except Exception as e:
        print(f"❌ Error al guardar instrumento: {e}")
        return None

def obtener_todos_instrumentos():
    conn = get_connection()
    instrumentos = []
    if conn:
        cur = conn.cursor()
        # Agregamos precio_hora al SELECT
        cur.execute("SELECT id, nombre, precio_hora FROM INSTRUMENTO ORDER BY nombre;")
        for row in cur.fetchall():
            # Pasamos los 3 argumentos al modelo
            instrumentos.append(Instrumento(id=row[0], nombre=row[1], precio_hora=row[2]))
        cur.close()
        conn.close()
    return instrumentos