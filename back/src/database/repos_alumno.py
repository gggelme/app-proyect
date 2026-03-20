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
    Retorna el ID de ALUMNO (no el de persona).
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
        print(f"   Persona creada con ID: {persona_id}")
        
        # 2. Insertar en ALUMNO y obtener el ID de ALUMNO
        query_alumno = """
            INSERT INTO alumno (id_persona, fecha_ing, estado_activo)
            VALUES (%s, %s, %s) RETURNING id;
        """
        cur.execute(query_alumno, (
            persona_id, 
            alumno.fecha_ing,
            alumno.estado_activo
        ))
        
        alumno_id = cur.fetchone()[0]  # Este es el ID de la tabla alumno
        print(f"   Alumno creado con ID: {alumno_id} (persona_id: {persona_id})")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Retornando ID de alumno: {alumno_id}")
        return alumno_id  # Retorna el ID de alumno, no de persona
        
    except Exception as e:
        if conn: 
            conn.rollback()
            conn.close()
        raise ErrorGuardarAlumno(f"Error en la base de datos: {str(e)}")
def buscar_alumnos(texto_busqueda: str = "") -> List[Dict]:
    conn = get_connection()
    alumnos = []
    
    try:
        cur = conn.cursor()
        
        if texto_busqueda and texto_busqueda.strip():
            # Si hay texto de búsqueda, filtrar
            query = """
                SELECT 
                    a.id as alumno_id,
                    p.id as persona_id,
                    p.dni, 
                    p.nomb_apel,
                    p.telefono,
                    a.fecha_ing,
                    a.estado_activo
                FROM persona p
                JOIN alumno a ON p.id = a.id_persona
                WHERE p.dni ILIKE %s OR p.nomb_apel ILIKE %s
                ORDER BY p.nomb_apel
                LIMIT 50
            """
            search_pattern = f'%{texto_busqueda}%'
            cur.execute(query, (search_pattern, search_pattern))
        else:
            # Si no hay texto, traer todos
            query = """
                SELECT 
                    a.id as alumno_id,
                    p.id as persona_id,
                    p.dni, 
                    p.nomb_apel,
                    p.telefono,
                    a.fecha_ing,
                    a.estado_activo
                FROM persona p
                JOIN alumno a ON p.id = a.id_persona
                ORDER BY p.nomb_apel
                LIMIT 100
            """
            cur.execute(query)
        
        for row in cur.fetchall():
            alumnos.append({
                'id': row[0],
                'persona_id': row[1],
                'dni': row[2],
                'nomb_apel': row[3],
                'telefono': row[4],
                'fecha_ing': row[5],
                'estado_activo': row[6]
            })
        
        cur.close()
        conn.close()
        return alumnos
        
    except Exception as e:
        print(f"Error al buscar alumnos: {e}")
        return []


def buscar_por_nombre(self, query):
    cursor = self.conn.cursor()
    cursor.execute("""
        SELECT id, nombre, apellido, dni 
        FROM alumnos 
        WHERE activo = 1 
          AND (LOWER(nombre) LIKE LOWER(?) OR LOWER(apellido) LIKE LOWER(?))
        ORDER BY apellido, nombre
        LIMIT 10
    """, (f'%{query}%', f'%{query}%'))
    return cursor.fetchall()


# back/src/database/repos_alumno.py

def buscar_alumnos_por_nombre(texto_busqueda: str) -> List[Dict]:
    """
    Busca alumnos por nombre o apellido (búsqueda parcial)
    Retorna lista de alumnos con sus datos básicos
    """
    conn = get_connection()
    alumnos = []
    
    try:
        cur = conn.cursor()
        
        # Buscar en nomb_apel (que contiene nombre y apellido juntos)
        # o buscar separando nombre y apellido si tu estructura lo permite
        query = """
            SELECT 
                a.id as alumno_id,
                p.id as persona_id,
                p.dni, 
                p.nomb_apel,
                p.telefono,
                a.fecha_ing,
                a.estado_activo
            FROM persona p
            JOIN alumno a ON p.id = a.id_persona
            WHERE p.nomb_apel ILIKE %s
               OR p.dni ILIKE %s
            ORDER BY p.nomb_apel
            LIMIT 10
        """
        search_pattern = f'%{texto_busqueda}%'
        cur.execute(query, (search_pattern, search_pattern))
        
        for row in cur.fetchall():
            alumnos.append({
                'alumno_id': row[0],
                'persona_id': row[1],
                'dni': row[2],
                'nomb_apel': row[3],
                'telefono': row[4],
                'fecha_ing': row[5],
                'estado_activo': row[6]
            })
        
        cur.close()
        conn.close()
        return alumnos
        
    except Exception as e:
        print(f"Error al buscar alumnos por nombre: {e}")
        if conn:
            conn.close()
        return []