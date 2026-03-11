# src/database/repos_pago.py
from database.connection import get_connection
from models.pago import Pago
from datetime import datetime

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
        
        # Insertar el pago
        query = """
            INSERT INTO pago (id_alumno_cuota, fecha_pago, pagado_bool, mes_correspondiente, monto, metodo_pago)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        cur.execute(query, (
            pago.id_alumno_cuota,
            pago.fecha_pago or datetime.now(),  # Si no viene fecha, usa la actual
            pago.pagado_bool,
            pago.mes_correspondiente,
            pago.monto,
            pago.metodo_pago
        ))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Pago guardado correctamente con ID: {id_generado}")
        print(f"   ID Alumno-Cuota: {pago.id_alumno_cuota}")
        print(f"   Mes correspondiente: {pago.mes_correspondiente}")
        print(f"   Monto: ${pago.monto}")
        print(f"   Método: {pago.metodo_pago}")
        print(f"   Pagado: {pago.pagado_bool}")
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