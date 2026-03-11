# src/models/horario.py
from dataclasses import dataclass
from typing import Optional
from datetime import time

@dataclass
class Horario:
    dia: str
    hora_init: time
    hora_fin: time
    id: Optional[int] = None