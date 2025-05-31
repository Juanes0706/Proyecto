from supabase_client import supabase
from typing import Optional
import unicodedata
import re
import uuid
from sqlalchemy.orm import Session
from db import SessionLocal
import models
import logging

def limpiar_nombre_archivo(nombre: str) -> str:
    nombre = unicodedata.normalize('NFD', nombre)
    nombre = nombre.encode('ascii', 'ignore').decode('utf-8')
    nombre = re.sub(r'\s+', '_', nombre)
    return nombre.lower()

def subir_imagen(bucket_name: str, file_name: str, file_bytes: bytes, content_type: str = "image/jpeg") -> Optional[str]:
    try:
        file_name = limpiar_nombre_archivo(file_name)
        # Opcional: evitar colisiones con UUID
        # file_name = f"{uuid.uuid4().hex}_{file_name}"

        response = supabase.storage.from_(bucket_name).upload(
            file_name,
            file_bytes,
            {"content-type": content_type},
            upsert=True
        )
        if response.get("error"):
            logging.error(f"Error subiendo imagen: {response['error']}")
            return None
        url = f"https://{supabase.supabase_url.replace('https://', '')}/storage/v1/object/public/{bucket_name}/{file_name}"
        logging.info(f"Imagen subida correctamente: {url}")
        return url
    except Exception as e:
        logging.error(f"Excepción al subir imagen: {e}")
        return None

# ---------------------- BUSES ----------------------

def obtener_buses(tipo: Optional[str] = None, activo: Optional[bool] = None):
    db: Session = SessionLocal()
    query = db.query(models.Bus)
    if tipo:
        query = query.filter(models.Bus.tipo.ilike(f"%{tipo}%"))
    if activo is not None:
        query = query.filter(models.Bus.activo == activo)
    buses = query.all()
    for bus in buses:
        if bus.tipo:
            bus.tipo = bus.tipo.strip().lower()
    db.close()
    return buses

def obtener_bus_por_id(bus_id: int):
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    db.close()
    return bus

def eliminar_bus(bus_id: int):
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None
    imagen_url = bus.imagen
    if imagen_url:
        try:
            bucket = "buses"
            filename = imagen_url.split(f"/{bucket}/")[-1]
            supabase.storage.from_(bucket).remove([filename])
            logging.info(f"Imagen de bus eliminada: {filename}")
        except Exception as e:
            logging.error(f"Error deleting bus image: {e}")
    db.delete(bus)
    db.commit()
    db.close()
    return {"mensaje": "Bus eliminado"}

def actualizar_estado_bus(bus_id: int, nuevo_estado: bool):
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None
    bus.activo = nuevo_estado
    db.commit()
    db.close()
    return {"mensaje": f"Estado de bus actualizado a {'activo' if nuevo_estado else 'inactivo'}"}

def crear_bus(bus: dict, imagen_bytes: Optional[bytes] = None, imagen_filename: Optional[str] = None):
    imagen_url = None
    if imagen_bytes and imagen_filename:
        imagen_url = subir_imagen("buses", imagen_filename, imagen_bytes)

    db: Session = SessionLocal()
    nuevo_bus = models.Bus(
        nombre_bus=bus.get("nombre_bus"),
        tipo=bus.get("tipo").lower().strip() if bus.get("tipo") else None,
        activo=bus.get("activo"),
        imagen=imagen_url
    )
    db.add(nuevo_bus)
    db.commit()
    db.refresh(nuevo_bus)
    db.close()
    return nuevo_bus

def actualizar_imagen_bus(bus_id: int, imagen_url: str):
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None
    bus.imagen = imagen_url
    db.commit()
    db.refresh(bus)
    db.close()
    return bus

# ---------------------- ESTACIONES ----------------------

def normalize_string(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()

def obtener_estaciones(sector: Optional[str] = None, activo: Optional[bool] = None):
    db: Session = SessionLocal()
    query = db.query(models.Estacion)
    if sector:
        sector_norm = normalize_string(sector)
        query = query.filter(models.Estacion.localidad.ilike(f"%{sector_norm}%"))
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

def eliminar_estacion(estacion_id: int):
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    imagen_url = estacion.imagen
    if imagen_url:
        try:
            bucket = "estaciones"
            filename = imagen_url.split(f"/{bucket}/")[-1]
            supabase.storage.from_(bucket).remove([filename])
            logging.info(f"Imagen de estación eliminada: {filename}")
        except Exception as e:
            logging.error(f"Error deleting estacion image: {e}")
    db.delete(estacion)
    db.commit()
    db.close()
    return {"mensaje": "Estación eliminada"}

def actualizar_estado_estacion(estacion_id: int, nuevo_estado: bool):
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    estacion.activo = nuevo_estado
    db.commit()
    db.close()
    return {"mensaje": f"Estado de estación actualizado a {'activo' if nuevo_estado else 'inactivo'}"}

def actualizar_id_estacion(estacion_id: int, nuevo_id: int):
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    estacion.id = nuevo_id
    db.commit()
    db.close()
    return {"mensaje": f"ID de estación actualizado a {nuevo_id}"}

def crear_estacion(estacion: dict, imagen_bytes: Optional[bytes] = None, imagen_filename: Optional[str] = None):
    imagen_url = None
    if imagen_bytes and imagen_filename:
        imagen_url = subir_imagen("estaciones", imagen_filename, imagen_bytes)

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

def actualizar_imagen_estacion(estacion_id: int, imagen_url: str):
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    estacion.imagen = imagen_url
    db.commit()
    db.refresh(estacion)
    db.close()
    return estacion

def actualizar_bus(bus_id: int, update_data: dict):
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    if not bus:
        db.close()
        return None
    for key, value in update_data.items():
        setattr(bus, key, value)
    db.commit()
    db.refresh(bus)
    db.close()
    return bus

def actualizar_estacion(estacion_id: int, update_data: dict):
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        return None
    for key, value in update_data.items():
        setattr(estacion, key, value)
    db.commit()
    db.refresh(estacion)
    db.close()
    return estacion
