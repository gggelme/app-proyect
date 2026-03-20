# back/src/database/repos_inscripcion.py
from database.connection import get_connection
from database.repos_horario import guardar_horario, obtener_horario_por_dia_y_hora
from database.repos_horario_clase import guardar_horario_clase
from database.repos_alumno_clase import guardar_alumno_clase
from models.horario import Horario
from datetime import date, time
from typing import List, Dict

class ErrorGuardarInscripcion(Exception):
    """Excepción personalizada para errores al guardar inscripción"""
    pass

def guardar_inscripcion_completa(id_clase: int, horarios: List[Dict], alumnos: List[Dict]) -> Dict:
    """
    Guarda una inscripción completa:
    - Guarda los horarios (si no existen)
    - Asigna horarios a la clase
    - Inscribe los alumnos en la clase
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarInscripcion("No se pudo conectar a la base de datos")
    
    resultados = {
        "horarios_guardados": [],
        "inscripciones": []
    }
    
    try:
        # 1. Procesar cada horario
        for horario_data in horarios:
            dia = horario_data.get("dia")
            hora_str = horario_data.get("hora")
            aula = horario_data.get("aula")
            
            if not dia or not hora_str:
                continue
            
            # Convertir hora string a time object
            try:
                hora_parts = hora_str.split(":")
                hora = time(int(hora_parts[0]), int(hora_parts[1]))
            except:
                print(f"Error al convertir hora: {hora_str}")
                continue
            
            # Verificar si el horario ya existe
            id_horario = obtener_horario_por_dia_y_hora(dia, hora)
            
            if not id_horario:
                # Crear nuevo horario
                nuevo_horario = Horario(dia=dia, hora_init=hora)
                id_horario = guardar_horario(nuevo_horario)
            
            # Asignar horario a la clase
            id_horario_clase = guardar_horario_clase(id_horario, id_clase, aula)
            
            resultados["horarios_guardados"].append({
                "id_horario": id_horario,
                "id_horario_clase": id_horario_clase,
                "dia": dia,
                "hora": hora_str,
                "aula": aula
            })
        
        # 2. Inscribir cada alumno
        for alumno_data in alumnos:
            id_alumno = alumno_data.get("id_alumno")
            if not id_alumno:
                continue
            
            # Inscribir alumno en la clase
            id_inscripcion = guardar_alumno_clase(id_alumno, id_clase)
            
            resultados["inscripciones"].append({
                "id_inscripcion": id_inscripcion,
                "id_alumno": id_alumno
            })
        
        return resultados
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise ErrorGuardarInscripcion(f"Error al guardar inscripción: {str(e)}")