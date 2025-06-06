from pydantic import BaseModel
from typing import Optional
from enum import Enum
from fastapi import Form, UploadFile, File

# ---------------------- ENUM ----------------------

class BusType(str, Enum):
    troncal = "troncal"
    zonal = "zonal"

# ---------------------- MODELOS Pydantic ----------------------

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

# ---------------------- FORMULARIO PARA UPDATE ----------------------
class BusCreateForm:
    def __init__(
        self,
        nombre_bus: Optional[str] = Form(None),
        tipo: Optional[str] = Form(None),
        activo: Optional[bool] = Form(None),  # CAMBIADO A bool
        imagen: Optional[UploadFile] = File(None)
    ):
        self.nombre_bus = nombre_bus
        self.tipo = tipo
        self.activo = activo
        self.imagen = imagen

class BusUpdateForm(BaseModel):
    # Los nombres de los campos aquí deben coincidir con los atributos 'name' en tu HTML
    nombre_bus: Optional[str] = None
    tipo: Optional[str] = None
    activo: Optional[bool] = None 
    imagen: Optional[UploadFile] = None 


    @classmethod
    def as_form(
        cls,
        nombre_bus: Optional[str] = Form(None),
        tipo: Optional[str] = Form(None),
        activo: Optional[bool] = Form(None),
        imagen: Optional[UploadFile] = File(None),
        
    ):
        return cls(
            nombre_bus=nombre_bus,
            tipo=tipo,
            activo=activo,
            imagen=imagen,
           
        )


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

class EstacionCreateForm:
    def __init__(
        self,
        nombre_estacion: Optional[str] = Form(None),
        localidad: Optional[str] = Form(None),
        rutas_asociadas: Optional[str] = Form(None),
        activo: Optional[bool] = Form(None),  # CAMBIADO A bool
        imagen: Optional[UploadFile] = File(None)
    ):
        self.nombre_estacion = nombre_estacion
        self.localidad = localidad
        self.rutas_asociadas = rutas_asociadas
        self.activo = activo
        self.imagen = imagen

class EstacionUpdateForm:
    def __init__(
        self,
        nombre_estacion: Optional[str] = Form(None),
        localidad: Optional[str] = Form(None),
        rutas_asociadas: Optional[str] = Form(None),
        activo: Optional[bool] = Form(None),  # CAMBIADO A bool
        imagen: Optional[UploadFile] = File(None),
        local_kw: Optional[str] = Form(None)
    ):
        self.nombre_estacion = nombre_estacion
        self.localidad = localidad
        self.rutas_asociadas = rutas_asociadas
        self.activo = activo
        self.imagen = imagen