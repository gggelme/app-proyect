# src/database/repos_alumno_clase.py
from database.connection import get_connection
from datetime import date
from typing import List, Dict

class ErrorGuardarAlumnoClase(Exception):
    """Excepción personalizada para errores al guardar alumno-clase"""
    pass

def guardar_alumno_clase(id_alumno: int, id_clase: int, fecha_inscripcion: date = None) -> int:
    """
    Inscribe un alumno en una clase.
    Si no se proporciona fecha, usa la fecha actual.
    Retorna el ID de la inscripción creada.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarAlumnoClase("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que el alumno existe
        cur.execute("SELECT id FROM alumno WHERE id = %s", (id_alumno,))
        if not cur.fetchone():
            raise ErrorGuardarAlumnoClase(f"No existe un alumno con ID {id_alumno}")
        
        # Verificar que la clase existe
        cur.execute("SELECT id FROM clase WHERE id = %s", (id_clase,))
        if not cur.fetchone():
            raise ErrorGuardarAlumnoClase(f"No existe una clase con ID {id_clase}")
        
        # Usar fecha actual si no se proporcionó
        if fecha_inscripcion is None:
            fecha_inscripcion = date.today()
        
        # Insertar la inscripción
        query = """
            INSERT INTO alumno_clase (id_alumno, id_clase, fecha_inscripcion)
            VALUES (%s, %s, %s) RETURNING id;
        """
        cur.execute(query, (id_alumno, id_clase, fecha_inscripcion))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Alumno inscrito en clase correctamente con ID: {id_generado}")
        print(f"   Alumno ID: {id_alumno} - Clase ID: {id_clase}")
        print(f"   Fecha inscripción: {fecha_inscripcion}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "duplicate key" in str(e).lower() or "ak_alumno_clase" in str(e):
            raise ErrorGuardarAlumnoClase(f"El alumno {id_alumno} ya está inscrito en la clase {id_clase}")
        elif "foreign key" in str(e).lower():
            raise ErrorGuardarAlumnoClase(f"Error de referencia: {str(e)}")
        else:
            raise ErrorGuardarAlumnoClase(f"Error en la base de datos: {str(e)}")


def obtener_alumnos_con_clases() -> List[Dict]:
    """
    Obtiene SOLO los alumnos que tienen al menos una clase
    Cada alumno viene con sus clases y cada clase con sus horarios y profesor
    """
    conn = get_connection()
    alumnos = []
    
    if not conn:
        return alumnos
    
    try:
        cur = conn.cursor()
        
        query = """
            SELECT DISTINCT
                p.id as persona_id,
                a.id as alumno_id,
                p.nomb_apel as nombre_alumno,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'clase_id', c.id,
                            'nombre_clase', c.nombre_clase,
                            'profesor_nombre', prof.nomb_apel,
                            'duracion', c.duracion,
                            'horarios', (
                                SELECT json_agg(
                                    json_build_object(
                                        'dia', h.dia,
                                        'hora', h.hora_init::text,
                                        'aula', hc.aula
                                    )
                                    ORDER BY 
                                        CASE h.dia
                                            WHEN 'LUNES' THEN 1
                                            WHEN 'MARTES' THEN 2
                                            WHEN 'MIERCOLES' THEN 3
                                            WHEN 'JUEVES' THEN 4
                                            WHEN 'VIERNES' THEN 5
                                            WHEN 'SABADO' THEN 6
                                            WHEN 'DOMINGO' THEN 7
                                        END,
                                        h.hora_init
                                )
                                FROM horario_clase hc
                                JOIN horario h ON hc.id_horario = h.id
                                WHERE hc.id_clase = c.id
                            )
                        )
                        ORDER BY c.nombre_clase
                    ) FILTER (WHERE c.id IS NOT NULL),
                    '[]'::json
                ) as clases
            FROM persona p
            JOIN alumno a ON p.id = a.id_persona
            JOIN alumno_clase ac ON a.id = ac.id_alumno
            JOIN clase c ON ac.id_clase = c.id
            JOIN persona prof ON c.id_profesor = prof.id
            GROUP BY p.id, a.id, p.nomb_apel
            ORDER BY p.nomb_apel
        """
        
        cur.execute(query)
        
        for row in cur.fetchall():
            alumno = {
                'id': row[1],  # alumno_id
                'nombre_alumno': row[2],
                'clases': row[3] if row[3] else []
            }
            alumnos.append(alumno)
        
        cur.close()
        conn.close()
        
        print(f"✅ Se obtuvieron {len(alumnos)} alumnos con clases")
        
    except Exception as e:
        print(f"❌ Error obteniendo alumnos con clases: {e}")
        import traceback
        traceback.print_exc()
    
    return alumnos