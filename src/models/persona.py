from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Persona:
    dni: str
    nombre_apellido: str
    fecha_nac: date
    telefono: str
    fecha_ingreso: date
    domicilio: Optional[str] = None
    id: Optional[int] = None

@dataclass
class Alumno(Persona):
    # Por ahora Alumno no tiene campos extra en la base de datos, 
    # pero hereda todo lo de Persona.
    pass

@dataclass
class Profesor(Persona):
    # Sumamos el atributo específico de la tabla PROFESOR
    alias_mp: Optional[str] = None