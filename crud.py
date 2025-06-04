import logging
import unicodedata
import asyncio
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from supabase_client import supabase, save_file
from db import SessionLocal
import models

# ---------------------- Funciones Auxiliares ----------------------

def normalize_string(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()

def subir_imagen(bucket: str, filename: str, imagen_bytes: bytes) -> Optional[str]:
    try:
        response = supabase.storage.from_(bucket).upload(filename, imagen_bytes, {"content-type": "image/jpeg"})
        if response.get("error"):
            logging.error(f"Error al subir imagen: {response['error']}")
            return None
        return supabase.storage.from_(bucket).get_public_url(filename)
    except Exception as e:
        logging.error(f"Excepción al subir imagen: {e}")
        return None

# ---------------------- CRUD Buses ----------------------

def obtener_buses(bus_id: Optional[int] = None, tipo: Optional[str] = None, activo: Optional[bool] = None):
    db: Session = SessionLocal()
    query = db.query(models.Bus)
    if bus_id is not None:
        query = query.filter(models.Bus.id == bus_id)
    if tipo:
        query = query.filter(models.Bus.tipo.ilike(f"%{tipo.strip().lower()}%"))
    if activo is not None:
        query = query.filter(models.Bus.activo == activo)
    buses = query.all()
    db.close()
    return buses

def obtener_bus_por_id(bus_id: int):
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    db.close()
    return bus

def crear_bus(bus: dict, imagen_bytes: Optional[bytes] = None, imagen_filename: Optional[str] = None):
    imagen_url = subir_imagen("buses", imagen_filename, imagen_bytes) if imagen_bytes and imagen_filename else None
    db: Session = SessionLocal()
    nuevo_bus = models.Bus(
        nombre_bus=bus.get("nombre_bus"),
        tipo=bus.get("tipo", "").strip().lower(),
        activo=bus.get("activo"),
        imagen=imagen_url
    )
    db.add(nuevo_bus)
    db.commit()
    db.refresh(nuevo_bus)
    db.close()
    return nuevo_bus

async def crear_bus_async(bus: dict, imagen: UploadFile):
    imagen_url = None
    if imagen:
        result = await save_file(imagen, to_supabase=True)
        imagen_url = result.get("url", {}).get("publicUrl") if isinstance(result.get("url"), dict) else result.get("url")

    def db_task():
        db: Session = SessionLocal()
        nuevo_bus = models.Bus(
            nombre_bus=bus.get("nombre_bus"),
            tipo=bus.get("tipo", "").strip().lower(),
            activo=bus.get("activo"),
            imagen=imagen_url
        )
        db.add(nuevo_bus)
        db.commit()
        db.refresh(nuevo_bus)
        db.close()
        return nuevo_bus

    return await asyncio.to_thread(db_task)

def actualizar_bus(bus_id: int, update_data: dict):
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None

    if "imagen" in update_data and update_data["imagen"] and bus.imagen:
        try:
            filename = bus.imagen.split("/buses/")[-1]
            supabase.storage.from_("buses").remove([filename])
        except Exception as e:
            logging.error(f"Error eliminando imagen anterior: {e}")

    for key, value in update_data.items():
        setattr(bus, key, value)

    db.commit()
    db.refresh(bus)
    db.close()
    return bus

def eliminar_bus(bus_id: int):
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None

    if bus.imagen:
        try:
            filename = bus.imagen.split("/buses/")[-1]
            supabase.storage.from_("buses").remove([filename])
        except Exception as e:
            logging.error(f"Error eliminando imagen de bus: {e}")

    db.delete(bus)
    db.commit()
    db.close()
    return {"mensaje": "Bus eliminado"}

# ---------------------- CRUD Estaciones ----------------------

def obtener_estaciones(estacion_id: Optional[int] = None, sector: Optional[str] = None, activo: Optional[bool] = None):
    db: Session = SessionLocal()
    query = db.query(models.Estacion)
    if estacion_id:
        query = query.filter(models.Estacion.id == estacion_id)
    if sector:
        query = query.filter(models.Estacion.localidad.ilike(f"%{normalize_string(sector)}%"))
    if activo is not None:
        query = query.filter(models.Estacion.activo == activo)
    estaciones = query.all()
    db.close()
    return estaciones

def obtener_estacion_por_id(estacion_id: int):
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    db.close()
    return estacion

def crear_estacion(estacion: dict, imagen_bytes: Optional[bytes] = None, imagen_filename: Optional[str] = None):
    imagen_url = subir_imagen("estaciones", imagen_filename, imagen_bytes) if imagen_bytes and imagen_filename else None
    db: Session = SessionLocal()
    nueva_estacion = models.Estacion(
        nombre_estacion=estacion.get("nombre_estacion"),
        localidad=estacion.get("localidad"),
        rutas_asociadas=estacion.get("rutas_asociadas"),
        activo=estacion.get("activo"),
        imagen=imagen_url
    )
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    db.close()
    return nueva_estacion

async def crear_estacion_async(estacion: dict, imagen: Optional[UploadFile]) -> Optional[models.Estacion]:
    imagen_url = None
    if imagen:
        try:
            result = await save_file(imagen, to_supabase=True)
            imagen_url = result.get("url", {}).get("publicUrl") if isinstance(result.get("url"), dict) else result.get("url")
        except Exception as e:
            logging.error(f"Error subiendo imagen estación: {e}")

    def db_task():
        db: Session = SessionLocal()
        nueva_estacion = models.Estacion(
            nombre_estacion=estacion.get("nombre_estacion"),
            localidad=estacion.get("localidad"),
            rutas_asociadas=estacion.get("rutas_asociadas"),
            activo=estacion.get("activo"),
            imagen=imagen_url
        )
        db.add(nueva_estacion)
        db.commit()
        db.refresh(nueva_estacion)
        db.close()
        return nueva_estacion

    return await asyncio.to_thread(db_task)

def actualizar_estacion(estacion_id: int, update_data: dict):
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None

    if "imagen" in update_data and update_data["imagen"] and estacion.imagen:
        try:
            filename = estacion.imagen.split("/estaciones/")[-1]
            supabase.storage.from_("estaciones").remove([filename])
        except Exception as e:
            logging.error(f"Error eliminando imagen anterior: {e}")

    for key, value in update_data.items():
        setattr(estacion, key, value)

    db.commit()
    db.refresh(estacion)
    db.close()
    return estacion

def eliminar_estacion(estacion_id: int):
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None

    if estacion.imagen:
        try:
            filename = estacion.imagen.split("/estaciones/")[-1]
            supabase.storage.from_("estaciones").remove([filename])
        except Exception as e:
            logging.error(f"Error eliminando imagen estación: {e}")

    db.delete(estacion)
    db.commit()
    db.close()
    return {"mensaje": "Estación eliminada"}
