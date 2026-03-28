import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Ajuste de rutas para encontrar el módulo database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.repos_pago import guardar_pago, actualizar_pago, obtener_pagos_pendientes_agrupados, ErrorGuardarPago
from database.connection import get_connection
from models.pago import Pago # Asegúrate de que el modelo Pago acepte estos argumentos

def preparar_datos_para_pagos():
    conn = get_connection()
    cur = conn.cursor()
    try:
        print("\n--- 🧹 Limpiando base para prueba de pagos ---")
        cur.execute("TRUNCATE TABLE persona, cuota, horario RESTART IDENTITY CASCADE;")
        
        print("--- 📝 Creando datos maestros (Alumno, Profe, Clase, Horario) ---")
        # 1. Alumno
        cur.execute("INSERT INTO persona (dni, nomb_apel) VALUES ('100', 'Mateo Pagador') RETURNING id;")
        id_per_alu = cur.fetchone()[0]
        cur.execute("INSERT INTO alumno (id_persona) VALUES (%s) RETURNING id;", (id_per_alu,))
        id_alu = cur.fetchone()[0]

        # 2. Profesor y Clase
        cur.execute("INSERT INTO persona (dni, nomb_apel) VALUES ('200', 'Santi Profe') RETURNING id;")
        id_per_prof = cur.fetchone()[0]
        cur.execute("INSERT INTO profesor (id_persona) VALUES (%s) RETURNING id;", (id_per_prof,))
        id_prof = cur.fetchone()[0]
        cur.execute("INSERT INTO clase (nombre_clase, id_profesor, duracion) VALUES ('Piano', %s, 60) RETURNING id;", (id_prof,))
        id_clase = cur.fetchone()[0]

        # 3. Horario
        cur.execute("INSERT INTO horario (dia, hora_init) VALUES ('Lunes', '10:00:00') RETURNING id;")
        id_hor = cur.fetchone()[0]

        # 4. Inscripción (CON DESCUENTO DEL 20%)
        cur.execute("""
            INSERT INTO alumno_clase (id_alumno, id_clase, id_horario, descuento) 
            VALUES (%s, %s, %s, 20.00) RETURNING id;
        """, (id_alu, id_clase, id_hor))
        id_ins_ac = cur.fetchone()[0]

        # 5. CUOTA (Vital para tu query de pendientes)
        print("--- 💰 Creando Cuota del Alumno ---")
        cur.execute("INSERT INTO cuota (nombre, precio_cuota) VALUES ('Mensualidad Piano', 5000.00) RETURNING id;")
        id_cuota = cur.fetchone()[0]
        cur.execute("INSERT INTO alumno_cuota (id_alumno, id_cuota) VALUES (%s, %s);", (id_alu, id_cuota))

        conn.commit()
        print(f"✅ Entorno listo. ID Inscripción: {id_ins_ac}")
        return id_ins_ac
    except Exception as e:
        conn.rollback()
        print(f"❌ Error preparando datos: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 INICIANDO TEST DE REPOSITORIO DE PAGOS")
    
    id_inscripcion = preparar_datos_para_pagos()

    # TEST 1: Crear un pago inicial (Deuda de Marzo)
    print("\n--- 🧪 TEST 1: Creando Deuda Inicial (Marzo 2026) ---")
    mes_marzo = date(2026, 3, 1)
    pago_marzo = Pago(
        id_alumno_clase=id_inscripcion,
        mes_correspondiente=mes_marzo,
        pagado_bool=False,
        fecha_pago=None,
        metodo_pago=None
    )
    
    try:
        id_pago_generado = guardar_pago(pago_marzo)
        print(f"✅ Pago pendiente creado con ID: {id_pago_generado}")
    except ErrorGuardarPago as e:
        print(f"❌ Error al guardar: {e}")

    # TEST 2: Obtener pendientes (Aquí probamos tu SQL complejo)
    print("\n--- 🧪 TEST 2: Consultando Pagos Pendientes ---")
    pendientes = obtener_pagos_pendientes_agrupados()
    if pendientes:
        p = pendientes[0]
        print(f"📋 Pendiente encontrado:")
        print(f"   Alumno: {p['nombre_alumno']} | Mes: {p['mes_correspondiente']}")
        print(f"   Clase: {p['nombre_clase']} | Cuota: {p['nombre_cuota']}")
        print(f"   Precio Base: ${p['price_base'] if 'price_base' in p else p.get('precio_base')} | Descuento: {p['descuento']}%")
        print(f"   💰 TOTAL A PAGAR: ${p['total_a_pagar']}")
    else:
        print("⚠️ No se encontraron pendientes. Revisa los JOINs de la cuota.")

    # TEST 3: Actualizar pago (Simular que el alumno paga marzo)
    print("\n--- 🧪 TEST 3: Pagando Marzo y Generando Abril ---")
    try:
        fecha_hoy = datetime.now()
        actualizar_pago(
            id_pago=id_pago_generado, 
            fecha_pago=fecha_hoy, 
            metodo_pago="Transferencia"
        )
        print("✅ Marzo marcado como pagado. Se debería haber creado Abril automáticamente.")
    except ErrorGuardarPago as e:
        print(f"❌ Error al actualizar: {e}")

    # TEST 4: Verificar que existe la deuda de Abril (Auto-generada)
    print("\n--- 🧪 TEST 4: Verificando Deuda de Abril (Recursividad) ---")
    pendientes_final = obtener_pagos_pendientes_agrupados()
    found_abril = False
    for pf in pendientes_final:
        if "2026-04-01" in pf['mes_correspondiente']:
            print(f"✅ ¡Genial! Se encontró la deuda automática de Abril para {pf['nombre_alumno']}")
            found_abril = True
    
    if not found_abril:
        print("❌ Error: No se generó automáticamente el pago de Abril.")

    print("\n🏁 TEST FINALIZADO")