# src/models/actualizar_horarios_request.py
from pydantic import BaseModel
from typing import List

class HorarioUpdate(BaseModel):
    dia: str
    hora: str
    aula: str

class ActualizarHorariosRequest(BaseModel):
    alumno_id: int
    clase_id: int
    horarios: List[HorarioUpdate]