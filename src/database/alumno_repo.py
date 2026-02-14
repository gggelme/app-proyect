from database.connection import get_connection
from models.persona import Alumno

def guardar_alumno(alumno: Alumno): 
    conn = get_connection()
    if not conn: return None
    
    try:
        cur = conn.cursor()
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
        if conn: conn.rollback()
        print(f"❌ Error al guardar alumno: {e}")
        return None