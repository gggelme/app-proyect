# src/database/repos_alumno_clase.py
from database.connection import get_connection
from datetime import date
from typing import List, Dict

class ErrorGuardarAlumnoClase(Exception):
    """Excepción personalizada para errores al guardar alumno-clase"""
    pass

class ErrorGuardarInscripcion(Exception):
    """Excepción personalizada para errores al guardar alumno-clase"""
    pass


class ErrorConsultaHorarios(Exception):
    pass


def guardar_alumno_clase(
    id_alumno: int, 
    id_clase: int, 
    id_horario: int,
    aula: str,  # ← Nuevo parámetro
    fecha_inscripcion: date = None
) -> int:
    """
    Inscribe un alumno en una clase con un horario específico y aula.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarAlumnoClase("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificaciones
        cur.execute("SELECT id FROM alumno WHERE id = %s", (id_alumno,))
        if not cur.fetchone():
            raise ErrorGuardarAlumnoClase(f"No existe un alumno con ID {id_alumno}")
        
        cur.execute("SELECT id FROM clase WHERE id = %s", (id_clase,))
        if not cur.fetchone():
            raise ErrorGuardarAlumnoClase(f"No existe una clase con ID {id_clase}")
        
        cur.execute("SELECT id FROM horario WHERE id = %s", (id_horario,))
        if not cur.fetchone():
            raise ErrorGuardarAlumnoClase(f"No existe un horario con ID {id_horario}")
        
        if fecha_inscripcion is None:
            fecha_inscripcion = date.today()
        
        # Insertar con aula
        query = """
            INSERT INTO alumno_clase (id_alumno, id_clase, id_horario, aula, fecha_inscripcion)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query, (id_alumno, id_clase, id_horario, aula, fecha_inscripcion))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "duplicate key" in str(e).lower() or "ak_alumno_clase" in str(e):
            raise ErrorGuardarAlumnoClase(f"El alumno ya está inscrito en esa clase y horario.")
        raise ErrorGuardarAlumnoClase(f"Error en la base de datos: {str(e)}")



# database/repos_alumno_clase.py

