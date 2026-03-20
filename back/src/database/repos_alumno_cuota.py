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
    print(f"   🔍 [repos_alumno_cuota] guardar_alumno_cuota({id_alumno}, {id_cuota})")
    
    conn = get_connection()
    if not conn:
        print(f"   ❌ No se pudo conectar a la base de datos")
        raise ErrorGuardarAlumnoCuota("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que el alumno existe
        print(f"   Verificando existencia del alumno {id_alumno}...")
        cur.execute("SELECT id FROM alumno WHERE id = %s", (id_alumno,))
        alumno_exists = cur.fetchone()
        if not alumno_exists:
            print(f"   ❌ No existe un alumno con ID {id_alumno}")
            raise ErrorGuardarAlumnoCuota(f"No existe un alumno con ID {id_alumno}")
        print(f"   ✅ Alumno {id_alumno} existe")
        
        # Verificar que la cuota existe
        print(f"   Verificando existencia de la cuota {id_cuota}...")
        cur.execute("SELECT id, nombre FROM cuota WHERE id = %s", (id_cuota,))
        cuota_data = cur.fetchone()
        if not cuota_data:
            print(f"   ❌ No existe una cuota con ID {id_cuota}")
            raise ErrorGuardarAlumnoCuota(f"No existe una cuota con ID {id_cuota}")
        print(f"   ✅ Cuota {id_cuota} existe: {cuota_data[1]}")
        
        # Insertar la relación
        print(f"   Insertando relación en alumno_cuota...")
        query = """
            INSERT INTO alumno_cuota (id_alumno, id_cuota)
            VALUES (%s, %s) RETURNING id;
        """
        cur.execute(query, (id_alumno, id_cuota))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"   ✅ Relación alumno-cuota guardada correctamente con ID: {id_generado}")
        print(f"   Alumno ID: {id_alumno} - Cuota ID: {id_cuota}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        print(f"   ❌ Error en guardar_alumno_cuota: {e}")
        
        if "duplicate key" in str(e).lower() or "ak_alumno_cuota" in str(e):
            raise ErrorGuardarAlumnoCuota(f"El alumno {id_alumno} ya tiene asignada la cuota {id_cuota}")
        elif "foreign key" in str(e).lower():
            raise ErrorGuardarAlumnoCuota(f"Error de referencia: {str(e)}")
        else:
            raise ErrorGuardarAlumnoCuota(f"Error en la base de datos: {str(e)}")