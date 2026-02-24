# src/database/repos_alumno_clase.py
from database.connection import get_connection
from datetime import date

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