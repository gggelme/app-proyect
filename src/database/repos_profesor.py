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
    Obtiene todos los profesores con sus datos completos.
    Retorna una lista de diccionarios con la información.
    """
    conn = get_connection()
    profesores = []
    
    if not conn:
        return profesores
    
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
                pr.alias,
                pr.email
            FROM persona p
            JOIN profesor pr ON p.id = pr.id_persona
            ORDER BY p.nomb_apel
        """
        cur.execute(query)
        
        for row in cur.fetchall():
            profesores.append({
                'id': row[0],
                'dni': row[1],
                'nomb_apel': row[2],
                'fecha_nac': row[3],
                'domicilio': row[4],
                'telefono': row[5],
                'fecha_registro': row[6],
                'alias': row[7],
                'email': row[8]
            })
        
        cur.close()
        conn.close()
        print(f"📋 Se obtuvieron {len(profesores)} profesores")
        
    except Exception as e:
        print(f"❌ Error al obtener profesores: {e}")
    
    return profesores