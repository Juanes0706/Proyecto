from pydantic import BaseModel
from typing import List, Optional

# ---------------------- RUTAS ----------------------

class RutaBase(BaseModel):
    nombre_ruta: str
    tipo_servicio: str
    horario: str
    activo: bool = True

class RutaCreate(RutaBase):
    pass

class Ruta(RutaBase):
    id: int
    class Config:
        orm_mode = True

# ---------------------- BUSES ----------------------

class BusBase(BaseModel):
    placa: str
    modelo: str
    capacidad: int
    ruta_id: int
    activo: bool = True

class BusCreate(BusBase):
    pass

class Bus(BusBase):
    id: int
    class Config:
        orm_mode = True