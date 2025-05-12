from sqlalchemy.orm import Session
import models, schemas

# ---------------------- RUTAS ----------------------

def crear_ruta(db: Session, ruta: schemas.RutaCreate):
    db_ruta = models.Ruta(**ruta.dict())
    db.add(db_ruta)
    db.commit()
    db.refresh(db_ruta)
    return db_ruta

def obtener_rutas(db: Session):
    return db.query(models.Ruta).all()

def obtener_ruta_por_id(db: Session, ruta_id: int):
    return db.query(models.Ruta).filter(models.Ruta.id == ruta_id).first()

def eliminar_ruta(db: Session, ruta_id: int):
    ruta = obtener_ruta_por_id(db, ruta_id)
    if ruta:
        db.delete(ruta)
        db.commit()
    return {"mensaje": "Ruta eliminada"}

def actualizar_estado_ruta(db: Session, ruta_id: int, nuevo_estado: bool):
    ruta = obtener_ruta_por_id(db, ruta_id)
    if ruta:
        ruta.activo = nuevo_estado
        db.commit()
        db.refresh(ruta)
    return ruta

# ---------------------- BUSES ----------------------

def crear_bus(db: Session, bus: schemas.BusCreate):
    db_bus = models.Bus(**bus.dict())
    db.add(db_bus)
    db.commit()
    db.refresh(db_bus)
    return db_bus

def obtener_buses(db: Session):
    return db.query(models.Bus).all()

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
