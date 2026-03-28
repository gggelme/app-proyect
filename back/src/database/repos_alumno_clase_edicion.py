# src/database/repos_alumno_clase_edicion.py
from database.connection import get_connection
from typing import List, Dict

def obtener_inscripciones_agrupadas() -> List[Dict]:
    """
    Obtiene todas las inscripciones agrupadas por alumno y clase
    Retorna lista con: alumno_id, alumno_nombre, clase_id, clase_nombre, horarios
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        query = """
            SELECT 
                a.id as alumno_id,
                p.nomb_apel as alumno_nombre,
                c.id as clase_id,
                c.nombre_clase as clase_nombre,
                json_agg(
                    json_build_object(
                        'dia', h.dia,
                        'hora', h.hora_init::text,
                        'aula', hc.aula
                    )
                    ORDER BY 
                        CASE h.dia
                            WHEN 'Lunes' THEN 1
                            WHEN 'Martes' THEN 2
                            WHEN 'Miércoles' THEN 3
                            WHEN 'Jueves' THEN 4
                            WHEN 'Viernes' THEN 5
                            WHEN 'Sábado' THEN 6
                            WHEN 'Domingo' THEN 7
                        END,
                        h.hora_init
                ) as horarios
            FROM alumno a
            JOIN persona p ON a.id_persona = p.id
            JOIN alumno_clase ac ON a.id = ac.id_alumno
            JOIN clase c ON ac.id_clase = c.id
            JOIN horario_clase hc ON c.id = hc.id_clase
            JOIN horario h ON hc.id_horario = h.id
            GROUP BY a.id, p.nomb_apel, c.id, c.nombre_clase
            ORDER BY p.nomb_apel, c.nombre_clase
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        resultados = []
        for row in rows:
            resultados.append({
                'alumno_id': row[0],
                'alumno_nombre': row[1],
                'clase_id': row[2],
                'clase_nombre': row[3],
                'horarios': row[4] if row[4] else []
            })
        
        cur.close()
        conn.close()
        
        print(f"✅ Obtenidas {len(resultados)} inscripciones agrupadas")
        return resultados
        
    except Exception as e:
        print(f"❌ Error obteniendo inscripciones agrupadas: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return []


def obtener_alumnos_por_clase(id_clase: int) -> List[Dict]:
    """
    Obtiene todos los alumnos de una clase específica
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        query = """
            SELECT 
                a.id as alumno_id,
                p.nomb_apel as alumno_nombre,
                ac.fecha_inscripcion
            FROM alumno a
            JOIN persona p ON a.id_persona = p.id
            JOIN alumno_clase ac ON a.id = ac.id_alumno
            WHERE ac.id_clase = %s
            ORDER BY p.nomb_apel
        """
        
        cur.execute(query, (id_clase,))
        rows = cur.fetchall()
        
        resultados = []
        for row in rows:
            resultados.append({
                'alumno_id': row[0],
                'alumno_nombre': row[1],
                'fecha_inscripcion': row[2].isoformat() if row[2] else None
            })
        
        cur.close()
        conn.close()
        
        return resultados
        
    except Exception as e:
        print(f"❌ Error obteniendo alumnos por clase: {e}")
        if conn:
            conn.close()
        return []


def obtener_horarios_por_clase(id_clase: int) -> List[Dict]:
    """
    Obtiene todos los horarios de una clase específica
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        query = """
            SELECT 
                hc.id,
                h.dia,
                h.hora_init,
                hc.aula
            FROM horario_clase hc
            JOIN horario h ON hc.id_horario = h.id
            WHERE hc.id_clase = %s
            ORDER BY 
                CASE h.dia
                    WHEN 'Lunes' THEN 1
                    WHEN 'Martes' THEN 2
                    WHEN 'Miércoles' THEN 3
                    WHEN 'Jueves' THEN 4
                    WHEN 'Viernes' THEN 5
                    WHEN 'Sábado' THEN 6
                    WHEN 'Domingo' THEN 7
                END,
                h.hora_init
        """
        
        cur.execute(query, (id_clase,))
        rows = cur.fetchall()
        
        resultados = []
        for row in rows:
            resultados.append({
                'id': row[0],
                'dia': row[1],
                'hora': row[2].strftime('%H:%M') if row[2] else None,
                'aula': row[3]
            })
        
        cur.close()
        conn.close()
        
        return resultados
        
    except Exception as e:
        print(f"❌ Error obteniendo horarios por clase: {e}")
        if conn:
            conn.close()
        return []
    


from database.connection import get_connection
from typing import List, Dict
import datetime

# database/repos_alumno_clase_edicion.py

def actualizar_horarios_alumno_clase(alumno_id: int, clase_id: int, horarios_nuevos: list) -> bool:
    print(f"\n🔍 [DB] actualizar_horarios_alumno_clase")
    print(f"   alumno_id: {alumno_id} (tipo: {type(alumno_id)})")
    print(f"   clase_id: {clase_id} (tipo: {type(clase_id)})")
    print(f"   horarios_nuevos: {horarios_nuevos}")
    print(f"   cantidad: {len(horarios_nuevos)}")
    
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    cur = conn.cursor()
    try:
        # 1. Obtener la fecha de inscripción original
        cur.execute("""
            SELECT fecha_inscripcion 
            FROM alumno_clase 
            WHERE id_alumno = %s AND id_clase = %s 
            LIMIT 1
        """, (alumno_id, clase_id))
        
        resultado = cur.fetchone()
        if not resultado:
            print(f"⚠️ No se encontró inscripción para alumno {alumno_id} clase {clase_id}")
            fecha_inscripcion = datetime.date.today()
        else:
            fecha_inscripcion = resultado[0]
            print(f"   Fecha inscripción original: {fecha_inscripcion}")
        
        # 2. Eliminar todos los horarios actuales
        cur.execute("""
            DELETE FROM alumno_clase 
            WHERE id_alumno = %s AND id_clase = %s
        """, (alumno_id, clase_id))
        
        deleted_count = cur.rowcount
        print(f"   Eliminados {deleted_count} horarios anteriores")
        
        # 3. Insertar los nuevos horarios
        inserted_count = 0
        for idx, horario in enumerate(horarios_nuevos):
            dia = horario.get('dia')
            hora = horario.get('hora')
            aula = horario.get('aula')
            
            print(f"   Procesando horario {idx+1}: {dia} {hora} Aula {aula}")
            
            # Buscar o crear el horario en la tabla 'horario'
            cur.execute("""
                INSERT INTO horario (dia, hora_init) 
                VALUES (%s, %s)
                ON CONFLICT (dia, hora_init) 
                DO UPDATE SET dia = EXCLUDED.dia 
                RETURNING id
            """, (dia, hora))
            
            horario_id = cur.fetchone()[0]
            print(f"      Horario ID: {horario_id}")
            
            # Insertar en alumno_clase
            cur.execute("""
                INSERT INTO alumno_clase (id_alumno, id_clase, id_horario, aula, fecha_inscripcion)
                VALUES (%s, %s, %s, %s, %s)
            """, (alumno_id, clase_id, horario_id, aula, fecha_inscripcion))
            
            inserted_count += 1
        
        # 4. Commit
        conn.commit()
        print(f"✅ Actualización completada: {inserted_count} horarios guardados")
        return True
        
    except Exception as e:
        print(f"❌ Error en actualizar_horarios_alumno_clase: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def obtener_horarios_alumno_clase(alumno_id: int, clase_id: int) -> List[Dict]:
    """
    Obtiene los horarios actuales usando la tabla real 'alumno_clase'
    """
    conn = get_connection()
    if not conn: return []
    
    try:
        cur = conn.cursor()
        query = """
            SELECT h.dia, h.hora_init::text, ac.aula
            FROM alumno_clase ac
            JOIN horario h ON ac.id_horario = h.id
            WHERE ac.id_alumno = %s AND ac.id_clase = %s
            ORDER BY 
                CASE h.dia 
                    WHEN 'Lunes' THEN 1 WHEN 'Martes' THEN 2 WHEN 'Miércoles' THEN 3 
                    WHEN 'Jueves' THEN 4 WHEN 'Viernes' THEN 5 WHEN 'Sábado' THEN 6 ELSE 7 
                END, h.hora_init
        """
        cur.execute(query, (alumno_id, clase_id))
        return [{'dia': r[0], 'hora': r[1], 'aula': r[2]} for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


# database/repos_alumno_clase_edicion.py
# database/repos_alumno_clase_edicion.py
from database.connection import get_connection
from typing import List, Dict

def obtener_todas_sesiones_agrupadas() -> List[Dict]:
    """
    Obtiene todas las sesiones agrupadas por alumno y clase.
    Retorna una lista donde cada elemento es un alumno con una clase específica
    y todos sus horarios.
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                a.id as alumno_id,
                p.nomb_apel as alumno_nombre,
                c.id as clase_id,
                c.nombre_clase,
                c.duracion,
                pr.id as profesor_id,
                per_prof.nomb_apel as profesor_nombre,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'sesion_id', ac.id,
                            'horario_id', h.id,
                            'dia', h.dia,
                            'hora', h.hora_init::text,
                            'aula', ac.aula,
                            'fecha_inscripcion', ac.fecha_inscripcion
                        )
                        ORDER BY 
                            CASE h.dia
                                WHEN 'Lunes' THEN 1
                                WHEN 'Martes' THEN 2
                                WHEN 'Miércoles' THEN 3
                                WHEN 'Jueves' THEN 4
                                WHEN 'Viernes' THEN 5
                                WHEN 'Sábado' THEN 6
                                ELSE 7
                            END,
                            h.hora_init
                    ),
                    '[]'::json
                ) as horarios
            FROM alumno_clase ac
            JOIN alumno a ON ac.id_alumno = a.id
            JOIN persona p ON a.id_persona = p.id
            JOIN clase c ON ac.id_clase = c.id
            JOIN profesor pr ON c.id_profesor = pr.id
            JOIN persona per_prof ON pr.id_persona = per_prof.id
            JOIN horario h ON ac.id_horario = h.id
            GROUP BY a.id, p.nomb_apel, c.id, c.nombre_clase, c.duracion, pr.id, per_prof.nomb_apel
            ORDER BY p.nomb_apel, c.nombre_clase
        """
        cur.execute(query)
        
        resultados = []
        for row in cur.fetchall():
            resultados.append({
                'alumno_id': row[0],
                'alumno_nombre': row[1],
                'clase_id': row[2],
                'clase_nombre': row[3],
                'clase_duracion': row[4],
                'profesor_id': row[5],
                'profesor_nombre': row[6],
                'horarios': row[7] if row[7] else []
            })
        
        cur.close()
        conn.close()
        print(f"📋 Se obtuvieron {len(resultados)} grupos alumno+clase")
        return resultados
        
    except Exception as e:
        print(f"❌ Error al obtener sesiones agrupadas: {e}")
        if conn:
            conn.close()
        return []


