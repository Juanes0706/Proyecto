from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas
from typing import Optional
import unicodedata


# ---------------------- BUSES ----------------------

def obtener_buses(db: Session, tipo: Optional[str] = None):
    query = db.query(models.Bus)
    
    if tipo:
        query = query.filter(models.Bus.tipo.ilike(f"%{tipo}%"))

    buses = query.all()
    # Normalize tipo to lowercase and strip spaces in response
    for bus in buses:
        if bus.tipo:
            bus.tipo = bus.tipo.strip().lower()
    return buses

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

def crear_bus(db: Session, bus: schemas.BusCreate):
    tipo_normalizado = bus.tipo.value.lower().strip() if hasattr(bus.tipo, 'value') else bus.tipo.lower().strip()
    nuevo_bus = models.Bus(
        nombre_bus=bus.nombre_bus,
        tipo=tipo_normalizado,
        activo=bus.activo
    )
    db.add(nuevo_bus)
    db.commit()
    db.refresh(nuevo_bus)
    return nuevo_bus


# ---------------------- ESTACIONES ----------------------

def normalize_string(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()

def obtener_estaciones(db: Session, sector: Optional[str] = None):
    estaciones = db.query(models.Estacion).all()
    if sector:
        sector_norm = normalize_string(sector)
        estaciones = [e for e in estaciones if normalize_string(e.localidad) == sector_norm]
    return estaciones

def obtener_estacion_por_id(db: Session, estacion_id: int):
    return db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()

def eliminar_estacion(db: Session, estacion_id: int):
    estacion = obtener_estacion_por_id(db, estacion_id)
    if not estacion:
        return None
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

def actualizar_id_estacion(db: Session, estacion_id: int, nuevo_id: int):
    estacion = obtener_estacion_por_id(db, estacion_id)
    if estacion:
        estacion.id = nuevo_id
        db.commit()
        db.refresh(estacion)
        return estacion
    return None

def crear_estacion(db: Session, estacion: schemas.EstacionCreate):
    nueva_estacion = models.Estacion(
        nombre_estacion=estacion.nombre_estacion,
        localidad=estacion.localidad,
        rutas_asociadas=estacion.rutas_asociadas,
        activo=estacion.activo
    )
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return nueva_estacion
