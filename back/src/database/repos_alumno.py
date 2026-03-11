# src/database/repos_alumno.py
from database.connection import get_connection
from models.persona import Alumno
from typing import List, Optional, Dict

class ErrorGuardarAlumno(Exception):
    """Excepción personalizada para errores al guardar alumno"""
    pass

def guardar_alumno(alumno: Alumno) -> int:
    """
    Guarda un alumno en la base de datos.
    Primero inserta en PERSONA, luego en ALUMNO.
    Retorna el ID generado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarAlumno("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar si el DNI ya existe
        cur.execute("SELECT id FROM persona WHERE dni = %s", (alumno.dni,))
        if cur.fetchone():
            raise ErrorGuardarAlumno(f"Ya existe una persona con DNI {alumno.dni}")
        
        # 1. Insertar en PERSONA
        query_persona = """
            INSERT INTO persona (dni, nomb_apel, fecha_nac, domicilio, telefono)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query_persona, (
            alumno.dni, 
            alumno.nomb_apel, 
            alumno.fecha_nac, 
            alumno.domicilio, 
            alumno.telefono
        ))
        persona_id = cur.fetchone()[0]
        
        # 2. Insertar en ALUMNO (con los nuevos campos)
        query_alumno = """
            INSERT INTO alumno (id_persona, fecha_ing, estado_activo)
            VALUES (%s, %s, %s);
        """
        cur.execute(query_alumno, (
            persona_id, 
            alumno.fecha_ing,
            alumno.estado_activo
        ))

        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Alumno guardado correctamente con ID: {persona_id}")
        return persona_id
        
    except Exception as e:
        if conn: 
            conn.rollback()
            conn.close()
        
        if "duplicate key" in str(e).lower():
            raise ErrorGuardarAlumno(f"Ya existe un alumno con esos datos: {str(e)}")
        elif "not null" in str(e).lower():
            raise ErrorGuardarAlumno(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarAlumno(f"Error en la base de datos: {str(e)}")

def buscar_alumnos(texto_busqueda: str) -> List[Dict]:
    conn = get_connection()
    alumnos = []
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                a.id as alumno_id,  -- <--- ESTE ES EL ID DE ALUMNO
                p.id as persona_id, -- <--- ESTE ES EL ID DE PERSONA
                p.dni, 
                p.nomb_apel,
                p.telefono,
                a.fecha_ing,
                a.estado_activo
            FROM persona p
            JOIN alumno a ON p.id = a.id_persona
            WHERE p.dni ILIKE %s OR p.nomb_apel ILIKE %s
            ORDER BY p.nomb_apel
            LIMIT 20
        """
        search_pattern = f'%{texto_busqueda}%'
        cur.execute(query, (search_pattern, search_pattern))
        
        for row in cur.fetchall():
            alumnos.append({
                'id': row[0],  # <--- ALUMNO_ID (el que necesitás para relaciones)
                'persona_id': row[1],  # <--- PERSONA_ID
                'dni': row[2],
                'nomb_apel': row[3],
                'telefono': row[4],
                'fecha_ing': row[5],
                'estado_activo': row[6]
            })
        
        return alumnos
    except Exception as e:
        print(f"Error al buscar alumnos: {e}")
        return []

def obtener_alumno_completo(id_alumno: int) -> Optional[Dict]:
    """
    Obtiene todos los datos de un alumno específico (para usar después)
    """
    conn = get_connection()
    
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                p.id,
                p.dni, 
                p.nomb_apel,
                p.fecha_nac,
                p.domicilio,
                p.telefono,
                p.fecha_registro,
                a.fecha_ing,
                a.estado_activo
            FROM persona p
            JOIN alumno a ON p.id = a.id_persona
            WHERE p.id = %s
        """
        cur.execute(query, (id_alumno,))
        row = cur.fetchone()
        
        if row:
            alumno = {
                'id': row[0],
                'dni': row[1],
                'nomb_apel': row[2],
                'fecha_nac': row[3],
                'domicilio': row[4],
                'telefono': row[5],
                'fecha_registro': row[6],
                'fecha_ing': row[7],
                'estado_activo': row[8]
            }
        else:
            alumno = None
        
        cur.close()
        conn.close()
        return alumno
        
    except Exception as e:
        print(f"❌ Error al obtener alumno completo: {e}")
        return None

def obtener_todos_alumnos() -> List[Dict]:
    """
    Obtiene todos los alumnos (para usar después)
    """
    conn = get_connection()
    alumnos = []
    
    if not conn:
        return alumnos
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                p.id,
                p.dni, 
                p.nomb_apel,
                a.estado_activo
            FROM persona p
            JOIN alumno a ON p.id = a.id_persona
            ORDER BY p.nomb_apel
        """
        cur.execute(query)
        
        for row in cur.fetchall():
            alumnos.append({
                'id': row[0],
                'dni': row[1],
                'nomb_apel': row[2],
                'estado_activo': row[3]
            })
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al obtener alumnos: {e}")
    
    return alumnos