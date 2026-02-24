# main.py
import sys
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

# Agregar el directorio src al path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

from database.repos_pago import guardar_pago
from models.pago import Pago

def probar_guardar_pago():
    """Prueba guardar un pago en la base de datos"""
    print("\n" + "="*50)
    print("🧪 PROBANDO GUARDAR PAGO")
    print("="*50)
    
    # ACÁ TENÉS QUE PONER EL ID DE LA RELACIÓN ALUMNO-CUOTA QUE SE GENERÓ EN TU PRUEBA ANTERIOR
    ID_ALUMNO_CUOTA_PRUEBA = 1   # <--- CAMBIAR POR EL ID DE TU ALUMNO_CUOTA
    
    # Crear un pago de prueba
    pago_prueba = Pago(
        id_alumno_cuota=ID_ALUMNO_CUOTA_PRUEBA,
        mes_correspondiente=date(2024, 2, 1),  # Febrero 2024
        monto=Decimal("15000.00"),
        metodo_pago="Efectivo",
        pagado_bool=True,
        fecha_pago=datetime.now()
    )
    
    print(f"\n📝 Datos del pago a guardar:")
    print(f"   ID Alumno-Cuota: {pago_prueba.id_alumno_cuota}")
    print(f"   Mes correspondiente: {pago_prueba.mes_correspondiente}")
    print(f"   Monto: ${pago_prueba.monto}")
    print(f"   Método: {pago_prueba.metodo_pago}")
    print(f"   Pagado: {pago_prueba.pagado_bool}")
    print(f"   Fecha pago: {pago_prueba.fecha_pago}")
    
    try:
        id_generado = guardar_pago(pago_prueba)
        print(f"\n✅ ¡Pago guardado exitosamente!")
        print(f"   ID asignado: {id_generado}")
        return id_generado
    except Exception as e:
        print(f"\n❌ Error al guardar pago: {e}")
        return None

def probar_guardar_pago_sin_fecha():
    """Prueba guardar un pago sin especificar fecha (debería usar la actual)"""
    print("\n" + "="*50)
    print("🧪 PROBANDO GUARDAR PAGO (SIN FECHA)")
    print("="*50)
    
    ID_ALUMNO_CUOTA_PRUEBA = 1
    
    # Crear un pago sin fecha (se asignará automáticamente)
    pago_prueba = Pago(
        id_alumno_cuota=ID_ALUMNO_CUOTA_PRUEBA,
        mes_correspondiente=date(2024, 2, 1),
        monto=Decimal("15000.00"),
        metodo_pago="Transferencia",
        pagado_bool=True
        # fecha_pago se deja como None, el repo usará datetime.now()
    )
    
    print(f"\n📝 Datos del pago a guardar:")
    print(f"   ID Alumno-Cuota: {pago_prueba.id_alumno_cuota}")
    print(f"   Mes correspondiente: {pago_prueba.mes_correspondiente}")
    print(f"   Monto: ${pago_prueba.monto}")
    print(f"   Método: {pago_prueba.metodo_pago}")
    print(f"   Pagado: {pago_prueba.pagado_bool}")
    print(f"   Fecha pago: (se asignará automáticamente)")
    
    try:
        id_generado = guardar_pago(pago_prueba)
        print(f"\n✅ ¡Pago guardado exitosamente!")
        print(f"   ID asignado: {id_generado}")
        return id_generado
    except Exception as e:
        print(f"\n❌ Error al guardar pago: {e}")
        return None

def main():
    """Función principal de prueba"""
    print("🚀 INICIANDO PRUEBA DE REPOSITORIO DE PAGO")
    
    # Probar pago con fecha específica
    probar_guardar_pago()
    
    print("\n" + "-"*30)
    
    # Probar pago sin fecha (opcional)
    # probar_guardar_pago_sin_fecha()
    
    print("\n" + "="*50)
    print("✅ PRUEBA COMPLETADA")
    print("="*50)

if __name__ == "__main__":
    main()