from database.connection import get_connection
from models.clase import Clase


def guardar_clase(clase: Clase):
    conn = get_connection()
    if not conn: return None
    
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO CLASE (nombre_materia, id_profesor, id_habitacion, dia_semana, hora_inicio, hora_fin)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query, (
            clase.nombre_materia, # <--- Enviamos el nombre
            clase.id_profesor, 
            clase.id_habitacion, 
            clase.dia_semana, 
            clase.hora_inicio, 
            clase.hora_fin
        ))
        
        clase_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return clase_id
    except Exception as e:
        if conn: conn.rollback()
        print(f"❌ Error en clase_repo: {e}")
        return None