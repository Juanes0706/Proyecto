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
    placa = Column(String, unique=True, index=True)
    modelo = Column(String)
    capacidad = Column(Integer)
    tipo = Column(String)  # troncal o zonal
    activo = Column(Boolean, default=True)

    estacion_id = Column(Integer, ForeignKey("estaciones.id")) 
    estacion = relationship("Estacion", back_populates="buses")
