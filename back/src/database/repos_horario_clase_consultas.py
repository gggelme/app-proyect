from database.connection import get_connection

class ErrorConsultaHorarios(Exception):
    pass


def obtener_clases_por_dia_y_hora(dia: str, hora: str):

    conn = get_connection()
    if not conn:
        raise ErrorConsultaHorarios("No se pudo conectar a la base de datos")

    try:
        cur = conn.cursor()

        query = """
            SELECT 
                hc.aula,
                prof.nomb_apel as profesor,
                json_agg(p.nomb_apel) as alumnos,
                COUNT(p.nomb_apel) as cantidad_alumnos
            FROM horario_clase hc
            INNER JOIN horario h ON hc.id_horario = h.id
            INNER JOIN clase c ON hc.id_clase = c.id
            INNER JOIN profesor pr ON c.id_profesor = pr.id
            INNER JOIN persona prof ON pr.id_persona = prof.id
            INNER JOIN alumno_clase ac ON ac.id_clase = c.id
            INNER JOIN alumno a ON ac.id_alumno = a.id
            INNER JOIN persona p ON a.id_persona = p.id
            WHERE h.dia = %s
              AND TO_CHAR(h.hora_init, 'HH24:MI') = %s
            GROUP BY hc.aula, prof.nomb_apel
            ORDER BY hc.aula;
        """

        cur.execute(query, (dia, hora))
        rows = cur.fetchall()

        resultado = []

        for aula, profesor, alumnos, cantidad in rows:
            resultado.append({
                "aula": aula,
                "profesor": profesor,
                "alumnos": alumnos if alumnos else [],
                "cantidad_alumnos": cantidad
            })

        cur.close()
        conn.close()

        return resultado

    except Exception as e:
        if conn:
            conn.close()
        raise ErrorConsultaHorarios(str(e))