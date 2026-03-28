# database/repos_inscripcion.py
from database.connection import get_connection
from datetime import date
from typing import List, Dict

class ErrorGuardarInscripcion(Exception):
    """Excepción personalizada para errores al guardar inscripción"""
    pass

def guardar_inscripcion_completa(id_clase: int, horarios: List[Dict], alumnos: List[Dict]) -> Dict:
    """
    Guarda una inscripción completa:
    - Para cada horario, crea/obtiene el horario en la tabla horario
    - Para cada alumno, crea una entrada en alumno_clase
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
                    "nuevo": True
                })
            
            horarios_ids.append({
                "id": horario_id,
                "aula": aula
            })
        
        # 3. Para cada alumno, crear inscripción en alumno_clase
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
                
                try:
                    cur.execute("""
                        INSERT INTO alumno_clase (id_alumno, id_clase, id_horario, fecha_inscripcion)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """, (id_alumno, id_clase, horario_id, fecha_actual))
                    
                    inscripcion_id = cur.fetchone()[0]
                    resultados["inscripciones"].append({
                        "alumno_id": id_alumno,
                        "clase_id": id_clase,
                        "horario_id": horario_id,
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