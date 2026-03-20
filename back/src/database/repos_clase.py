# src/database/repos_clase.py
from typing import Dict, List, Optional

from database.connection import get_connection
from models.clase import Clase

class ErrorGuardarClase(Exception):
    """Excepción personalizada para errores al guardar clase"""
    pass

def guardar_clase(clase: Clase) -> int:
    """
    Guarda una nueva clase en la base de datos.
    Retorna el ID generado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarClase("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que el profesor existe
        cur.execute("SELECT id FROM profesor WHERE id = %s", (clase.id_profesor,))
        if not cur.fetchone():
            raise ErrorGuardarClase(f"No existe un profesor con ID {clase.id_profesor}")
        
        # Insertar la clase (incluyendo duracion)
        query = """
            INSERT INTO clase (nombre_clase, id_profesor, duracion)
            VALUES (%s, %s, %s) RETURNING id;
        """
        cur.execute(query, (
            clase.nombre_clase,
            clase.id_profesor,
            clase.duracion  # Nueva columna
        ))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Clase guardada correctamente con ID: {id_generado}")
        print(f"   Nombre: {clase.nombre_clase}")
        print(f"   Profesor ID: {clase.id_profesor}")
        if clase.duracion:
            print(f"   Duración: {clase.duracion} minutos")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "foreign key" in str(e).lower():
            raise ErrorGuardarClase(f"El profesor con ID {clase.id_profesor} no existe")
        elif "not null" in str(e).lower():
            raise ErrorGuardarClase(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarClase(f"Error en la base de datos: {str(e)}")

# Si tenés otras funciones en el repositorio (como obtener_todas_clases, etc.),
# actualizalas también para incluir el campo duracion


def obtener_todas_clases_con_detalles() -> List[Dict]:
    """
    Obtiene todas las clases con:
    - Nombre de la clase
    - Profesor (nombre)
    - Duración
    - Todos sus horarios (día, hora, aula)
    """
    conn = get_connection()
    clases = []
    
    if not conn:
        return clases
    
    try:
        cur = conn.cursor()
        
        query = """
            SELECT 
                c.id,
                c.nombre_clase,
                c.id_profesor,
                p.nomb_apel as nombre_profesor,
                c.duracion,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'id', hc.id,
                            'dia', h.dia,
                            'hora_init', h.hora_init::text,
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
                    ) FILTER (WHERE h.id IS NOT NULL),
                    '[]'::json
                ) as horarios
            FROM clase c
            JOIN persona p ON c.id_profesor = p.id
            LEFT JOIN horario_clase hc ON c.id = hc.id_clase
            LEFT JOIN horario h ON hc.id_horario = h.id
            GROUP BY c.id, c.nombre_clase, c.id_profesor, p.nomb_apel, c.duracion
            ORDER BY c.nombre_clase
        """
        
        cur.execute(query)
        
        for row in cur.fetchall():
            clases.append({
                'id': row[0],
                'nombre_clase': row[1],
                'id_profesor': row[2],
                'nombre_profesor': row[3],
                'duracion': row[4],
                'horarios': row[5] if row[5] else []
            })
        
        cur.close()
        conn.close()
        
        print(f"✅ Se obtuvieron {len(clases)} clases")
        
    except Exception as e:
        print(f"❌ Error obteniendo clases: {e}")
        import traceback
        traceback.print_exc()
    
    return clases

def get_nombres_clases(self):
    cursor = self.conn.cursor()
    cursor.execute("SELECT DISTINCT nombre_clase FROM clases ORDER BY nombre_clase")
    return [row[0] for row in cursor.fetchall()]


def crear(self, nombre_clase, profesor_id):
    cursor = self.conn.cursor()
    cursor.execute(
        "INSERT INTO clases (nombre_clase, profesor_id) VALUES (?, ?)",
        (nombre_clase, profesor_id)
    )
    self.conn.commit()
    return cursor.lastrowid


def get_clases_por_dia_hora(self, dia, hora):
    cursor = self.conn.cursor()
    cursor.execute("""
        SELECT c.id, c.nombre_clase, h.dia, h.hora, h.aula,
               p.nombre || ' ' || p.apellido as profesor,
               GROUP_CONCAT(a.nombre || ' ' || a.apellido) as alumnos
        FROM clases c
        JOIN clase_horarios h ON c.id = h.clase_id
        JOIN profesores p ON c.profesor_id = p.id
        LEFT JOIN clase_alumnos ca ON c.id = ca.clase_id
        LEFT JOIN alumnos a ON ca.alumno_id = a.id
        WHERE h.dia = ? AND h.hora = ?
        GROUP BY c.id, h.id
    """, (dia, hora))
    
    resultados = []
    for row in cursor.fetchall():
        resultados.append({
            "id": row[0],
            "nombre_clase": row[1],
            "dia": row[2],
            "hora": row[3],
            "aula": row[4],
            "profesor": row[5],
            "alumnos": row[6].split(',') if row[6] else []
        })
    return resultados

def obtener_todas_clases() -> List[Dict]:
    """
    Obtiene todas las clases con su información básica
    """
    conn = get_connection()
    clases = []
    
    try:
        cur = conn.cursor()
        
        query = """
            SELECT 
                c.id,
                c.nombre_clase,
                c.duracion,
                p.nomb_apel as profesor_nombre
            FROM clase c
            JOIN profesor prof ON c.id_profesor = prof.id
            JOIN persona p ON prof.id_persona = p.id
            ORDER BY c.nombre_clase
        """
        
        cur.execute(query)
        
        for row in cur.fetchall():
            clases.append({
                'id': row[0],
                'nombre_clase': row[1],
                'duracion': row[2],
                'profesor': row[3]
            })
        
        cur.close()
        conn.close()
        return clases
        
    except Exception as e:
        print(f"Error al obtener clases: {e}")
        if conn:
            conn.close()
        return []