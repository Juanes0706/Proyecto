from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Estacion(Base):
    __tablename__ = "estaciones"
    id = Column(Integer, primary_key=True, index=True)
    nombre_estacion = Column(String, unique=True, index=True)
    localidad = Column(String)
    rutas_asociadas = Column(String)
    activo = Column(Boolean, default=True)

    buses = relationship("Bus", back_populates="estacion")

class Bus(Base):
    __tablename__ = "buses"
    id = Column(Integer, primary_key=True, index=True)
    nombre_bus = Column(String)
    tipo = Column(String)  
    activo = Column(Boolean, default=True)
