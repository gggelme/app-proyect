from database.connection import get_connection
from database.repos_alumno_cuota import guardar_alumno_cuota, ErrorGuardarAlumnoCuota
from database.repos_pago import guardar_pago, ErrorGuardarPago
from models.pago import Pago
from datetime import date
from typing import List, Dict

class ErrorGuardarInscripcionCuotas(Exception):
    """Excepción personalizada para errores al guardar inscripción con cuotas"""
    pass

def guardar_inscripcion_completa_con_cuotas(
    id_alumno: int, 
    ids_cuotas: List[int], 
    porcentaje_descuento: float
) -> Dict:
    """
    Guarda la inscripción completa:
    1. Asocia el alumno con cada cuota seleccionada (tabla alumno_cuota)
    2. Genera un pago no pagado para cada cuota con el mes correspondiente
    
    Args:
        id_alumno: ID del alumno creado
        ids_cuotas: Lista de IDs de cuotas seleccionadas
        porcentaje_descuento: Porcentaje de descuento a aplicar (0-100)
    
    Returns:
        Dict con resultados de la operación
    """
    conn = get_connection()
    if not conn:
        raise ErrorGuardarInscripcionCuotas("No se pudo conectar a la base de datos")
    
    resultados = {
        "alumno_id": id_alumno,
        "cuotas_asociadas": [],
        "pagos_generados": [],
        "errores": []
    }
    
    try:
        # Obtener la fecha actual para el mes correspondiente (primer día del mes)
        hoy = date.today()
        mes_correspondiente = date(hoy.year, hoy.month, 1)
        
        # Para cada cuota seleccionada
        for id_cuota in ids_cuotas:
            try:
                # 1. Guardar relación alumno-cuota
                id_alumno_cuota = guardar_alumno_cuota(id_alumno, id_cuota)
                resultados["cuotas_asociadas"].append({
                    "id_cuota": id_cuota,
                    "id_alumno_cuota": id_alumno_cuota
                })
                
                # 2. Obtener el precio de la cuota para mostrar en el log
                cur = conn.cursor()
                cur.execute("SELECT nombre, precio_cuota FROM cuota WHERE id = %s", (id_cuota,))
                cuota_data = cur.fetchone()
                nombre_cuota = cuota_data[0]
                precio_cuota = float(cuota_data[1])
                cur.close()
                
                # Calcular el monto final con descuento
                monto_final = precio_cuota * (1 - porcentaje_descuento / 100)
                
                # 3. Crear el pago no pagado
                pago = Pago(
                    id_alumno_cuota=id_alumno_cuota,
                    mes_correspondiente=mes_correspondiente,
                    descuento=porcentaje_descuento,  # Guardamos el porcentaje
                    pagado_bool=False,
                    fecha_pago=None,
                    metodo_pago=None
                )
                
                id_pago = guardar_pago(pago)
                resultados["pagos_generados"].append({
                    "id_pago": id_pago,
                    "id_alumno_cuota": id_alumno_cuota,
                    "id_cuota": id_cuota,
                    "nombre_cuota": nombre_cuota,
                    "precio_original": precio_cuota,
                    "descuento_porcentaje": porcentaje_descuento,
                    "monto_final": monto_final,
                    "mes_correspondiente": mes_correspondiente.isoformat(),
                    "pagado": False
                })
                
                print(f"✅ Cuota '{nombre_cuota}' asociada al alumno {id_alumno}")
                print(f"   Precio original: ${precio_cuota:.2f}")
                print(f"   Descuento: {porcentaje_descuento}% -> ${monto_final:.2f}")
                print(f"   Pago generado para {mes_correspondiente.strftime('%B %Y')}")
                
            except (ErrorGuardarAlumnoCuota, ErrorGuardarPago) as e:
                error_msg = f"Error al procesar cuota {id_cuota}: {str(e)}"
                print(f"❌ {error_msg}")
                resultados["errores"].append(error_msg)
                # Continuar con las demás cuotas, no cancelar todo
                continue
        
        if resultados["errores"]:
            print(f"⚠️ Se completó con {len(resultados['errores'])} errores")
        else:
            print(f"✅ Inscripción completada exitosamente para alumno {id_alumno}")
            print(f"   Cuotas procesadas: {len(resultados['cuotas_asociadas'])}")
            print(f"   Pagos generados: {len(resultados['pagos_generados'])}")
        
        return resultados
        
    except Exception as e:
        raise ErrorGuardarInscripcionCuotas(f"Error general en la inscripción: {str(e)}")