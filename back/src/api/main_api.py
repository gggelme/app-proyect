# back/src/api/main_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, List
import sys
import os

# Agregar el path para que encuentre los módulos de src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar repositorios existentes
from database.repos_alumno import guardar_alumno, buscar_alumnos, buscar_alumnos_por_nombre
from database.repos_profesor import guardar_profesor, obtener_todos_profesores
from database.repos_alumno_clase import *
# Importar el nuevo repositorio

from models.persona import Alumno, Profesor

from database.repos_alumno import buscar_alumnos_por_nombre
from database.repos_clase import obtener_todas_clases

from database.repos_inscripcion import guardar_inscripcion_completa, ErrorGuardarInscripcion

from database.repos_cuota import obtener_todas_cuotas
from database.repos_inscripcion_cuotas import guardar_inscripcion_completa_con_cuotas, ErrorGuardarInscripcionCuotas
from database.repos_pago import obtener_pagos_pendientes_agrupados

from models.clase import Clase
from database.repos_clase import guardar_clase



app = FastAPI(
    title="Academia Irupe API",
    description="API para gestión de alumnos y profesores",
    version="1.0.0"
)

# Configurar CORS para que Flutter pueda conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo permitimos todos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- ENDPOINTS DE ALUMNOS -------------------

@app.get("/api/alumnos", response_model=List[dict])
async def get_alumnos():
    """Obtiene todos los alumnos"""
    try:
        alumnos = buscar_alumnos("") 
        return alumnos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alumnos/buscar/{texto}")
