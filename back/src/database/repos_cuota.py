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
    print("🔍 Iniciando obtener_todas_cuotas...")
    conn = get_connection()
    cuotas = []
    
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return cuotas
    
    try:
        cursor = conn.cursor()
        print("📝 Ejecutando SELECT...")
        cursor.execute("SELECT id, nombre, precio_cuota FROM cuota ORDER BY nombre")
        cuotas_raw = cursor.fetchall()
        print(f"✅ Registros encontrados: {len(cuotas_raw)}")
        
        cuotas = [{"id": c[0], "nombre": c[1], "precio": c[2]} for c in cuotas_raw]
        print(f"📊 Cuotas formateadas: {cuotas}")
        return cuotas
    except Exception as e:
        print(f"❌ Error en obtener_todas_cuotas: {e}")
        return []
    finally:
        conn.close()


   # src/database/repos_cuota.py

def actualizar_precios_cuotas(cuotas_data: list) -> dict:
    """
    Actualiza los precios de múltiples cuotas.
    Recibe lista de diccionarios con 'id' y 'nuevo_precio'
    Retorna dict con resultados
    """
    print(f"🔄 Actualizando {len(cuotas_data)} cuotas...")
    conn = get_connection()
    
    if not conn:
        return {
            "success": False, 
            "message": "Error de conexión a la base de datos",
            "actualizadas": 0,
            "fallidas": 0,
            "detalles": []
        }
    
    resultados = {
        "success": True,
        "actualizadas": 0,
        "fallidas": 0,
        "detalles": []
    }
    
    try:
        cursor = conn.cursor()
        
        for cuota in cuotas_data:
            try:
                id_cuota = cuota["id"]
                nuevo_precio = cuota["nuevo_precio"]
                
                # Primero verificamos si existe
                cursor.execute("SELECT id, nombre FROM cuota WHERE id = %s", (id_cuota,))
                existe = cursor.fetchone()
                
                if not existe:
                    resultados["fallidas"] += 1
                    resultados["detalles"].append({
                        "id": id_cuota,
                        "estado": "error",
                        "mensaje": "Cuota no encontrada"
                    })
                    continue
                
                # Actualizamos el precio
                cursor.execute(
                    "UPDATE cuota SET precio_cuota = %s WHERE id = %s",
                    (nuevo_precio, id_cuota)
                )
                
                resultados["actualizadas"] += 1
                resultados["detalles"].append({
                    "id": id_cuota,
                    "nombre": existe[1],
                    "estado": "ok",
                    "nuevo_precio": nuevo_precio
                })
                
                print(f"✅ Cuota actualizada: {existe[1]} (ID: {id_cuota}) -> ${nuevo_precio}")
                
            except Exception as e:
                resultados["fallidas"] += 1
                resultados["detalles"].append({
                    "id": id_cuota,
                    "estado": "error",
                    "mensaje": str(e)
                })
                print(f"❌ Error actualizando cuota ID {id_cuota}: {e}")
        
        # Hacemos commit de todas las operaciones exitosas
        conn.commit()
        
        # Si hubo algún error, marcamos success como false
        if resultados["fallidas"] > 0:
            resultados["success"] = False
            resultados["message"] = f"Se actualizaron {resultados['actualizadas']} cuotas, {resultados['fallidas']} fallaron"
        else:
            resultados["message"] = f"Todas las cuotas actualizadas correctamente ({resultados['actualizadas']})"
        
        return resultados
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error en actualización masiva: {e}")
        return {
            "success": False,
            "message": f"Error en la base de datos: {str(e)}",
            "actualizadas": 0,
            "fallidas": len(cuotas_data),
            "detalles": []
        }
    finally:
        conn.close()


