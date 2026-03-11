# src/models/pago.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

@dataclass
class Pago:
    id_alumno_cuota: int
    mes_correspondiente: date           # Sin default, va primero
    monto: Decimal                       # Sin default, va segundo
    fecha_pago: Optional[datetime] = None  # Con default, va después
    pagado_bool: bool = False             # Con default
    metodo_pago: Optional[str] = None     # Con default
    id: Optional[int] = None              # Con default