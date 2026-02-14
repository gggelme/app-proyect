from dataclasses import dataclass
from typing import Optional

@dataclass
class Clase:
    nombre_materia: str  # <--- Agregado
    id_profesor: int
    id_habitacion: int
    dia_semana: str
    hora_inicio: str
    hora_fin: str
    id: Optional[int] = None