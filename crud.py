from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas
from typing import Optional

# ---------------------- BUSES ----------------------

def obtener_buses(db: Session, tipo: Optional[str] = None):
    query = db.query(models.Bus)
    
    if tipo:
        query = query.filter(models.Bus.tipo == tipo)

    return query.all()

def obtener_bus_por_id(db: Session, bus_id: int):
    return db.query(models.Bus).filter(models.Bus.id == bus_id).first()

def eliminar_bus(db: Session, bus_id: int):
    bus = obtener_bus_por_id(db, bus_id)
    if bus:
        db.delete(bus)
        db.commit()
    return {"mensaje": "Bus eliminado"}

def actualizar_estado_bus(db: Session, bus_id: int, nuevo_estado: bool):
    bus = obtener_bus_por_id(db, bus_id)
    if bus:
        bus.activo = nuevo_estado
        db.commit()
        db.refresh(bus)
    return bus


# ---------------------- ESTACIONES ----------------------

def obtener_estaciones(db: Session, sector: Optional[str] = None):
    query = db.query(models.Estacion)
    
    if sector:
        query = query.filter(models.Estacion.localidad == sector)

    return query.all()

def obtener_estacion_por_id(db: Session, estacion_id: int):
    return db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()

def eliminar_estacion(db: Session, estacion_id: int):
    estacion = obtener_estacion_por_id(db, estacion_id)
    if estacion:
        db.delete(estacion)
        db.commit()
    return {"mensaje": "Estación eliminada"}

def actualizar_estado_estacion(db: Session, estacion_id: int, nuevo_estado: bool):
    estacion = obtener_estacion_por_id(db, estacion_id)
    if estacion:
        estacion.activo = nuevo_estado
        db.commit()
        db.refresh(estacion)
    return estacion
