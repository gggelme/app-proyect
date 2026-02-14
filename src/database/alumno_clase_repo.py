from database.connection import get_connection

def inscribir_alumno_en_materia(id_alumno, id_clase):
    """
    Registra a un alumno en una clase/materia específica.
    Columnas: id_alumno, id_clase, fecha_inscripcion (automática).
    """
    conn = get_connection()
    if not conn: return False
    
    try:
        cur = conn.cursor()
        # Solo enviamos los dos IDs que existen en tu tabla
        query = """
            INSERT INTO ALUMNO_CLASE (id_alumno, id_clase)
            VALUES (%s, %s);
        """
        cur.execute(query, (id_alumno, id_clase))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        if conn: conn.rollback()
        print(f"❌ Error al inscribir alumno en la clase: {e}")
        return False

def obtener_alumnos_de_clase(id_clase):
    """
    Lista todos los alumnos anotados en una clase específica.
    """
    conn = get_connection()
    resultados = []
    if conn:
        cur = conn.cursor()
        query = """
            SELECT p.nombre_apellido, ac.fecha_inscripcion
            FROM ALUMNO_CLASE ac
            JOIN PERSONA p ON ac.id_alumno = p.id
            WHERE ac.id_clase = %s;
        """
        cur.execute(query, (id_clase,))
        resultados = cur.fetchall()
        cur.close()
        conn.close()
    return resultados