# src/database/repos_alumno_cuota.py
from database.connection import get_connection

class ErrorGuardarAlumnoCuota(Exception):
    """Excepción personalizada para errores al guardar alumno-cuota"""
    pass

def guardar_alumno_cuota(id_alumno: int, id_cuota: int) -> int:
    """
    Asocia un alumno con una cuota.
    Retorna el ID de la relación creada.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarAlumnoCuota("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que el alumno existe
        cur.execute("SELECT id FROM alumno WHERE id = %s", (id_alumno,))
        if not cur.fetchone():
            raise ErrorGuardarAlumnoCuota(f"No existe un alumno con ID {id_alumno}")
        
        # Verificar que la cuota existe
        cur.execute("SELECT id FROM cuota WHERE id = %s", (id_cuota,))
        if not cur.fetchone():
            raise ErrorGuardarAlumnoCuota(f"No existe una cuota con ID {id_cuota}")
        
        # Insertar la relación
        query = """
            INSERT INTO alumno_cuota (id_alumno, id_cuota)
            VALUES (%s, %s) RETURNING id;
        """
        cur.execute(query, (id_alumno, id_cuota))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Relación alumno-cuota guardada correctamente con ID: {id_generado}")
        print(f"   Alumno ID: {id_alumno} - Cuota ID: {id_cuota}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "duplicate key" in str(e).lower() or "ak_alumno_cuota" in str(e):
            raise ErrorGuardarAlumnoCuota(f"El alumno {id_alumno} ya tiene asignada la cuota {id_cuota}")
        elif "foreign key" in str(e).lower():
            raise ErrorGuardarAlumnoCuota(f"Error de referencia: {str(e)}")
        else:
            raise ErrorGuardarAlumnoCuota(f"Error en la base de datos: {str(e)}")