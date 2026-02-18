from database.connection import get_connection
from models.persona import Profesor


class ErrorGuardarProfesor(Exception):
    """Excepción personalizada para errores al guardar profesor"""
    pass


def guardar_profesor(profe: Profesor):
    conn = get_connection()
    if not conn:
        raise ErrorGuardarProfesor("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar si el DNI ya existe
        cur.execute("SELECT id FROM PERSONA WHERE dni = %s", (profe.dni,))
        if cur.fetchone():
            raise ErrorGuardarProfesor(f"Ya existe una persona con DNI {profe.dni}")
        
        # 1. Insertar en la tabla PERSONA
        query_persona = """
            INSERT INTO PERSONA (dni, nombre_apellido, fecha_nac, domicilio, telefono, fecha_ingreso)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query_persona, (
            profe.dni, profe.nombre_apellido, profe.fecha_nac, 
            profe.domicilio, profe.telefono, profe.fecha_ingreso
        ))
        
        persona_id = cur.fetchone()[0]
        
        # 2. Insertar en la tabla PROFESOR
        query_profe = """
            INSERT INTO PROFESOR (id_persona, alias_mp)
            VALUES (%s, %s);
        """
        cur.execute(query_profe, (persona_id, profe.alias_mp))
        
        conn.commit()
        cur.close()
        conn.close()
        return persona_id

    except Exception as e:
        conn.rollback()
        if "duplicate key" in str(e).lower():
            raise ErrorGuardarProfesor(f"Ya existe un profesor con esos datos: {str(e)}")
        elif "not null" in str(e).lower():
            raise ErrorGuardarProfesor(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarProfesor(f"Error en la base de datos: {str(e)}")