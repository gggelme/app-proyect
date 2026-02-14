from database.connection import get_connection
from datetime import date

def calcular_proximo_vencimiento(fecha_actual):
    if fecha_actual.month == 12:
        return date(fecha_actual.year + 1, 1, 10)
    else:
        return date(fecha_actual.year, fecha_actual.month + 1, 10)

def crear_pago_inicial_por_inscripcion(cur, id_alumno, id_instrumento):
    """Crea el pago usando la relación compuesta."""
    vencimiento = calcular_proximo_vencimiento(date.today())
    query = """
        INSERT INTO PAGO (id_alumno, id_instrumento, fecha_vencimiento, estado)
        VALUES (%s, %s, %s, 'PENDIENTE');
    """
    cur.execute(query, (id_alumno, id_instrumento, vencimiento))

def registrar_pago_y_generar_proximo(id_pago):
    """Marca como pagado y crea el siguiente para el MISMO instrumento."""
    conn = get_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        # 1. Obtener datos (ahora con id_instrumento)
        cur.execute("SELECT id_alumno, id_instrumento, fecha_vencimiento FROM PAGO WHERE id = %s", (id_pago,))
        res = cur.fetchone()
        if not res: return False
        
        id_alumno, id_inst, venc_actual = res

        # 2. Pagar
        cur.execute("UPDATE PAGO SET estado = 'PAGADO', fecha_pago = %s WHERE id = %s", (date.today(), id_pago))

        # 3. Generar el del mes que viene para esa inscripción
        venc_siguiente = calcular_proximo_vencimiento(venc_actual)
        cur.execute("""
            INSERT INTO PAGO (id_alumno, id_instrumento, fecha_vencimiento, estado)
            VALUES (%s, %s, %s, 'PENDIENTE')
        """, (id_alumno, id_inst, venc_siguiente))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        if conn: conn.rollback()
        return False

def obtener_pagos_alumno(id_alumno):
    """Muestra todos los pagos, indicando de qué instrumento son."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
        SELECT pa.id, i.nombre, pa.fecha_vencimiento, pa.estado 
        FROM PAGO pa
        JOIN INSTRUMENTO i ON pa.id_instrumento = i.id
        WHERE pa.id_alumno = %s 
        ORDER BY pa.fecha_vencimiento;
    """
    cur.execute(query, (id_alumno,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows