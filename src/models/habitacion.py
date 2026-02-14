from dataclasses import dataclass
from typing import Optional


@dataclass
class Habitacion:
    nombre: str
    capacidad: int
    id: Optional[int] = None