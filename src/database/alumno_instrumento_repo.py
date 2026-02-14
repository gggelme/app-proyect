from database.connection import get_connection

def asignar_instrumento_a_alumno(id_alumno, id_instrumento, cant_horas, descuento):
    conn = get_connection()
    if not conn: return False
    
    try:
        cur = conn.cursor()
        # 1. Crear la inscripción
        query_ins = """
            INSERT INTO ALUMNO_INSTRUMENTO (id_alumno, id_instrumento, cant_horas, descuento)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """
        cur.execute(query_ins, (id_alumno, id_instrumento, cant_horas, descuento))
        
        # 2. Si se insertó (no era duplicado), disparamos el pago inicial
        if cur.rowcount > 0:
            from database.pago_repo import crear_pago_inicial_por_inscripcion
            crear_pago_inicial_por_inscripcion(cur, id_alumno, id_instrumento)
            print(f"✅ Alumno {id_alumno} inscripto en instrumento {id_instrumento} y pago generado.")
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        if conn: conn.rollback()
        print(f"❌ Error en inscripción y pago: {e}")
        return False