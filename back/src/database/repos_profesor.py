# src/database/repos_profesor.py
from database.connection import get_connection
from models.persona import Profesor
from typing import List, Optional, Dict

class ErrorGuardarProfesor(Exception):
    """Excepción personalizada para errores al guardar profesor"""
    pass

def guardar_profesor(profe: Profesor) -> int:
    """
    Guarda un profesor en la base de datos.
    Primero inserta en PERSONA, luego en PROFESOR.
    Retorna el ID generado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarProfesor("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar si el DNI ya existe
        cur.execute("SELECT id FROM persona WHERE dni = %s", (profe.dni,))
        if cur.fetchone():
            raise ErrorGuardarProfesor(f"Ya existe una persona con DNI {profe.dni}")
        
        # 1. Insertar en la tabla PERSONA
        query_persona = """
            INSERT INTO persona (dni, nomb_apel, fecha_nac, domicilio, telefono)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query_persona, (
            profe.dni, 
            profe.nomb_apel, 
            profe.fecha_nac, 
            profe.domicilio, 
            profe.telefono
        ))
        
        persona_id = cur.fetchone()[0]
        
        # 2. Insertar en la tabla PROFESOR
        query_profe = """
            INSERT INTO profesor (id_persona, alias, email)
            VALUES (%s, %s, %s);
        """
        cur.execute(query_profe, (
            persona_id, 
            profe.alias,
            profe.email
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Profesor guardado correctamente con ID: {persona_id}")
        return persona_id

    except Exception as e:
        conn.rollback()
        if "duplicate key" in str(e).lower():
            raise ErrorGuardarProfesor(f"Ya existe un profesor con esos datos: {str(e)}")
        elif "not null" in str(e).lower():
            raise ErrorGuardarProfesor(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarProfesor(f"Error en la base de datos: {str(e)}")

def obtener_todos_profesores() -> List[Dict]:
    """
    Obtiene todos los profesores con sus datos.
    IMPORTANTE: Devuelve el id de la tabla profesor (no el de persona)
    """
    conn = get_connection()
    profesores = []
    
    if not conn:
        return profesores
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                pr.id as profesor_id,  -- ← ESTE es el que necesitas para clase
                p.id as persona_id,
                p.nomb_apel,
                p.dni,
                pr.alias,
                pr.email
            FROM profesor pr
            JOIN persona p ON pr.id_persona = p.id
            ORDER BY p.nomb_apel
        """
        cur.execute(query)
        
        for row in cur.fetchall():
            profesores.append({
                'id': row[0],           # ← profesor_id (para clase.id_profesor)
                'persona_id': row[1],   # ← persona_id (para otros usos)
                'nomb_apel': row[2],
                'dni': row[3],
                'alias': row[4],
                'email': row[5]
            })
        
        cur.close()
        conn.close()
        return profesores
        
    except Exception as e:
        print(f"❌ Error al obtener profesores: {e}")
        if conn:
            conn.close()
        return []

def buscar_por_nombre(self, query):
    cursor = self.conn.cursor()
    cursor.execute("""
        SELECT id, nombre, apellido, alias 
        FROM profesores 
        WHERE activo = 1 
          AND (LOWER(nombre) LIKE LOWER(?) OR LOWER(apellido) LIKE LOWER(?))
        ORDER BY apellido, nombre
        LIMIT 10
    """, (f'%{query}%', f'%{query}%'))
    return cursor.fetchall()


def actualizar_profesor(id_profesor: int, profesor_data: dict) -> bool:
    """
    Actualiza los datos de un profesor
    Retorna True si se actualizó correctamente
    """
    conn = get_connection()
    
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cur = conn.cursor()
        
        # Primero obtenemos el id_persona del profesor
        cur.execute("SELECT id_persona FROM profesor WHERE id = %s", (id_profesor,))
        result = cur.fetchone()
        
        if not result:
            print(f"❌ Profesor con ID {id_profesor} no encontrado")
            return False
        
        id_persona = result[0]
        
        # Si se está cambiando el DNI, verificar que no esté en uso por otra persona
        nuevo_dni = profesor_data.get('dni')
        if nuevo_dni:
            cur.execute("SELECT id FROM persona WHERE dni = %s AND id != %s", (nuevo_dni, id_persona))
            existe = cur.fetchone()
            if existe:
                print(f"❌ El DNI {nuevo_dni} ya está siendo usado por otra persona")
                conn.close()
                return False
        
        # Construir la consulta dinámicamente según los campos que vienen
        persona_updates = []
        persona_values = []
        
        if 'nomb_apel' in profesor_data and profesor_data['nomb_apel'] is not None:
            persona_updates.append("nomb_apel = %s")
            persona_values.append(profesor_data['nomb_apel'])
        
        if 'dni' in profesor_data and profesor_data['dni'] is not None:
            persona_updates.append("dni = %s")
            persona_values.append(profesor_data['dni'])
        
        if 'fecha_nac' in profesor_data:
            persona_updates.append("fecha_nac = %s")
            persona_values.append(profesor_data['fecha_nac'])
        
        if 'domicilio' in profesor_data:
            persona_updates.append("domicilio = %s")
            persona_values.append(profesor_data['domicilio'])
        
        if 'telefono' in profesor_data:
            persona_updates.append("telefono = %s")
            persona_values.append(profesor_data['telefono'])
        
        if persona_updates:
            persona_values.append(id_persona)
            query_persona = f"UPDATE persona SET {', '.join(persona_updates)} WHERE id = %s"
            cur.execute(query_persona, persona_values)
        
        # Actualizar datos en profesor
        profesor_updates = []
        profesor_values = []
        
        if 'alias' in profesor_data:
            profesor_updates.append("alias = %s")
            profesor_values.append(profesor_data['alias'])
        
        if 'email' in profesor_data:
            profesor_updates.append("email = %s")
            profesor_values.append(profesor_data['email'])
        
        if profesor_updates:
            profesor_values.append(id_profesor)
            query_profesor = f"UPDATE profesor SET {', '.join(profesor_updates)} WHERE id = %s"
            cur.execute(query_profesor, profesor_values)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Profesor ID {id_profesor} actualizado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar profesor: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False