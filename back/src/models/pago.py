# src/models/pago.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

@dataclass
class Pago:
    id_alumno_clase: int        # CAMBIADO: antes era id_alumno_cuota
    mes_correspondiente: date   # Mes al que corresponde el pago
    # ELIMINADO: descuento (ahora está en AlumnoClase)
    fecha_pago: Optional[datetime] = None  # Fecha cuando se pagó (NULL si no pagó)
    pagado_bool: bool = False              # Estado del pago
    metodo_pago: Optional[str] = None      # Método de pago (NULL si no pagó)
    id: Optional[int] = None               # ID generado por la BD