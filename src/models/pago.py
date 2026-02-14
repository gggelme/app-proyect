from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Pago:
    id_alumno: int      # Parte de la FK compuesta
    id_instrumento: int # Parte de la FK compuesta
    fecha_vencimiento: date
    estado: str = "PENDIENTE"
    fecha_pago: Optional[date] = None
    id: Optional[int] = None