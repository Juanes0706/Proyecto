import logging
import unicodedata
from supabase_client import supabase, save_file
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import SessionLocal, async_session
import models
from typing import Optional
from fastapi import HTTPException

async def actualizar_bus_async(bus_id: int, vehiculo_update, session: AsyncSession):
    result = await session.execute(select(models.Bus).where(models.Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    if bus is None:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    imagen_actual = bus.imagen
    nueva_imagen_url: Optional[str] = None
    if hasattr(vehiculo_update, "imagen") and vehiculo_update.imagen:
        resultado = await save_file(vehiculo_update.imagen, to_supabase=True)
        if "url" in resultado:
            nueva_imagen_url = resultado["url"]["publicUrl"] if isinstance(resultado["url"], dict) else resultado["url"]
            if imagen_actual:
                bucket = "buses"
                path_antiguo = imagen_actual.split(f"/{bucket}/")[-1]
                supabase.storage.from_(bucket).remove([path_antiguo])
        else:
            logging.error(f"Error al subir nueva imagen: {resultado.get('error')}")
    for campo in ["nombre_bus", "tipo", "activo"]:
        valor = getattr(vehiculo_update, campo)
        if valor is not None:
            setattr(bus, campo, valor)
    if nueva_imagen_url:
        bus.imagen = nueva_imagen_url
    session.add(bus)
    await session.commit()
    await session.refresh(bus)
    return bus

async def actualizar_estacion_async(estacion_id: int, vehiculo_update, session: AsyncSession):
    result = await session.execute(select(models.Estacion).where(models.Estacion.id == estacion_id))
    estacion = result.scalar_one_or_none()
    if estacion is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    imagen_actual = estacion.imagen
    nueva_imagen_url: Optional[str] = None
    if hasattr(vehiculo_update, "imagen") and vehiculo_update.imagen:
        resultado = await save_file(vehiculo_update.imagen, to_supabase=True)
        if "url" in resultado:
            nueva_imagen_url = resultado["url"]["publicUrl"] if isinstance(resultado["url"], dict) else resultado["url"]
            if imagen_actual:
                bucket = "estaciones"
                path_antiguo = imagen_actual.split(f"/{bucket}/")[-1]
                supabase.storage.from_(bucket).remove([path_antiguo])
        else:
            logging.error(f"Error al subir nueva imagen: {resultado.get('error')}")
    for campo in ["nombre_estacion", "localidad", "rutas_asociadas", "activo"]:
        valor = getattr(vehiculo_update, campo)
        if valor is not None:
            setattr(estacion, campo, valor)
    if nueva_imagen_url:
        estacion.imagen = nueva_imagen_url
    session.add(estacion)
    await session.commit()
    await session.refresh(estacion)
    return estacion

def obtener_buses(bus_id: Optional[int] = None, tipo: Optional[str] = None, activo: Optional[bool] = None):
    db: Session = SessionLocal()
    query = db.query(models.Bus)
    if bus_id is not None:
        query = query.filter(models.Bus.id == bus_id)
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

def actualizar_bus(bus_id: int, update_data: dict):
    logging.info(f"Actualizar bus {bus_id} con datos: {update_data}")
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    if not bus:
        db.close()
        logging.warning(f"Bus {bus_id} no encontrado para actualizar")
        return None
    try:
        # Delete old image if updating image
        if "imagen" in update_data and bus.imagen:
            try:
                bucket = "buses"
                filename = bus.imagen.split(f"/{bucket}/")[-1]
                supabase.storage.from_(bucket).remove([filename])
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

def actualizar_estacion(estacion_id: int, update_data: dict):
    logging.info(f"Actualizar estación {estacion_id} con datos: {update_data}")
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        logging.warning(f"Estación {estacion_id} no encontrada para actualizar")
        return None
    try:
        # Delete old image if updating image
        if "imagen" in update_data and estacion.imagen:
            try:
                bucket = "estaciones"
                filename = estacion.imagen.split(f"/{bucket}/")[-1]
                supabase.storage.from_(bucket).remove([filename])
                logging.info(f"Imagen antigua de estación eliminada: {filename}")
            except Exception as e:
                logging.error(f"Error eliminando imagen antigua de estación: {e}")

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
            logging.error(f"Error eliminando imagen de bus: {e}")
    db.delete(bus)
    db.commit()
    db.close()
    return {"mensaje": "Bus eliminado"}

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

import asyncio
from supabase_client import save_file
from fastapi import UploadFile

import asyncio

async def crear_bus_async(bus: dict, imagen: UploadFile):
    imagen_url = None
    if imagen:
        result = await save_file(imagen, to_supabase=True)
        if "url" in result:
            imagen_url = result["url"]["publicUrl"] if isinstance(result["url"], dict) else result["url"]
        elif "error" in result:
            # Log or handle error as needed
            imagen_url = None

    def db_task():
        db: Session = SessionLocal()
        try:
            nuevo_bus = models.Bus(
                nombre_bus=bus.get("nombre_bus"),
                tipo=bus.get("tipo").lower().strip() if bus.get("tipo") else None,
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

    nuevo_bus = await asyncio.to_thread(db_task)
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

def actualizar_bus(bus_id: int, update_data: dict):
    import logging
    logging.info(f"Actualizar bus {bus_id} con datos: {update_data}")
    db: Session = SessionLocal()
    bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
    if not bus:
        db.close()
        logging.warning(f"Bus {bus_id} no encontrado para actualizar")
        return None
    try:
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

# ---------------------- ESTACIONES ----------------------

def normalize_string(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()

def obtener_estaciones(estacion_id: Optional[int] = None, sector: Optional[str] = None, activo: Optional[bool] = None):
    db: Session = SessionLocal()
    query = db.query(models.Estacion)
    if estacion_id is not None:
        query = query.filter(models.Estacion.id == estacion_id)
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

import asyncio
from supabase_client import save_file
from fastapi import UploadFile

from fastapi import UploadFile
from typing import Optional

import asyncio

async def crear_estacion_async(estacion: dict, imagen: Optional[UploadFile]) -> Optional[models.Estacion]:
    """
    Crea una nueva estación de forma asíncrona, subiendo la imagen a Supabase si se proporciona.

    :param estacion: Diccionario con los datos de la estación.
    :param imagen: Archivo de imagen para subir (opcional).
    :return: Instancia de models.Estacion creada o None si falla la creación.
    """
    imagen_url = None
    if imagen:
        try:
            result = await save_file(imagen, to_supabase=True)
            if "url" in result:
                imagen_url = result["url"]["publicUrl"] if isinstance(result["url"], dict) else result["url"]
            elif "error" in result:
                logging.error(f"Error al subir imagen de estación: {result['error']}")
                imagen_url = None
        except Exception as e:
            logging.error(f"Excepción al subir imagen de estación: {e}")
            imagen_url = None

    def db_task():
        db: Session = SessionLocal()
        try:
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
            return nueva_estacion
        except Exception as e:
            logging.error(f"Error creando estación en la base de datos: {e}")
            return None
        finally:
            db.close()

    nueva_estacion = await asyncio.to_thread(db_task)
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

import logging
from supabase_client import supabase
from sqlalchemy.orm import Session
from db import SessionLocal
import models
from typing import Optional

def actualizar_estacion(estacion_id: int, update_data: dict):
    logging.info(f"Actualizar estación {estacion_id} con datos: {update_data}")
    db: Session = SessionLocal()
    estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
    if not estacion:
        db.close()
        logging.warning(f"Estación {estacion_id} no encontrada para actualizar")
        return None
    try:
        # Delete old image if updating image
        if "imagen" in update_data and estacion.imagen:
            try:
                bucket = "estaciones"
                filename = estacion.imagen.split(f"/{bucket}/")[-1]
                supabase.storage.from_(bucket).remove([filename])
                logging.info(f"Imagen antigua de estación eliminada: {filename}")
            except Exception as e:
                logging.error(f"Error eliminando imagen antigua de estación: {e}")

        # Remove duplicate keys that do not exist in model
        valid_keys = set(c.name for c in models.Estacion.__table__.columns)
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
