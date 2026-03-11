# src/models/clase.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Clase:
    nombre_clase: str
    id_profesor: int
    duracion: Optional[int] = None
    id: Optional[int] = None