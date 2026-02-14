from database.connection import get_connection
from models.persona import Profesor

def guardar_profesor(profe: Profesor):
    conn = get_connection()
    if not conn: return None
    
    try:
        cur = conn.cursor()
        
        # 1. Insertar en la tabla PERSONA
        query_persona = """
            INSERT INTO PERSONA (dni, nombre_apellido, fecha_nac, domicilio, telefono, fecha_ingreso)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query_persona, (
            profe.dni, profe.nombre_apellido, profe.fecha_nac, 
            profe.domicilio, profe.telefono, profe.fecha_ingreso
        ))
        
        # Obtenemos el ID generado para la persona
        persona_id = cur.fetchone()[0]
        
        # 2. Insertar en la tabla PROFESOR usando ese mismo ID
        query_profe = """
            INSERT INTO PROFESOR (id_persona, alias_mp)
            VALUES (%s, %s);
        """
        cur.execute(query_profe, (persona_id, profe.alias_mp))
        
        # Confirmamos los cambios (COMMIT)
        conn.commit()
        cur.close()
        conn.close()
        return persona_id

    except Exception as e:
        conn.rollback() # Si algo falla, deshacemos todo
        print(f"❌ Error al guardar profesor: {e}")
        return None