# src/database/repos_pago.py
from database.connection import get_connection
from models.pago import Pago
from models.alumno_clase import AlumnoClase
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Optional

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
        
        # Verificar que la inscripción alumno-clase existe
        cur.execute("SELECT id FROM alumno_clase WHERE id = %s", (pago.id_alumno_clase,))
        if not cur.fetchone():
            raise ErrorGuardarPago(f"No existe una inscripción alumno-clase con ID {pago.id_alumno_clase}")
        
        # Insertar el pago (ya no tiene descuento)
        query = """
            INSERT INTO pago (id_alumno_clase, fecha_pago, pagado_bool, mes_correspondiente, metodo_pago)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query, (
            pago.id_alumno_clase,
            pago.fecha_pago,
            pago.pagado_bool,
            pago.mes_correspondiente,
            pago.metodo_pago
        ))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Pago guardado correctamente con ID: {id_generado}")
        print(f"   ID Inscripción: {pago.id_alumno_clase}")
        print(f"   Mes correspondiente: {pago.mes_correspondiente}")
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
            raise ErrorGuardarPago(f"La inscripción {pago.id_alumno_clase} no existe")
        elif "not null" in str(e).lower():
            raise ErrorGuardarPago(f"Falta un campo obligatorio: {str(e)}")
        else:
            raise ErrorGuardarPago(f"Error en la base de datos: {str(e)}")


def actualizar_pago(id_pago: int, fecha_pago: datetime, metodo_pago: str) -> None:
    """
    Actualiza un pago existente (cuando se paga) y crea automáticamente el próximo mes.
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarPago("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Actualizar el pago y obtener información necesaria
        query = """
            UPDATE pago 
            SET pagado_bool = TRUE, 
                fecha_pago = %s, 
                metodo_pago = %s
            WHERE id = %s AND pagado_bool = FALSE
            RETURNING id_alumno_clase, mes_correspondiente
        """
        cur.execute(query, (fecha_pago, metodo_pago, id_pago))
        
        result = cur.fetchone()
        if not result:
            raise ErrorGuardarPago(f"No se encontró un pago pendiente con ID {id_pago}")
        
        id_alumno_clase = result[0]
        mes_correspondiente = result[1]
        
        # Crear el próximo pago (mes siguiente)
        proximo_mes = mes_correspondiente + relativedelta(months=1)
        
        # Obtener el descuento desde alumno_clase (solo para referencia, no se guarda en pago)
        cur.execute("SELECT descuento FROM alumno_clase WHERE id = %s", (id_alumno_clase,))
        descuento_row = cur.fetchone()
        descuento = descuento_row[0] if descuento_row else None
        
        nuevo_pago = Pago(
            id_alumno_clase=id_alumno_clase,
            mes_correspondiente=proximo_mes,
            pagado_bool=False,
            fecha_pago=None,
            metodo_pago=None
        )
        
        guardar_pago(nuevo_pago)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Pago ID {id_pago} marcado como pagado")
        if descuento:
            print(f"   Descuento aplicado: {descuento}%")
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
    
    Ahora cada pago está asociado a una inscripción (alumno_clase) 
    que a su vez está asociada a una cuota específica.
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
                c.precio_cuota AS precio_base,
                ac.descuento,
                CASE 
                    WHEN ac.descuento IS NOT NULL AND ac.descuento > 0 
                    THEN c.precio_cuota * (1 - ac.descuento / 100)
                    ELSE c.precio_cuota
                END AS total_a_pagar,
                CASE WHEN ac.descuento > 0 THEN 1 ELSE 0 END AS tiene_descuento,
                c.nombre AS nombre_cuota,
                cl.nombre_clase AS nombre_clase
            FROM persona p
            JOIN alumno a ON p.id = a.id_persona
            JOIN alumno_clase ac ON a.id = ac.id_alumno
            JOIN clase cl ON ac.id_clase = cl.id
            JOIN alumno_cuota acu ON a.id = acu.id_alumno
            JOIN cuota c ON acu.id_cuota = c.id
            JOIN pago pg ON ac.id = pg.id_alumno_clase
            WHERE pg.pagado_bool = FALSE
              AND pg.mes_correspondiente <= DATE_TRUNC('month', CURRENT_DATE)
            GROUP BY a.id, p.nomb_apel, pg.mes_correspondiente, c.precio_cuota, ac.descuento, c.nombre, cl.nombre_clase
            ORDER BY p.nomb_apel, pg.mes_correspondiente
        """
        cur.execute(query)
        
        resultados = []
        for row in cur.fetchall():
            resultados.append({
                'alumno_id': row[0],
                'nombre_alumno': row[1],
                'mes_correspondiente': row[2].isoformat(),
                'precio_base': float(row[3]),
                'descuento': float(row[4]) if row[4] else None,
                'total_a_pagar': float(row[5]),
                'tiene_descuento': row[6] == 1,
                'nombre_cuota': row[7],
                'nombre_clase': row[8]
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