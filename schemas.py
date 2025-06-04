from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from fastapi import Form, UploadFile, File

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

class BusUpdateForm:
    def __init__(
        self,
        nombre_bus: Optional[str] = Form(None),
        tipo: Optional[str] = Form(None),
        activo: Optional[bool] = Form(None),
        imagen: Optional[UploadFile] = File(None)
    ):
        self.nombre_bus = nombre_bus
        self.tipo = tipo
        self.activo = activo
        self.imagen = imagen

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

class EstacionUpdateForm:
    def __init__(
        self,
        nombre_estacion: Optional[str] = Form(None),
        localidad: Optional[str] = Form(None),
        rutas_asociadas: Optional[str] = Form(None),
        activo: Optional[bool] = Form(None),
        imagen: Optional[UploadFile] = File(None)
    ):
        self.nombre_estacion = nombre_estacion
        self.localidad = localidad
        self.rutas_asociadas = rutas_asociadas
        self.activo = activo
        self.imagen = imagen
