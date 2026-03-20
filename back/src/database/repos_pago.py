from database.connection import get_connection
from models.pago import Pago
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict

class ErrorGuardarPago(Exception):
    """Excepción personalizada para errores al guardar pago"""
    pass

def guardar_pago(pago: Pago) -> int:
    """
    Guarda un nuevo pago en la base de datos.
    Retorna el ID generado.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarPago("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que la relación alumno-cuota existe
        cur.execute("SELECT id FROM alumno_cuota WHERE id = %s", (pago.id_alumno_cuota,))
        if not cur.fetchone():
            raise ErrorGuardarPago(f"No existe una relación alumno-cuota con ID {pago.id_alumno_cuota}")
        
        # Insertar el pago con el campo descuento
        query = """
            INSERT INTO pago (id_alumno_cuota, fecha_pago, pagado_bool, mes_correspondiente, descuento, metodo_pago)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query, (
            pago.id_alumno_cuota,
            pago.fecha_pago,
            pago.pagado_bool,
            pago.mes_correspondiente,
            pago.descuento,
            pago.metodo_pago
        ))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Pago guardado correctamente con ID: {id_generado}")
        print(f"   ID Alumno-Cuota: {pago.id_alumno_cuota}")
        print(f"   Mes correspondiente: {pago.mes_correspondiente}")
        print(f"   Descuento: {pago.descuento}%")
        print(f"   Pagado: {pago.pagado_bool}")
        if pago.pagado_bool:
            print(f"   Fecha pago: {pago.fecha_pago}")
            print(f"   Método: {pago.metodo_pago}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        if "foreign key" in str(e).lower():
            raise ErrorGuardarPago(f"La relación alumno-cuota {pago.id_alumno_cuota} no existe")
        elif "not null" in str(e).lower():
            raise ErrorGuardarPago(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarPago(f"Error en la base de datos: {str(e)}")


def actualizar_pago(id_pago: int, fecha_pago: datetime, metodo_pago: str) -> None:
    """
    Actualiza un pago existente (cuando se paga).
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarPago("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        query = """
            UPDATE pago 
            SET pagado_bool = TRUE, 
                fecha_pago = %s, 
                metodo_pago = %s
            WHERE id = %s AND pagado_bool = FALSE
            RETURNING id_alumno_cuota, mes_correspondiente, descuento
        """
        cur.execute(query, (fecha_pago, metodo_pago, id_pago))
        
        result = cur.fetchone()
        if not result:
            raise ErrorGuardarPago(f"No se encontró un pago pendiente con ID {id_pago}")
        
        id_alumno_cuota = result[0]
        mes_correspondiente = result[1]
        descuento = result[2]
        
        # Crear el próximo pago (mes siguiente)
        proximo_mes = mes_correspondiente + relativedelta(months=1)
        
        nuevo_pago = Pago(
            id_alumno_cuota=id_alumno_cuota,
            mes_correspondiente=proximo_mes,
            descuento=descuento,  # Mantener el mismo descuento
            pagado_bool=False,
            fecha_pago=None,
            metodo_pago=None
        )
        
        guardar_pago(nuevo_pago)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Pago ID {id_pago} marcado como pagado")
        print(f"✅ Nuevo pago creado para {proximo_mes}")
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        raise ErrorGuardarPago(f"Error al actualizar pago: {str(e)}")
    
def obtener_pagos_pendientes_agrupados() -> List[Dict]:
    """
    Obtiene los pagos pendientes agrupados por alumno y mes
    Solo muestra los pagos con mes_correspondiente <= mes actual
    Retorna lista con: alumno_id, nombre, mes, total_a_pagar, tiene_descuento
    """
    conn = get_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        query = """
            SELECT 
                a.id AS alumno_id,
                p.nomb_apel AS nombre_alumno,
                pg.mes_correspondiente,
                SUM(c.precio_cuota * (1 - pg.descuento / 100)) AS total_a_pagar,
                MAX(CASE WHEN pg.descuento > 0 THEN 1 ELSE 0 END) AS tiene_descuento
            FROM persona p
            JOIN alumno a ON p.id = a.id_persona
            JOIN alumno_cuota ac ON a.id = ac.id_alumno
            JOIN cuota c ON ac.id_cuota = c.id
            JOIN pago pg ON ac.id = pg.id_alumno_cuota
            WHERE pg.pagado_bool = FALSE
              AND pg.mes_correspondiente <= DATE_TRUNC('month', CURRENT_DATE)
            GROUP BY a.id, p.nomb_apel, pg.mes_correspondiente
            ORDER BY p.nomb_apel, pg.mes_correspondiente
        """
        cur.execute(query)
        
        resultados = []
        for row in cur.fetchall():
            resultados.append({
                'alumno_id': row[0],
                'nombre_alumno': row[1],
                'mes_correspondiente': row[2].isoformat(),
                'total_a_pagar': float(row[3]),
                'tiene_descuento': row[4] == 1
            })
        
        cur.close()
        conn.close()
        print(f"✅ Se encontraron {len(resultados)} pagos pendientes (mes <= actual)")
        return resultados
        
    except Exception as e:
        print(f"❌ Error al obtener pagos pendientes: {e}")
        if conn:
            conn.close()
        return []
    

def registrar_pago_adelantado(alumno_id: int, meses_a_pagar: int, metodo_pago: str, mantener_descuento: bool = True) -> Dict:
    """
    Registra el pago de uno o más meses para un alumno
    """
    conn = get_connection()
    if not conn:
        raise Exception("No se pudo conectar a la base de datos")

    cur = conn.cursor()

    print("\n🔍 [FUNCION] Parámetros recibidos:")
    print(f"   alumno_id: {alumno_id}")
    print(f"   meses_a_pagar: {meses_a_pagar}")
    print(f"   metodo_pago: {metodo_pago}")
    print(f"   mantener_descuento: {mantener_descuento}")
    
    # Asegurar que metodo_pago es string
    if metodo_pago is None:
        metodo_pago = "No especificado"
    else:
        metodo_pago = str(metodo_pago)

    try:
        # Asegurar que mantener_descuento es bool
        mantener_descuento = bool(mantener_descuento)
        
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        # Fecha actual (primer día del mes actual)
        fecha_actual = date.today().replace(day=1)
        
        print(f"\n🔍 Fecha actual: {fecha_actual}")

        # ==============================
        # 1. Obtener pagos pendientes del alumno
        # ==============================
        query = """
            SELECT 
                pg.id,
                pg.id_alumno_cuota,
                pg.mes_correspondiente,
                pg.descuento,
                c.precio_cuota,
                c.nombre as nombre_cuota
            FROM pago pg
            JOIN alumno_cuota ac ON pg.id_alumno_cuota = ac.id
            JOIN cuota c ON ac.id_cuota = c.id
            WHERE ac.id_alumno = %s AND pg.pagado_bool = FALSE
            ORDER BY pg.mes_correspondiente ASC
        """
        cur.execute(query, (alumno_id,))
        pagos_pendientes = cur.fetchall()

        if not pagos_pendientes:
            raise Exception("No hay pagos pendientes para este alumno")

        # ==============================
        # 2. Agrupar por mes y obtener el mes más antiguo pendiente
        # ==============================
        from collections import defaultdict
        pagos_por_mes = defaultdict(list)
        
        for pago in pagos_pendientes:
            pagos_por_mes[pago[2]].append(pago)
        
        meses_ordenados = sorted(pagos_por_mes.keys())
        
        # El primer mes pendiente es el que debemos pagar
        primer_mes_pendiente = meses_ordenados[0]
        print(f"🔍 Primer mes pendiente: {primer_mes_pendiente}")
        
        # ==============================
        # 3. Determinar descuento original y nuevo
        # ==============================
        descuento_original = float(pagos_pendientes[0][3]) if pagos_pendientes[0][3] else 0
        
        if mantener_descuento:
            nuevo_descuento = descuento_original
            print(f"🔍 Manteniendo descuento: {nuevo_descuento}%")
        else:
            nuevo_descuento = 0
            print(f"🔍 ELIMINANDO descuento: {nuevo_descuento}%")

        total_pagado = 0.0
        meses_procesados = 0
        
        # ==============================
        # 4. PAGAR MESES PENDIENTES (desde el más antiguo)
        # ==============================
        # Solo pagamos los meses que están dentro de los meses_a_pagar
        meses_a_pagar_restantes = meses_a_pagar
        
        for mes in meses_ordenados:
            if meses_a_pagar_restantes <= 0:
                break
                
            for pago in pagos_por_mes[mes]:
                pago_id = pago[0]
                precio_cuota = float(pago[4])
                nombre_cuota = pago[5]
                descuento_actual = float(pago[3]) if pago[3] else 0
                
                monto_final = precio_cuota * (1 - descuento_actual / 100)
                
                # Marcar como pagado
                cur.execute("""
                    UPDATE pago
                    SET pagado_bool = TRUE,
                        fecha_pago = NOW(),
                        metodo_pago = %s
                    WHERE id = %s
                """, (metodo_pago, pago_id))
                
                total_pagado += monto_final
                print(f"   ✅ Pagado: {nombre_cuota} - {mes} - ${monto_final:.2f}")
            
            meses_procesados += 1
            meses_a_pagar_restantes -= 1
        
        # ==============================
        # 5. Obtener todas las cuotas del alumno
        # ==============================
        cur.execute("""
            SELECT ac.id, c.precio_cuota, c.nombre
            FROM alumno_cuota ac
            JOIN cuota c ON ac.id_cuota = c.id
            WHERE ac.id_alumno = %s
        """, (alumno_id,))
        cuotas_alumno = cur.fetchall()
        
        # ==============================
        # 6. GENERAR PAGOS ADELANTADOS (pagados) si quedan meses por pagar
        # ==============================
        if meses_a_pagar_restantes > 0:
            # El último mes que procesamos
            if meses_ordenados:
                ultimo_mes_procesado = meses_ordenados[meses_procesados - 1]
            else:
                ultimo_mes_procesado = primer_mes_pendiente
            
            print(f"🔍 Último mes procesado: {ultimo_mes_procesado}")
            
            for i in range(1, meses_a_pagar_restantes + 1):
                nuevo_mes = ultimo_mes_procesado + relativedelta(months=i)
                
                for cuota_id, precio_cuota, nombre_cuota in cuotas_alumno:
                    precio_cuota_float = float(precio_cuota)
                    monto_final = precio_cuota_float * (1 - nuevo_descuento / 100)
                    
                    cur.execute("""
                        INSERT INTO pago (id_alumno_cuota, mes_correspondiente, descuento, pagado_bool, fecha_pago, metodo_pago)
                        VALUES (%s, %s, %s, TRUE, NOW(), %s)
                        RETURNING id
                    """, (cuota_id, nuevo_mes, nuevo_descuento, metodo_pago))
                    
                    nuevo_id = cur.fetchone()[0]
                    total_pagado += monto_final
                    print(f"   ✅ Adelantado pagado: {nombre_cuota} - {nuevo_mes} - ${monto_final:.2f}")
            
            meses_procesados += meses_a_pagar_restantes
        
        # ==============================
        # 7. GENERAR PRÓXIMO PAGO PENDIENTE
        # ==============================
        # Calculamos el próximo mes basado en el último mes que se pagó
        if meses_ordenados:
            # Buscamos el último mes que se pagó (puede ser uno de los originales o uno adelantado)
            ultimo_mes_pagado = None
            
            # Primero, vemos cuál fue el último mes procesado en los pagos originales
            if meses_procesados <= len(meses_ordenados):
                ultimo_mes_pagado = meses_ordenados[meses_procesados - 1]
            else:
                # Si se pagaron más meses de los que había pendientes, usamos el último adelantado
                ultimo_mes_pagado = ultimo_mes_procesado + relativedelta(months=meses_a_pagar_restantes)
            
            siguiente_mes = ultimo_mes_pagado + relativedelta(months=1)
        else:
            siguiente_mes = fecha_actual
        
        print(f"🔍 Siguiente mes pendiente a generar: {siguiente_mes}")
        
        for cuota_id, precio_cuota, nombre_cuota in cuotas_alumno:
            precio_cuota_float = float(precio_cuota)
            monto_pendiente = precio_cuota_float * (1 - nuevo_descuento / 100)
            
            cur.execute("""
                INSERT INTO pago (id_alumno_cuota, mes_correspondiente, descuento, pagado_bool)
                VALUES (%s, %s, %s, FALSE)
                RETURNING id
            """, (cuota_id, siguiente_mes, nuevo_descuento))
            
            nuevo_id = cur.fetchone()[0]
            print(f"   ⏳ Nuevo pendiente: {nombre_cuota} - {siguiente_mes} - ${monto_pendiente:.2f}")

        conn.commit()

        resultado = {
            "meses_procesados": meses_procesados,
            "total_pagado": total_pagado,
            "descuento_mantenido": mantener_descuento,
            "nuevo_descuento": nuevo_descuento
        }
        
        print(f"\n✅ Pago registrado exitosamente:")
        print(f"   Meses pagados: {meses_procesados}")
        print(f"   Total pagado: ${total_pagado:.2f}")
        print(f"   Descuento mantenido: {mantener_descuento}")
        print(f"   Nuevo descuento para futuros: {nuevo_descuento}%")
        
        return resultado

    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise e

    finally:
        cur.close()
        conn.close()