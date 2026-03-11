# src/database/repos_cuota.py
from database.connection import get_connection
from models.cuota import Cuota

class ErrorGuardarCuota(Exception):
    """Excepción personalizada para errores al guardar cuota"""
    pass

def guardar_cuota(cuota: Cuota) -> int:
    """
    Guarda una nueva cuota en la base de datos.
    Retorna el ID generado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarCuota("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Insertar la cuota
        query = """
            INSERT INTO cuota (nombre, precio_cuota)
            VALUES (%s, %s) RETURNING id;
        """
        cur.execute(query, (
            cuota.nombre,
            cuota.precio_cuota
        ))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Cuota guardada correctamente con ID: {id_generado}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "duplicate key" in str(e).lower():
            raise ErrorGuardarCuota(f"Ya existe una cuota con ese nombre: {str(e)}")
        elif "not null" in str(e).lower():
            raise ErrorGuardarCuota(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarCuota(f"Error en la base de datos: {str(e)}")
        

def obtener_todas_cuotas():
    """
    Obtiene todas las cuotas ordenadas por nombre.
    """
    conn = get_connection()
    cuotas = []
    
    if not conn:
        return cuotas
    
    try:
        cur = conn.cursor()
        query = """
            SELECT id, nombre, precio_cuota
            FROM cuota
            ORDER BY nombre
        """
        cur.execute(query)
        
        for row in cur.fetchall():
            cuotas.append({
                'id': row[0],
                'nombre': row[1],
                'precio_cuota': float(row[2]) if row[2] else 0
            })
        
        cur.close()
        conn.close()
        print(f"📋 Se obtuvieron {len(cuotas)} cuotas")
        
    except Exception as e:
        print(f"❌ Error al obtener cuotas: {e}")
    
    return cuotas