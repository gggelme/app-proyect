from database.connection import get_connection
from models.habitacion import Habitacion

def guardar_habitacion(hab: Habitacion):
    conn = get_connection()
    if not conn: return None
    
    try:
        cur = conn.cursor()
        query = "INSERT INTO HABITACION (nombre, capacidad) VALUES (%s, %s) RETURNING id;"
        cur.execute(query, (hab.nombre, hab.capacidad))
        
        habitacion_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        return habitacion_id
    except Exception as e:
        print(f"❌ Error al guardar habitación: {e}")
        return None

def obtener_todas_habitaciones():
    conn = get_connection()
    habitaciones = []
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, capacidad FROM HABITACION ORDER BY nombre;")
        for row in cur.fetchall():
            habitaciones.append(Habitacion(id=row[0], nombre=row[1], capacidad=row[2]))
        cur.close()
        conn.close()
    return habitaciones