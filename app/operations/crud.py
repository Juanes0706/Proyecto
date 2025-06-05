import logging
import asyncio
import unicodedata
from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database.db import *
from app.models import *  
from app.schemas import *
from app.services import * 
from app.services.supabase_client import *
from app.models.models import Bus, Estacion  

# ---------------------- CONST ----------------------
SUPABASE_BUCKET_BUSES = "buses"
SUPABASE_BUCKET_ESTACIONES = "estaciones"


# ---------------------- UTILS ----------------------
def get_supabase_path_from_url(url: str, bucket_name: str) -> str:
    parts = url.split(f"/public/{bucket_name}/")
    if len(parts) > 1:
        return parts[-1]
    return ""

def normalize_string(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()


# ---------------------- BUS CRUD ----------------------
def obtener_buses(bus_id: Optional[int] = None, tipo: Optional[str] = None, activo: Optional[bool] = None):
    db: Session = SessionLocal()
    query = db.query(Bus)
    if bus_id is not None:
        query = query.filter(Bus.id == bus_id)
    if tipo:
        query = query.filter(Bus.tipo.ilike(f"%{tipo}%"))
    if activo is not None:
        query = query.filter(Bus.activo == activo)
    buses = query.all()
    for bus in buses:
        if bus.tipo:
            bus.tipo = bus.tipo.strip().lower()
    db.close()
    return buses

def obtener_bus_por_id(bus_id: int):
    db: Session = SessionLocal()
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    db.close()
    return bus

def actualizar_bus(bus_id: int, update_data: dict):
    logging.info(f"Actualizar bus {bus_id} con datos: {update_data}")
    db: Session = SessionLocal()
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        db.close()
        logging.warning(f"Bus {bus_id} no encontrado para actualizar")
        return None
    try:
        if "imagen" in update_data and update_data["imagen"] and bus.imagen:
            try:
                filename = get_supabase_path_from_url(bus.imagen, SUPABASE_BUCKET_BUSES)
                if filename:
                    supabase.storage.from_(SUPABASE_BUCKET_BUSES).remove([filename])
                    logging.info(f"Imagen antigua de bus eliminada: {filename}")
            except Exception as e:
                logging.error(f"Error eliminando imagen antigua de bus: {e}")

        for key, value in update_data.items():
            setattr(bus, key, value)
        db.commit()
        db.refresh(bus)
    except Exception as e:
        logging.error(f"Error actualizando bus {bus_id}: {e}")
        db.rollback()
        bus = None
    finally:
        db.close()
    return bus

def eliminar_bus(bus_id: int):
    db: Session = SessionLocal()
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None
    imagen_url = bus.imagen
    if imagen_url:
        try:
            filename = get_supabase_path_from_url(imagen_url, SUPABASE_BUCKET_BUSES)
            if filename:
                supabase.storage.from_(SUPABASE_BUCKET_BUSES).remove([filename])
                logging.info(f"Imagen de bus eliminada: {filename}")
        except Exception as e:
            logging.error(f"Error eliminando imagen de bus: {e}")
    db.delete(bus)
    db.commit()
    db.close()
    return {"mensaje": "Bus eliminado"}

async def crear_bus_async(bus: dict, imagen: UploadFile):
    imagen_url = None
    if imagen:
        result = await save_file(imagen, to_supabase=True)
        if "url" in result:
            imagen_url = result["url"].get("publicUrl") if isinstance(result["url"], dict) else result["url"]
        elif "error" in result:
            logging.error(f"Error al subir imagen para nuevo bus: {result['error']}")

    def db_task():
        db: Session = SessionLocal()
        try:
            nuevo_bus = Bus(
                nombre_bus=bus.get("nombre_bus"),
                tipo=bus.get("tipo", "").lower().strip(),
                activo=bus.get("activo"),
                imagen=imagen_url
            )
            db.add(nuevo_bus)
            db.commit()
            db.refresh(nuevo_bus)
            return nuevo_bus
        except Exception as e:
            logging.error(f"Error creando bus en la base de datos: {e}")
            return None
        finally:
            db.close()

    return await asyncio.to_thread(db_task)

def actualizar_estado_bus(bus_id: int, nuevo_estado: bool):
    db: Session = SessionLocal()
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None
    bus.activo = nuevo_estado
    db.commit()
    db.close()
    return {"mensaje": f"Estado de bus actualizado a {'activo' if nuevo_estado else 'inactivo'}"}

def actualizar_imagen_bus(bus_id: int, imagen_url: str):
    db: Session = SessionLocal()
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None
    bus.imagen = imagen_url
    db.commit()
    db.refresh(bus)
    db.close()
    return bus


# ---------------------- ESTACION CRUD ----------------------
def obtener_estaciones(estacion_id: Optional[int] = None, sector: Optional[str] = None, activo: Optional[bool] = None):
    db: Session = SessionLocal()
    query = db.query(Estacion)
    if estacion_id is not None:
        query = query.filter(Estacion.id == estacion_id)
    if sector:
        sector_norm = normalize_string(sector)
        query = query.filter(Estacion.localidad.ilike(f"%{sector_norm}%"))
    if activo is not None:
        query = query.filter(Estacion.activo == activo)
    estaciones = query.all()
    db.close()
    return estaciones

def obtener_estacion_por_id(estacion_id: int):
    db: Session = SessionLocal()
    estacion = db.query(Estacion).filter(Estacion.id == estacion_id).first()
    db.close()
    return estacion

def actualizar_estacion(estacion_id: int, update_data: dict):
    logging.info(f"Actualizar estación {estacion_id} con datos: {update_data}")
    db: Session = SessionLocal()
    estacion = db.query(Estacion).filter(Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    try:
        if "imagen" in update_data and estacion.imagen:
            try:
                filename = get_supabase_path_from_url(estacion.imagen, SUPABASE_BUCKET_ESTACIONES)
                if filename:
                    supabase.storage.from_(SUPABASE_BUCKET_ESTACIONES).remove([filename])
            except Exception as e:
                logging.error(f"Error eliminando imagen antigua de estación: {e}")

        valid_keys = set(c.name for c in Estacion.__table__.columns)
        for key in list(update_data.keys()):
            if key not in valid_keys:
                update_data.pop(key)

        for key, value in update_data.items():
            setattr(estacion, key, value)
        db.commit()
        db.refresh(estacion)
    except Exception as e:
        logging.error(f"Error actualizando estación {estacion_id}: {e}")
        db.rollback()
        estacion = None
    finally:
        db.close()
    return estacion

def eliminar_estacion(estacion_id: int):
    db: Session = SessionLocal()
    estacion = db.query(Estacion).filter(Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    imagen_url = estacion.imagen
    if imagen_url:
        try:
            filename = get_supabase_path_from_url(imagen_url, SUPABASE_BUCKET_ESTACIONES)
            if filename:
                supabase.storage.from_(SUPABASE_BUCKET_ESTACIONES).remove([filename])
        except Exception as e:
            logging.error(f"Error deleting estacion image: {e}")
    db.delete(estacion)
    db.commit()
    db.close()
    return {"mensaje": "Estación eliminada"}

async def crear_estacion_async(estacion: dict, imagen: Optional[UploadFile]) -> Optional[Estacion]:
    imagen_url = None
    if imagen:
        try:
            result = await save_file(imagen, to_supabase=True)
            if "url" in result:
                imagen_url = result["url"].get("publicUrl") if isinstance(result["url"], dict) else result["url"]
            elif "error" in result:
                logging.error(f"Error al subir imagen de estación: {result['error']}")
        except Exception as e:
            logging.error(f"Excepción al subir imagen de estación: {e}")

    def db_task():
        db: Session = SessionLocal()
        try:
            nueva_estacion = Estacion(
                nombre_estacion=estacion.get("nombre_estacion"),
                localidad=estacion.get("localidad"),
                rutas_asociadas=estacion.get("rutas_asociadas"),
                activo=estacion.get("activo"),
                imagen=imagen_url
            )
            db.add(nueva_estacion)
            db.commit()
            db.refresh(nueva_estacion)
            return nueva_estacion
        except Exception as e:
            logging.error(f"Error creando estación en la base de datos: {e}")
            return None
        finally:
            db.close()

    return await asyncio.to_thread(db_task)

def actualizar_estado_estacion(estacion_id: int, nuevo_estado: bool):
    db: Session = SessionLocal()
    estacion = db.query(Estacion).filter(Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    estacion.activo = nuevo_estado
    db.commit()
    db.close()
    return {"mensaje": f"Estado de estación actualizado a {'activo' if nuevo_estado else 'inactivo'}"}

def actualizar_imagen_estacion(estacion_id: int, imagen_url: str):
    db: Session = SessionLocal()
    estacion = db.query(Estacion).filter(Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    estacion.imagen = imagen_url
    db.commit()
    db.refresh(estacion)
    db.close()
    return estacion
