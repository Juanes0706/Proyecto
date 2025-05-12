from pydantic import BaseModel
from typing import List, Optional

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

# ---------------------- BUSES ----------------------

class BusBase(BaseModel):
    nombre_bus: str
    tipo: str 
    activo: bool = True
    estacion_id: int

class BusCreate(BusBase):
    pass

class Bus(BusBase):
    id: int
    class Config:
        orm_mode = True
