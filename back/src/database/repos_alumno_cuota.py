# src/database/repos_alumno_cuota.py
from database.connection import get_connection

class ErrorGuardarAlumnoCuota(Exception):
    """Excepción personalizada para errores al guardar alumno-cuota"""
    pass

def guardar_alumno_cuota(id_alumno: int, id_cuota: int) -> int:
    """
    Asocia un alumno con una cuota.
    Retorna el ID de la relación creada.
    """
    print(f"   🔍 [repos_alumno_cuota] guardar_alumno_cuota({id_alumno}, {id_cuota})")
    
    conn = get_connection()
    if not conn:
        print(f"   ❌ No se pudo conectar a la base de datos")
        raise ErrorGuardarAlumnoCuota("No se pudo conectar a la base de datos")
    
    try:
        cur = conn.cursor()
        
        # Verificar que el alumno existe
        print(f"   Verificando existencia del alumno {id_alumno}...")
        cur.execute("SELECT id FROM alumno WHERE id = %s", (id_alumno,))
        alumno_exists = cur.fetchone()
        if not alumno_exists:
            print(f"   ❌ No existe un alumno con ID {id_alumno}")
            raise ErrorGuardarAlumnoCuota(f"No existe un alumno con ID {id_alumno}")
        print(f"   ✅ Alumno {id_alumno} existe")
        
        # Verificar que la cuota existe
        print(f"   Verificando existencia de la cuota {id_cuota}...")
        cur.execute("SELECT id, nombre FROM cuota WHERE id = %s", (id_cuota,))
        cuota_data = cur.fetchone()
        if not cuota_data:
            print(f"   ❌ No existe una cuota con ID {id_cuota}")
            raise ErrorGuardarAlumnoCuota(f"No existe una cuota con ID {id_cuota}")
        print(f"   ✅ Cuota {id_cuota} existe: {cuota_data[1]}")
        
        # Insertar la relación
        print(f"   Insertando relación en alumno_cuota...")
        query = """
            INSERT INTO alumno_cuota (id_alumno, id_cuota)
            VALUES (%s, %s) RETURNING id;
        """
        cur.execute(query, (id_alumno, id_cuota))
        
        id_generado = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"   ✅ Relación alumno-cuota guardada correctamente con ID: {id_generado}")
        print(f"   Alumno ID: {id_alumno} - Cuota ID: {id_cuota}")
        return id_generado
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        
        print(f"   ❌ Error en guardar_alumno_cuota: {e}")
        
        if "duplicate key" in str(e).lower() or "ak_alumno_cuota" in str(e):
            raise ErrorGuardarAlumnoCuota(f"El alumno {id_alumno} ya tiene asignada la cuota {id_cuota}")
        elif "foreign key" in str(e).lower():
            raise ErrorGuardarAlumnoCuota(f"Error de referencia: {str(e)}")
        else:
            raise ErrorGuardarAlumnoCuota(f"Error en la base de datos: {str(e)}")

# src/database/repos_alumno_cuota.py
from database.connection import get_connection
from typing import List, Dict

def obtener_cuotas_por_alumno(id_alumno: int) -> List[Dict]:
    """
    Obtiene todas las cuotas asociadas a un alumno
    Retorna lista de cuotas con información de la cuota y los pagos
    """
    print(f"🔍 Buscando cuotas para alumno ID: {id_alumno}")
    conn = get_connection()
    cuotas = []
    
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return cuotas
    
    try:
        cursor = conn.cursor()
        
        query = """
            SELECT 
                ac.id as alumno_cuota_id,
                ac.id_alumno,
                ac.id_cuota,
                c.id as cuota_id,
                c.nombre as cuota_nombre,
                c.precio_cuota as cuota_precio_base,
                p.id as pago_id,
                p.fecha_pago,
                p.pagado_bool,
                p.mes_correspondiente,
                p.metodo_pago
            FROM alumno_cuota ac
            JOIN cuota c ON ac.id_cuota = c.id
            LEFT JOIN pago p ON ac.id = p.id_alumno_cuota
            WHERE ac.id_alumno = %s
            ORDER BY c.nombre, p.mes_correspondiente
        """
        
        cursor.execute(query, (id_alumno,))
        rows = cursor.fetchall()
        
        print(f"📊 Registros encontrados: {len(rows)}")
        
        # Diccionario para agrupar cuotas por id_cuota
        cuotas_dict = {}
        
        for row in rows:
            id_cuota = row[2]  # id_cuota
            cuota_nombre = row[4]  # cuota_nombre
            
            # Si no existe la cuota en el diccionario, la creamos
            if id_cuota not in cuotas_dict:
                cuotas_dict[id_cuota] = {
                    'id_alumno_cuota': row[0],
                    'id_cuota': id_cuota,
                    'nombre': cuota_nombre,
                    'precio_base': float(row[5]) if row[5] else 0,
                    'pagos': []
                }
            
            # Si hay un pago asociado, lo agregamos
            if row[6]:  # pago_id existe
                cuotas_dict[id_cuota]['pagos'].append({
                    'id_pago': row[6],
                    'fecha_pago': row[7].isoformat() if row[7] else None,
                    'pagado_bool': row[8] if row[8] is not None else False,
                    'mes_correspondiente': row[9].strftime('%Y-%m') if row[9] else None,
                    'metodo_pago': row[10]
                })
        
        # Convertir el diccionario a lista
        cuotas = list(cuotas_dict.values())
        
        # Ordenar cuotas por nombre
        cuotas.sort(key=lambda x: x['nombre'])
        
        # Para cada cuota, ordenar pagos por mes
        for cuota in cuotas:
            if cuota['pagos']:
                cuota['pagos'].sort(key=lambda x: x['mes_correspondiente'] if x['mes_correspondiente'] else '')
        
        cursor.close()
        conn.close()
        
        print(f"✅ Encontradas {len(cuotas)} cuotas para alumno {id_alumno}")
        return cuotas
        
    except Exception as e:
        print(f"❌ Error al obtener cuotas del alumno: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return []