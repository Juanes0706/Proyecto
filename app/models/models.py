from sqlalchemy import Column, Integer, String, Boolean
from app.database.db import Base

class Ruta(Base):
    __tablename__ = "rutas"
    id = Column(Integer, primary_key=True, index=True)
    nombre_ruta = Column(String, unique=True, index=True)
    tipo_servicio = Column(String)
    horario = Column(String)
    activo = Column(Boolean, default=True)

class Bus(Base):
    __tablename__ = "buses"
    id = Column(Integer, primary_key=True, index=True)
    nombre_bus = Column(String, index=True)
    tipo = Column(String)  
    activo = Column(Boolean, default=True)
    imagen = Column(String, nullable=True)  

class Estacion(Base):
    __tablename__ = "estaciones"
    id = Column(Integer, primary_key=True, index=True)
    nombre_estacion = Column(String, unique=True, index=True)
    localidad = Column(String)  
    rutas_asociadas = Column(String)
    activo = Column(Boolean, default=True)
    imagen = Column(String, nullable=True)  