def obtener_clases_por_dia_y_hora(dia: str, hora: str) -> List[Dict]:
    """
    Obtiene todas las clases que se dictan en un día y hora específicos.
    Retorna una lista donde cada elemento es una combinación de clase + aula.
    """
    print(f"🔍 Buscando clases para día: {dia}, hora: {hora}")
    
    conn = get_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return []
    
    try:
        cur = conn.cursor()
        
        # Normalizar la hora
        hora_normalizada = hora
        if len(hora.split(':')) == 2:
            hora_normalizada = hora + ":00"
        
        # Buscar horarios
        query_horarios = """
            SELECT id, dia, hora_init 
            FROM horario 
            WHERE dia = %s AND hora_init::text = %s
        """
        cur.execute(query_horarios, (dia, hora_normalizada))
        horarios = cur.fetchall()
        
        if not horarios:
            cur.close()
            conn.close()
            return []
        
        clases_resultado = []
        
        for horario in horarios:
            horario_id = horario[0]
            
            # Consulta corregida: agrupar por clase Y aula
            query_clases = """
                SELECT 
                    ac.id as alumno_clase_id,
                    c.id as clase_id,
                    c.nombre_clase,
                    c.duracion,
                    per_prof.nomb_apel as profesor_nombre,
                    ac.aula,  -- ← Aula de esta inscripción
                    COALESCE(
                        json_agg(DISTINCT per_alumno.nomb_apel) FILTER (WHERE per_alumno.nomb_apel IS NOT NULL),
                        '[]'::json
                    ) as alumnos
                FROM alumno_clase ac
                JOIN clase c ON ac.id_clase = c.id
                JOIN profesor prof ON c.id_profesor = prof.id
                JOIN persona per_prof ON prof.id_persona = per_prof.id
                LEFT JOIN alumno a ON ac.id_alumno = a.id
                LEFT JOIN persona per_alumno ON a.id_persona = per_alumno.id
                WHERE ac.id_horario = %s
                GROUP BY ac.id, c.id, c.nombre_clase, c.duracion, per_prof.nomb_apel, ac.aula
                ORDER BY c.nombre_clase, ac.aula
            """
            cur.execute(query_clases, (horario_id,))
            clases = cur.fetchall()
            
            print(f"   Clases encontradas para horario {horario_id}: {len(clases)}")
            
            for clase in clases:
                # Imprimir para debug
                print(f"      - Clase: {clase[2]}, Aula: {clase[5]}, Alumnos: {len(clase[6]) if clase[6] else 0}")
                
                clases_resultado.append({
                    'alumno_clase_id': clase[0],
                    'clase_id': clase[1],
                    'nombre_clase': clase[2],
                    'duracion': clase[3],
                    'profesor_nombre': clase[4],
                    'aula': clase[5],  # ← Aula individual
                    'alumnos': clase[6] if clase[6] else [],
                    'horario': {
                        'horario_id': horario_id,
                        'dia': horario[1],
                        'hora': str(horario[2])
                    }
                })
        
        cur.close()
        conn.close()
        
        print(f"✅ Total de clases+aule encontradas: {len(clases_resultado)}")
        return clases_resultado
        
    except Exception as e:
        print(f"❌ Error al obtener clases por día y hora: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return []

# database/repos_inscripcion.py

def guardar_inscripcion_completa(id_clase: int, horarios: List[Dict], alumnos: List[Dict]) -> Dict:
    """
    Guarda una inscripción completa:
    - Para cada horario, crea/obtiene el horario en la tabla horario
    - Para cada alumno, crea una entrada en alumno_clase con aula
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarInscripcion("No se pudo conectar a la base de datos")
    
    resultados = {
        "horarios_guardados": [],
        "inscripciones": [],
        "errores": []
    }
    
    try:
        cur = conn.cursor()
        
        # 1. Verificar que la clase existe
        cur.execute("SELECT id FROM clase WHERE id = %s", (id_clase,))
        if not cur.fetchone():
            raise ErrorGuardarInscripcion(f"No existe una clase con ID {id_clase}")
        
        # 2. Para cada horario, obtener o crear el horario
        horarios_ids = []
        for horario in horarios:
            dia = horario.get('dia')
            hora = horario.get('hora')
            aula = horario.get('aula')
            
            if not dia or not hora:
                resultados["errores"].append(f"Horario inválido: {horario}")
                continue
            
            # Normalizar hora (asegurar formato HH:MM:SS)
            if len(hora.split(':')) == 2:
                hora = hora + ":00"
            
            # Buscar si ya existe el horario
            cur.execute("""
                SELECT id FROM horario 
                WHERE dia = %s AND hora_init = %s
            """, (dia, hora))
            
            horario_existente = cur.fetchone()
            
            if horario_existente:
                horario_id = horario_existente[0]
                resultados["horarios_guardados"].append({
                    "horario_id": horario_id,
                    "dia": dia,
                    "hora": hora,
                    "aula": aula,
                    "nuevo": False
                })
            else:
                # Crear nuevo horario
                cur.execute("""
                    INSERT INTO horario (dia, hora_init)
                    VALUES (%s, %s) RETURNING id
                """, (dia, hora))
                horario_id = cur.fetchone()[0]
                resultados["horarios_guardados"].append({
                    "horario_id": horario_id,
                    "dia": dia,
                    "hora": hora,
                    "aula": aula,
                    "nuevo": True
                })
            
            horarios_ids.append({
                "id": horario_id,
                "aula": aula
            })
        
        # 3. Para cada alumno, crear inscripción en alumno_clase con aula
        fecha_actual = date.today()
        
        for alumno in alumnos:
            id_alumno = alumno.get('id_alumno')
            
            if not id_alumno:
                resultados["errores"].append(f"Alumno sin ID: {alumno}")
                continue
            
            # Verificar que el alumno existe
            cur.execute("SELECT id FROM alumno WHERE id = %s", (id_alumno,))
            if not cur.fetchone():
                resultados["errores"].append(f"No existe alumno con ID {id_alumno}")
                continue
            
            # Crear inscripción para cada horario
            for horario_info in horarios_ids:
                horario_id = horario_info["id"]
                aula = horario_info["aula"]
                
                try:
                    cur.execute("""
                        INSERT INTO alumno_clase (id_alumno, id_clase, id_horario, aula, fecha_inscripcion)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id
                    """, (id_alumno, id_clase, horario_id, aula, fecha_actual))
                    
                    inscripcion_id = cur.fetchone()[0]
                    resultados["inscripciones"].append({
                        "alumno_id": id_alumno,
                        "clase_id": id_clase,
                        "horario_id": horario_id,
                        "aula": aula,
                        "inscripcion_id": inscripcion_id
                    })
                    
                except Exception as e:
                    if "duplicate key" in str(e).lower():
                        resultados["errores"].append(
                            f"Alumno {id_alumno} ya está inscrito en clase {id_clase} con horario {horario_id}"
                        )
                    else:
                        resultados["errores"].append(
                            f"Error al inscribir alumno {id_alumno}: {str(e)}"
                        )
        
        # Commit de todos los cambios
        conn.commit()
        cur.close()
        conn.close()
        
        return resultados
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise ErrorGuardarInscripcion(f"Error en la base de datos: {str(e)}")
