# database/repositorio_habitacion.py
from database.connection import get_connection
from models.habitacion import Habitacion

class ErrorGuardarHabitacion(Exception):
    """Excepción personalizada para errores al guardar habitación"""
    pass

def guardar_habitacion(hab: Habitacion):
    conn = get_connection()
    if not conn:
        raise ErrorGuardarHabitacion("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar si ya existe una habitación con ese nombre
        cur.execute("SELECT id FROM HABITACION WHERE nombre = %s", (hab.nombre,))
        if cur.fetchone():
            raise ErrorGuardarHabitacion(f"Ya existe una habitación con el nombre '{hab.nombre}'")
        
        # Validar que la capacidad sea positiva
        if hab.capacidad <= 0:
            raise ErrorGuardarHabitacion("La capacidad debe ser un número positivo")
        
        query = "INSERT INTO HABITACION (nombre, capacidad) VALUES (%s, %s) RETURNING id;"
        cur.execute(query, (hab.nombre, hab.capacidad))
        
        habitacion_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        return habitacion_id
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            raise ErrorGuardarHabitacion(f"Ya existe una habitación con el nombre '{hab.nombre}'")
        else:
            raise ErrorGuardarHabitacion(f"Error en la base de datos: {str(e)}")

def obtener_todas_habitaciones():
    conn = get_connection()
    habitaciones = []
    if not conn:
        return habitaciones
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, capacidad FROM HABITACION ORDER BY nombre;")
        for row in cur.fetchall():
            habitaciones.append(Habitacion(id=row[0], nombre=row[1], capacidad=row[2]))
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al obtener habitaciones: {e}")
    return habitaciones