async def buscar_alumnos_endpoint(texto: str = ""):
    """Busca alumnos por DNI o nombre"""
    try:
        return buscar_alumnos(texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# crear alumno

@app.post("/api/alumnos", response_model=int)
async def crear_alumno(alumno: dict):
    """Crea un nuevo alumno"""
    try:
        print("=" * 50)
        print("📥 Creando alumno con datos:")
        print(alumno)
        
        nuevo_alumno = Alumno(
            dni=alumno.get("dni"),
            nomb_apel=alumno.get("nomb_apel"),
            fecha_nac=alumno.get("fecha_nac"),
            domicilio=alumno.get("domicilio"),
            telefono=alumno.get("telefono"),
            fecha_ing=alumno.get("fecha_ing"),
            estado_activo=alumno.get("estado_activo", True)
        )
        
        id_generado = guardar_alumno(nuevo_alumno)
        print(f"📌 ID de ALUMNO retornado: {id_generado}")
        print("=" * 50)
        return id_generado
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ------------------- ENDPOINTS DE PROFESORES -------------------

@app.get("/api/profesores", response_model=List[dict])
async def get_profesores():
    """Obtiene todos los profesores"""
    try:
        return obtener_todos_profesores()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/profesores", response_model=int)
async def crear_profesor(profesor: dict):
    """Crea un nuevo profesor"""
    try:
        nuevo_profesor = Profesor(
            dni=profesor.get("dni"),
            nomb_apel=profesor.get("nomb_apel"),
            fecha_nac=profesor.get("fecha_nac"),
            domicilio=profesor.get("domicilio"),
            telefono=profesor.get("telefono"),
            alias=profesor.get("alias"),
            email=profesor.get("email")
        )
        id_generado = guardar_profesor(nuevo_profesor)
        return id_generado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ------------------- ENDPOINT DE SALUD -------------------

@app.get("/api/health")
async def health_check():
    """Verifica que la API funciona"""
    return {
        "status": "ok", 
        "message": "API funcionando correctamente",
        "version": "1.0.0"
    }

# ------------------- ENDPOINT DE HORARIOS -------------------

@app.get("/api/clases")
async def get_clases_por_dia_y_hora(dia: str, hora: str):
    try:
        return obtener_clases_por_dia_y_hora(dia, hora)
    except ErrorConsultaHorarios as e:
        raise HTTPException(status_code=500, detail=str(e))



#-------------------- ENDPOINT DE BÚSQUEDA DE ALUMNOS POR NOMBRE -------------------
@app.get("/api/alumnos/buscar-por-nombre/{texto}")
async def buscar_alumnos_por_nombre_endpoint(texto: str):
    """Busca alumnos por nombre o apellido"""
    try:
        return buscar_alumnos_por_nombre(texto)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- Enpoint tener alumnos

@app.get("/api/alumnos", response_model=List[dict])
async def get_alumnos():
    """Obtiene todos los alumnos"""
    try:
        from database.repos_alumno import buscar_alumnos
        alumnos = buscar_alumnos("")
        print(f"📡 Endpoint /api/alumnos - Enviando {len(alumnos)} alumnos")
        if alumnos:
            print(f"📡 Primer alumno: {alumnos[0].get('nomb_apel')}, fecha_nac: {alumnos[0].get('fecha_nac')}")
        return alumnos
    except Exception as e:
        print(f"❌ Error en endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ------------------- ENDPOINT PARA OBTENER TODAS LAS CLASES -------------------
@app.get("/api/clases/todas")
async def get_todas_clases():
    """Obtiene todas las clases disponibles"""
    try:
        return obtener_todas_clases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# ------------------- ENDPOINT PARA CREAR CLASE CON HORARIOS E INSCRIPCIONES -------------------
@app.post("/api/inscripcion")
async def crear_inscripcion(data: dict):
    """Crea una inscripción completa"""
    try:
        id_clase = data.get("id_clase")
        horarios = data.get("horarios", [])
        alumnos = data.get("alumnos", [])
        
        if not id_clase:
            raise HTTPException(status_code=400, detail="Falta ID de clase")
        
        if not alumnos:
            raise HTTPException(status_code=400, detail="No hay alumnos para inscribir")
        
        resultados = guardar_inscripcion_completa(id_clase, horarios, alumnos)
        
        return {
            "status": "success",
            "message": f"Inscripción completada: {len(resultados['inscripciones'])} alumnos, {len(resultados['horarios_guardados'])} horarios",
            "data": resultados
        }
        
    except ErrorGuardarInscripcion as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    # ------------------- ENDPOINT DE CUOTAS -------------------

@app.get("/api/cuotas")
async def get_cuotas():
    """Obtiene todas las cuotas disponibles"""
    try:
        from database.repos_cuota import obtener_todas_cuotas
        cuotas = obtener_todas_cuotas()
        print(f"📊 Cuotas encontradas: {cuotas}")  # Para debug
        return cuotas
    except Exception as e:
        print(f"❌ Error en get_cuotas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


# ------------------- ENDPOINT DE INSCRIPCIÓN CON CUOTAS -------------------

@app.post("/api/inscripcion-cuotas")
async def crear_inscripcion_con_cuotas(data: dict):
    """
    Crea una inscripción completa con cuotas y pagos automáticos
    Data esperado:
    {
        "id_alumno": int,
        "ids_cuotas": List[int],
        "porcentaje_descuento": float
    }
    """
    try:
    
        
        id_alumno = data.get("id_alumno")
        ids_cuotas = data.get("ids_cuotas", [])
        porcentaje_descuento = data.get("porcentaje_descuento", 0.0)
        
        if not id_alumno:
            raise HTTPException(status_code=400, detail="Falta ID de alumno")
        
        if not ids_cuotas:
            raise HTTPException(status_code=400, detail="No hay cuotas seleccionadas")
        
        if porcentaje_descuento < 0 or porcentaje_descuento > 100:
            raise HTTPException(status_code=400, detail="El descuento debe estar entre 0 y 100")
        
        resultados = guardar_inscripcion_completa_con_cuotas(
            id_alumno, 
            ids_cuotas, 
            porcentaje_descuento
        )
        
        if resultados["errores"]:
            return {
                "status": "partial",
                "message": f"Inscripción completada parcialmente: {len(resultados['pagos_generados'])} cuotas procesadas, {len(resultados['errores'])} errores",
                "data": resultados
            }
        else:
            return {
                "status": "success",
                "message": f"Inscripción completada exitosamente: {len(resultados['pagos_generados'])} cuotas asociadas con sus pagos",
                "data": resultados
            }
        
    except ErrorGuardarInscripcionCuotas as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    # ------------------- ENDPOINT DE PAGOS PENDIENTES -------------------

@app.get("/api/pagos/pendientes")
async def get_pagos_pendientes():
    """Obtiene todos los pagos pendientes agrupados por alumno y mes"""
    try:
        from database.repos_pago import obtener_pagos_pendientes_agrupados
        return obtener_pagos_pendientes_agrupados()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- ENDPOINT PARA REGISTRAR PAGO -------------------

@app.post("/api/pagos/registrar")
async def registrar_pago(data: dict):
    """
    Registra un pago para un alumno
    """
    try:
        from database.repos_pago import registrar_pago_adelantado
        
        print("\n🔍 [ENDPOINT] Datos recibidos completos:")
        print(data)
        
        alumno_id = data.get("alumno_id")
        meses_a_pagar = data.get("meses_a_pagar", 1)
        metodo_pago = data.get("metodo_pago")
        mantener_descuento_raw = data.get("mantener_descuento", True)
        
        print(f"🔍 [ENDPOINT] alumno_id: {alumno_id}")
        print(f"🔍 [ENDPOINT] meses_a_pagar: {meses_a_pagar}")
        print(f"🔍 [ENDPOINT] metodo_pago: {metodo_pago} (tipo: {type(metodo_pago)})")
        print(f"🔍 [ENDPOINT] mantener_descuento_raw: {mantener_descuento_raw} (tipo: {type(mantener_descuento_raw)})")
        
        # Convertir explícitamente a bool
        if isinstance(mantener_descuento_raw, str):
            mantener_descuento = mantener_descuento_raw.lower() == 'true'
        else:
            mantener_descuento = bool(mantener_descuento_raw)
        
        print(f"🔍 [ENDPOINT] mantener_descuento convertido: {mantener_descuento}")
        
        if not alumno_id:
            raise HTTPException(status_code=400, detail="Falta ID de alumno")
        
        if meses_a_pagar < 1:
            raise HTTPException(status_code=400, detail="Debe pagar al menos 1 mes")
        
        if not metodo_pago:
            raise HTTPException(status_code=400, detail="Debe seleccionar un método de pago")
        
        resultado = registrar_pago_adelantado(
            alumno_id, 
            meses_a_pagar, 
            metodo_pago, 
            mantener_descuento
        )
        
        return {
            "status": "success",
            "message": f"Pago registrado exitosamente: {resultado['meses_procesados']} meses pagados",
            "data": resultado
        }
        
    except Exception as e:
        print(f"❌ Error en registrar_pago: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

    # actualizacion cuotas

@app.put("/api/cuotas")
async def update_cuotas(cuotas: List[Dict[str, Any]]):
    """
    Actualiza múltiples cuotas
    Espera un array de objetos con id y nuevo_precio
    Ejemplo: [{"id": 1, "nuevo_precio": 16000}, {"id": 2, "nuevo_precio": 13000}]
    """
    try:
        from database.repos_cuota import actualizar_precios_cuotas
        
        # Validar que cada objeto tenga los campos necesarios
        for cuota in cuotas:
            if "id" not in cuota or "nuevo_precio" not in cuota:
                raise HTTPException(
                    status_code=400, 
                    detail="Cada cuota debe tener 'id' y 'nuevo_precio'"
                )
        
        resultado = actualizar_precios_cuotas(cuotas)
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en update_cuotas: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ------------------- ENDPOINT DE CUOTAS POR ALUMNO -------------------

@app.get("/api/alumnos/{id_alumno}/cuotas")
async def get_cuotas_por_alumno(id_alumno: int):
    """Obtiene todas las cuotas asociadas a un alumno"""
    try:
        from database.repos_alumno_cuota import obtener_cuotas_por_alumno
        cuotas = obtener_cuotas_por_alumno(id_alumno)
        return cuotas
    except Exception as e:
        print(f"❌ Error en get_cuotas_por_alumno: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# ------------------- ENDPOINT PARA ACTUALIZAR PROFESOR -------------------

@app.put("/api/profesores/{id_profesor}")
async def actualizar_profesor(id_profesor: int, profesor: dict):
    """Actualiza los datos de un profesor"""
    try:
        from database.repos_profesor import actualizar_profesor
        resultado = actualizar_profesor(id_profesor, profesor)
        
        if resultado:
            return {"status": "success", "message": "Profesor actualizado correctamente"}
        else:
            raise HTTPException(status_code=404, detail="Profesor no encontrado")
            
    except Exception as e:
        print(f"❌ Error en actualizar_profesor: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# ------------------- ENDPOINT PARA ACTUALIZAR ALUMNO -------------------

@app.put("/api/alumnos/{id_alumno}")
async def actualizar_alumno(id_alumno: int, alumno: dict):
    """Actualiza los datos de un alumno"""
    try:
        from database.repos_alumno import actualizar_alumno
        resultado = actualizar_alumno(id_alumno, alumno)
        
        if resultado:
            return {"status": "success", "message": "Alumno actualizado correctamente"}
        else:
            raise HTTPException(status_code=404, detail="Alumno no encontrado")
            
    except Exception as e:
        print(f"❌ Error en actualizar_alumno: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------- ENDPOINT PARA ACTUALIZAR CUOTAS DEL ALUMNO -------------------

@app.put("/api/alumnos/{id_alumno}/cuotas")
async def actualizar_cuotas_alumno(id_alumno: int, data: dict):
    """
    Actualiza las cuotas de un alumno
    Data esperado: {"ids_cuotas": [1, 2, 3]}
    """
    try:
        from database.repos_alumno_cuota_update import actualizar_cuotas_alumno
        
        ids_cuotas = data.get("ids_cuotas", [])
        
        if not isinstance(ids_cuotas, list):
            raise HTTPException(status_code=400, detail="ids_cuotas debe ser una lista")
        
        resultado = actualizar_cuotas_alumno(id_alumno, ids_cuotas)
        
        if resultado["success"]:
            return {
                "status": "success",
                "message": f"Cuotas actualizadas: {resultado['eliminadas']} eliminadas, {resultado['agregadas']} agregadas",
                "data": resultado
            }
        else:
            raise HTTPException(status_code=500, detail=resultado.get("message", "Error al actualizar cuotas"))
            
    except Exception as e:
        print(f"❌ Error en actualizar_cuotas_alumno: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# ------------------- ENDPOINTS PARA EDICIÓN DE CLASES -------------------

@app.get("/api/inscripciones")
async def get_inscripciones_agrupadas():
    """Obtiene todas las inscripciones agrupadas por alumno y clase"""
    try:
        from database.repos_alumno_clase_edicion import obtener_inscripciones_agrupadas
        return obtener_inscripciones_agrupadas()
    except Exception as e:
        print(f"❌ Error en get_inscripciones_agrupadas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clases/{id_clase}/alumnos")
async def get_alumnos_por_clase(id_clase: int):
    """Obtiene todos los alumnos de una clase"""
    try:
        from database.repos_alumno_clase_edicion import obtener_alumnos_por_clase
        return obtener_alumnos_por_clase(id_clase)
    except Exception as e:
        print(f"❌ Error en get_alumnos_por_clase: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clases/{id_clase}/horarios")
async def get_horarios_por_clase(id_clase: int):
    """Obtiene todos los horarios de una clase"""
    try:
        from database.repos_alumno_clase_edicion import obtener_horarios_por_clase
        return obtener_horarios_por_clase(id_clase)
    except Exception as e:
        print(f"❌ Error en get_horarios_por_clase: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel

# Crear un modelo Pydantic para la clase
class ClaseCreate(BaseModel):
    nombre_clase: str
    id_profesor: int
    duracion: int = 60

@app.post("/api/clases")
async def crear_clase(clase: ClaseCreate):  # ← Recibir como JSON body
    """Crea una nueva clase"""
    
    try:
        nueva_clase = Clase(
            nombre_clase=clase.nombre_clase,
            id_profesor=clase.id_profesor,
            duracion=clase.duracion
        )
        
        id_generado = guardar_clase(nueva_clase)
        
        return {
            'status': 'success',
            'message': 'Clase creada exitosamente',
            'id': id_generado
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# ------------------- ENDPOINT PARA ACTUALIZAR HORARIOS DE ALUMNO EN CLASE -------------------

@app.put("/api/alumno-clase/horarios")
async def actualizar_horarios_alumno_clase(data: dict):
    """
    Actualiza los horarios de un alumno en una clase específica
    Data esperado: {
        "alumno_id": int,
        "clase_id": int,
        "horarios": [{"dia": "Lunes", "hora": "09:00", "aula": "A"}, ...]
    }
    """
    try:
        print("\n" + "="*50)
        print("📝 Actualizando horarios de alumno en clase")
        print(f"   Alumno ID: {data.get('alumno_id')}")
        print(f"   Clase ID: {data.get('clase_id')}")
        print(f"   Horarios: {data.get('horarios')}")
        print("="*50)
        
        # Importar la función del repositorio
        from database.repos_alumno_clase_edicion import actualizar_horarios_alumno_clase
        
        # Actualizar en base de datos
        success = actualizar_horarios_alumno_clase(
            data.get('alumno_id'),
            data.get('clase_id'),
            data.get('horarios', [])
        )
        
        if success:
            return {
                "status": "success",
                "message": "Horarios actualizados correctamente"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al actualizar los horarios"
            )
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

# En main_api.py, agregar estos endpoints después de los existentes

# ------------------- ENDPOINTS PARA EDICIÓN DE CLASES -------------------

from database.repos_clase_edicion import (
    obtener_todas_clases_completas,
    actualizar_clase,
    eliminar_clase,
    ErrorActualizarClase,
    ErrorEliminarClase
)

@app.get("/api/clases/editar/todas")
async def get_todas_clases_para_editar():
    """Obtiene todas las clases para editar"""
    try:
        return obtener_todas_clases_completas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/clases/{id_clase}")
async def update_clase(id_clase: int, data: dict):
    """
    Actualiza una clase existente
    Data esperado: {"nombre_clase": "Nuevo nombre", "duracion": 90}
    """
    try:
        nombre_clase = data.get("nombre_clase")
        duracion = data.get("duracion")
        
        resultado = actualizar_clase(
            id_clase=id_clase,
            nombre_clase=nombre_clase,
            duracion=duracion
        )
        
        return {
            "status": "success",
            "message": "Clase actualizada correctamente"
        }
        
    except ErrorActualizarClase as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/clases/{id_clase}")
async def delete_clase(id_clase: int, confirm: bool = False):
    """
    Elimina una clase y todas sus inscripciones asociadas
    Requiere confirm=true para ejecutar
    """
    if not confirm:
        raise HTTPException(
            status_code=400, 
            detail="Se requiere confirmación. Enviar confirm=true"
        )
    
    try:
        resultado = eliminar_clase(id_clase)
        return resultado
        
    except ErrorEliminarClase as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# En main_api.py, agregar este endpoint

from database.repos_alumno_clase_edicion import obtener_todas_sesiones_agrupadas

@app.get("/api/sesiones/agrupadas")
async def get_sesiones_agrupadas():
    """Obtiene todas las sesiones agrupadas por alumno y clase"""
    try:
        return obtener_todas_sesiones_agrupadas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



# Para correr directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)