from sqlalchemy.orm import Session
from models import Ruta, Estacion
from schemas import RutaCreate, EstacionCreate
from fastapi import HTTPException

# ---------- Rutas ----------
def crear_ruta(db: Session, ruta: RutaCreate):
    if db.query(Ruta).filter(Ruta.nombre_ruta == ruta.nombre_ruta).first():
        raise HTTPException(status_code=400, detail="La ruta ya está registrada")
    db_ruta = Ruta(**ruta.dict())
    db.add(db_ruta)
    db.commit()
    db.refresh(db_ruta)
    return db_ruta

# ---------- Estaciones ----------
def crear_estacion(db: Session, estacion: EstacionCreate):
    if db.query(Estacion).filter(Estacion.nombre_estacion == estacion.nombre_estacion).first():
        raise HTTPException(status_code=400, detail="La estación ya está registrada")
    db_estacion = Estacion(**estacion.dict())
    db.add(db_estacion)
    db.commit()
    db.refresh(db_estacion)
    return db_estacion
