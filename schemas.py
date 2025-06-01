from pydantic import BaseModel
from typing import Optional
from enum import Enum

# ---------------------- BUSES ----------------------

class BusType(str, Enum):
    troncal = "troncal"
    zonal = "zonal"

class BusBase(BaseModel):
    nombre_bus: str
    tipo: str
    activo: bool = True
    imagen: Optional[str] = None

class BusCreate(BusBase):
    pass

class Bus(BusBase):
    id: int

    class Config:
        from_attributes = True

class BusResponse(BaseModel):
    id: int
    nombre_bus: str
    tipo: str
    activo: bool
    imagen: Optional[str] = None

    class Config:
        from_attributes = True

# ---------------------- ESTACIONES ----------------------

class EstacionBase(BaseModel):
    nombre_estacion: str
    localidad: str
    rutas_asociadas: str
    activo: bool = True
    imagen: Optional[str] = None

class EstacionCreate(EstacionBase):
    pass

class Estacion(EstacionBase):
    id: int

    class Config:
        from_attributes = True

class EstacionResponse(BaseModel):
    id: int
    nombre_estacion: str
    localidad: str
    rutas_asociadas: str
    activo: bool
    imagen: Optional[str] = None

    class Config:
        from_attributes = True
