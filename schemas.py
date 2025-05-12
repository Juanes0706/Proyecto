from pydantic import BaseModel
from typing import List, Optional

# ---------------------- RUTAS ----------------------

class RutaBase(BaseModel):
    nombre_ruta: str
    tipo_servicio: str
    horario: str

class RutaCreate(RutaBase):
    pass

class Ruta(RutaBase):
    id: int
    activo: bool

    class Config:
        orm_mode = True  

# ---------------------- ESTACIONES ----------------------

class EstacionBase(BaseModel):
    nombre_estacion: str
    localidad: str
    rutas_asociadas: List[int]  
class EstacionCreate(EstacionBase):
    pass

class Estacion(EstacionBase):
    id: int
    activo: bool

    class Config:
        orm_mode = True
