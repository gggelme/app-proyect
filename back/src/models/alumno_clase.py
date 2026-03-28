# src/models/alumno_clase.py
from dataclasses import dataclass
from typing import Optional
from datetime import date
from decimal import Decimal

@dataclass
class AlumnoClase:
    id_alumno: int
    id_clase: int
    id_horario: int
    aula: str  # ← Nueva columna: A, B, C, D
    fecha_inscripcion: Optional[date] = None  # Default CURRENT_DATE en BD
    id: Optional[int] = None