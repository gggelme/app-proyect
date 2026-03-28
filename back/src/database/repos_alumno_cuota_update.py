# src/database/repos_alumno_cuota_update.py
from database.connection import get_connection
from datetime import datetime
from typing import List

def actualizar_cuotas_alumno(id_alumno: int, ids_cuotas_nuevas: List[int]) -> dict:
    """
    Actualiza las cuotas de un alumno
    - Elimina cuotas que ya no están seleccionadas
    - Agrega nuevas cuotas que fueron seleccionadas
    - Para nuevas cuotas, genera el pago inicial
    """
    conn = get_connection()
    if not conn:
        return {"success": False, "message": "Error de conexión"}
    
    try:
        cur = conn.cursor()
        
        # 1. Obtener cuotas actuales del alumno
        cur.execute("""
            SELECT id, id_cuota FROM alumno_cuota WHERE id_alumno = %s
        """, (id_alumno,))
        cuotas_actuales = cur.fetchall()
        
        ids_actuales = [c[1] for c in cuotas_actuales]  # ids de cuota
        id_alumno_cuota_actual = {c[1]: c[0] for c in cuotas_actuales}  # mapeo id_cuota -> id_alumno_cuota
        
        # 2. Determinar cuátes eliminar y cuáles agregar
        ids_a_eliminar = set(ids_actuales) - set(ids_cuotas_nuevas)
        ids_a_agregar = set(ids_cuotas_nuevas) - set(ids_actuales)
        
        resultados = {
            "success": True,
            "eliminadas": 0,
            "agregadas": 0,
            "detalles": []
        }
        
        # 3. ELIMINAR cuotas (y sus pagos asociados)
        for id_cuota in ids_a_eliminar:
            id_relacion = id_alumno_cuota_actual[id_cuota]
            
            # Eliminar pagos asociados (CASCADE en BD no está configurado, lo hacemos manual)
            cur.execute("DELETE FROM pago WHERE id_alumno_cuota = %s", (id_relacion,))
            pagos_eliminados = cur.rowcount
            
            # Eliminar relación alumno_cuota
            cur.execute("DELETE FROM alumno_cuota WHERE id = %s", (id_relacion,))
            
            resultados["eliminadas"] += 1
            resultados["detalles"].append({
                "accion": "eliminar",
                "id_cuota": id_cuota,
                "pagos_eliminados": pagos_eliminados
            })
            print(f"   🗑️ Eliminada cuota ID {id_cuota} con {pagos_eliminados} pagos")
        
        # 4. AGREGAR nuevas cuotas
        mes_actual = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        
        for id_cuota in ids_a_agregar:
            # Insertar en alumno_cuota
            cur.execute("""
                INSERT INTO alumno_cuota (id_alumno, id_cuota)
                VALUES (%s, %s) RETURNING id
            """, (id_alumno, id_cuota))
            id_alumno_cuota = cur.fetchone()[0]
            
            # Obtener el descuento que el alumno tenía (buscamos en pagos existentes de otras cuotas)
            cur.execute("""
                SELECT descuento FROM pago pg
                JOIN alumno_cuota ac ON pg.id_alumno_cuota = ac.id
                WHERE ac.id_alumno = %s AND pg.descuento IS NOT NULL
                LIMIT 1
            """, (id_alumno,))
            descuento_existente = cur.fetchone()
            descuento = descuento_existente[0] if descuento_existente else 0
            
            # Crear pago inicial pendiente para esta cuota
            cur.execute("""
                INSERT INTO pago (id_alumno_cuota, mes_correspondiente, descuento, pagado_bool, fecha_pago, metodo_pago)
                VALUES (%s, %s, %s, FALSE, NULL, NULL)
            """, (id_alumno_cuota, mes_actual, descuento))
            
            resultados["agregadas"] += 1
            resultados["detalles"].append({
                "accion": "agregar",
                "id_cuota": id_cuota,
                "descuento_aplicado": descuento
            })
            print(f"   ✨ Agregada cuota ID {id_cuota} con descuento {descuento}%")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Actualización completada: {resultados['eliminadas']} eliminadas, {resultados['agregadas']} agregadas")
        return resultados
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"❌ Error actualizando cuotas: {e}")
        return {"success": False, "message": str(e), "eliminadas": 0, "agregadas": 0, "detalles": []}