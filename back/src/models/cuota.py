# src/models/cuota.py
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

@dataclass
class Cuota:
    nombre: str
    precio_cuota: Decimal
    id: Optional[int] = None