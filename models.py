from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Ruta(Base):
    __tablename__ = "rutas"
    id = Column(Integer, primary_key=True, index=True)
    nombre_ruta = Column(String, unique=True, index=True)
    tipo_servicio = Column(String)
    horario = Column(String)
    activo = Column(Boolean, default=True)

    buses = relationship("Bus", back_populates="ruta")

class Bus(Base):
    __tablename__ = "buses"
    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String, unique=True, index=True)
    modelo = Column(String)
    capacidad = Column(Integer)
    tipo = Column(String)  # troncal o zonal
    activo = Column(Boolean, default=True)

    ruta_id = Column(Integer, ForeignKey("rutas.id"))
    ruta = relationship("Ruta", back_populates="buses")

class Estacion(Base):
    __tablename__ = "estaciones"
    id = Column(Integer, primary_key=True, index=True)
    nombre_estacion = Column(String, unique=True, index=True)
    localidad = Column(String)
    rutas_asociadas = Column(String)
    activo = Column(Boolean, default=True)