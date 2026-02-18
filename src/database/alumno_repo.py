# database/repositorio_alumno.py
from database.connection import get_connection
from models.persona import Alumno

class ErrorGuardarAlumno(Exception):
    """Excepción personalizada para errores al guardar alumno"""
    pass

def guardar_alumno(alumno: Alumno): 
    conn = get_connection()
    if not conn:
        raise ErrorGuardarAlumno("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar si el DNI ya existe
        cur.execute("SELECT id FROM PERSONA WHERE dni = %s", (alumno.dni,))
        if cur.fetchone():
            raise ErrorGuardarAlumno(f"Ya existe una persona con DNI {alumno.dni}")
        
        # 1. Insertar en PERSONA
        query_persona = """
            INSERT INTO PERSONA (dni, nombre_apellido, fecha_nac, domicilio, telefono, fecha_ingreso)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query_persona, (
            alumno.dni, alumno.nombre_apellido, alumno.fecha_nac, 
            alumno.domicilio, alumno.telefono, alumno.fecha_ingreso
        ))
        persona_id = cur.fetchone()[0]
        
        # 2. Insertar en ALUMNO
        query_alumno = "INSERT INTO ALUMNO (id_persona) VALUES (%s);"
        cur.execute(query_alumno, (persona_id,))

        conn.commit()
        cur.close()
        conn.close()
        return persona_id
        
    except Exception as e:
        if conn: 
            conn.rollback()
            conn.close()
        
        if "duplicate key" in str(e).lower():
            raise ErrorGuardarAlumno(f"Ya existe un alumno con esos datos: {str(e)}")
        elif "not null" in str(e).lower():
            raise ErrorGuardarAlumno(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarAlumno(f"Error en la base de datos: {str(e)}")