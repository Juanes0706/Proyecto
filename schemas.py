from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# ---------------------- BUSES ----------------------

class BusType(str, Enum):
    troncal = "troncal"
    zonal = "zonal"

class BusBase(BaseModel):
    nombre_bus: str
    tipo: BusType  
    activo: bool = True

class BusCreate(BusBase):
    pass

class Bus(BusBase):
    id: int
    class Config:
        orm_mode = True

# ---------------------- ESTACIONES ----------------------

class EstacionBase(BaseModel):
    nombre_estacion: str
    localidad: str
    rutas_asociadas: str
    activo: bool = True

class EstacionCreate(EstacionBase):
    pass

class Estacion(EstacionBase):
    id: int
    class Config:
        orm_mode = True
