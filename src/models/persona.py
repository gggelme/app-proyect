# src/models/persona.py
from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

@dataclass
class Persona:
    dni: str
    nomb_apel: str
    fecha_nac: Optional[date] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    id: Optional[int] = None

@dataclass
class Alumno(Persona):
    fecha_ing: Optional[date] = None
    estado_activo: bool = True

@dataclass
class Profesor(Persona):
    alias: Optional[str] = None
    email: Optional[str] = None