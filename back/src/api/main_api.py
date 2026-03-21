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
# Importar el nuevo repositorio
from database.repos_horario_clase_consultas import (
    obtener_clases_por_dia_y_hora,
    ErrorConsultaHorarios
)
from models.persona import Alumno, Profesor

from database.repos_alumno import buscar_alumnos_por_nombre
from database.repos_clase import obtener_todas_clases

from database.repos_inscripcion import guardar_inscripcion_completa, ErrorGuardarInscripcion

from database.repos_cuota import obtener_todas_cuotas
from database.repos_inscripcion_cuotas import guardar_inscripcion_completa_con_cuotas, ErrorGuardarInscripcionCuotas
from database.repos_pago import registrar_pago_adelantado
from database.repos_pago import obtener_pagos_pendientes_agrupados




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


# Para correr directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)