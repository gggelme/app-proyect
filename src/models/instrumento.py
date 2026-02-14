from dataclasses import dataclass
from typing import Optional

@dataclass
class Instrumento:
    nombre: str
    precio_hora: float  
    id: Optional[int] = None