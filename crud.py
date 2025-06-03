from sqlalchemy.exc import IntegrityError
from typing import Optional
import logging
import unicodedata
import asyncio
from supabase_client import supabase, save_file
from sqlalchemy.orm import Session
from db import SessionLocal
from fastapi import UploadFile
import models

# ---------------------- BUSES ----------------------

def actualizar_bus(bus_id: int, update_data: dict) -> Optional[models.Bus]:
    """
    Actualiza un bus en la base de datos, manejando la eliminación de la imagen antigua si se proporciona una nueva.

    :param bus_id: ID del bus a actualizar.
    :param update_data: Diccionario con los datos a actualizar.
    :return: Instancia del bus actualizado o None si no se encuentra o falla.
    """
    logging.info(f"Actualizar bus {bus_id} con datos: {update_data}")
    
    with SessionLocal() as db:
        bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
        if not bus:
            logging.warning(f"Bus {bus_id} no encontrado para actualizar")
            return None

        try:
            # Eliminar imagen antigua si se proporciona una nueva
            if "imagen" in update_data and bus.imagen:
                try:
                    bucket = "buses"
                    filename = bus.imagen.split(f"/{bucket}/")[-1]
                    supabase.storage.from_(bucket).remove([filename])
                    logging.info(f"Imagen antigua de bus eliminada: {filename}")
                except Exception as e:
                    logging.error(f"Error eliminando imagen antigua de bus: {e}")

            # Validar atributos antes de actualizar
            valid_attributes = {c.name for c in models.Bus.__table__.columns}
            for key, value in update_data.items():
                if key not in valid_attributes:
                    logging.warning(f"Atributo {key} no válido para Bus")
                    continue
                setattr(bus, key, value)

            db.commit()
            db.refresh(bus)
            return bus

        except IntegrityError as e:
            logging.error(f"Error de integridad actualizando bus {bus_id}: {e}")
            db.rollback()
            return None
        except Exception as e:
            logging.error(f"Error inesperado actualizando bus {bus_id}: {e}")
            db.rollback()
            return None

def actualizar_estado_bus(bus_id: int, nuevo_estado: bool) -> dict:
    """
    Actualiza el estado (activo/inactivo) de un bus.

    :param bus_id: ID del bus a actualizar.
    :param nuevo_estado: Nuevo estado (True para activo, False para inactivo).
    :return: Diccionario con mensaje de resultado.
    """
    with SessionLocal() as db:
        bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
        if not bus:
            logging.warning(f"Bus {bus_id} no encontrado para actualizar estado")
            return {"mensaje": f"Bus {bus_id} no encontrado"}
        
        try:
            bus.activo = nuevo_estado
            db.commit()
            return {"mensaje": f"Estado de bus actualizado a {'activo' if nuevo_estado else 'inactivo'}"}
        except Exception as e:
            logging.error(f"Error actualizando estado de bus {bus_id}: {e}")
            db.rollback()
            return {"mensaje": f"Error actualizando estado de bus: {str(e)}"}

def crear_bus(bus: dict, imagen_bytes: Optional[bytes] = None, imagen_filename: Optional[str] = None) -> Optional[models.Bus]:
    """
    Crea un nuevo bus en la base de datos.

    :param bus: Diccionario con los datos del bus.
    :param imagen_bytes: Bytes de la imagen a subir (opcional).
    :param imagen_filename: Nombre del archivo de la imagen (opcional).
    :return: Instancia del bus creado o None si falla.
    """
    imagen_url = None
    if imagen_bytes and imagen_filename:
        try:
            imagen_url = subir_imagen("buses", imagen_filename, imagen_bytes)
        except Exception as e:
            logging.error(f"Error subiendo imagen de bus: {e}")
            return None

    with SessionLocal() as db:
        try:
            nuevo_bus = models.Bus(
                nombre_bus=normalize_string(bus.get("nombre_bus", "")),
                tipo=normalize_string(bus.get("tipo", "").lower().strip()) if bus.get("tipo") else None,
                activo=bus.get("activo", True),
                imagen=imagen_url
            )
            db.add(nuevo_bus)
            db.commit()
            db.refresh(nuevo_bus)
            return nuevo_bus
        except Exception as e:
            logging.error(f"Error creando bus en la base de datos: {e}")
            db.rollback()
            return None

async def crear_bus_async(bus: dict, imagen: Optional[UploadFile]) -> Optional[models.Bus]:
    """
    Crea un nuevo bus de forma asíncrona, subiendo la imagen a Supabase si se proporciona.

    :param bus: Diccionario con los datos del bus.
    :param imagen: Archivo de imagen para subir (opcional).
    :return: Instancia del bus creado o None si falla.
    """
    imagen_url = None
    if imagen:
        try:
            result = await save_file(imagen, to_supabase=True)
            if "url" in result:
                imagen_url = result["url"]["publicUrl"] if isinstance(result["url"], dict) else result["url"]
            else:
                logging.error(f"Error al subir imagen de bus: {result.get('error', 'Desconocido')}")
                return None
        except Exception as e:
            logging.error(f"Excepción al subir imagen de bus: {e}")
            return None

    def db_task():
        with SessionLocal() as db:
            try:
                nuevo_bus = models.Bus(
                    nombre_bus=normalize_string(bus.get("nombre_bus", "")),
                    tipo=normalize_string(bus.get("tipo", "").lower().strip()) if bus.get("tipo") else None,
                    activo=bus.get("activo", True),
                    imagen=imagen_url
                )
                db.add(nuevo_bus)
                db.commit()
                db.refresh(nuevo_bus)
                return nuevo_bus
            except Exception as e:
                logging.error(f"Error creando bus en la base de datos: {e}")
                return None

    return await asyncio.to_thread(db_task)

def actualizar_imagen_bus(bus_id: int, imagen_url: str) -> Optional[models.Bus]:
    """
    Actualiza la imagen de un bus en la base de datos.

    :param bus_id: ID del bus a actualizar.
    :param imagen_url: Nueva URL de la imagen.
    :return: Instancia del bus actualizado o None si no se encuentra.
    """
    with SessionLocal() as db:
        bus = db.query(models.Bus).filter(models.Bus.id == bus_id).first()
        if not bus:
            logging.warning(f"Bus {bus_id} no encontrado para actualizar imagen")
            return None
        
        try:
            bus.imagen = imagen_url
            db.commit()
            db.refresh(bus)
            return bus
        except Exception as e:
            logging.error(f"Error actualizando imagen de bus {bus_id}: {e}")
            db.rollback()
            return None

# ---------------------- ESTACIONES ----------------------

def normalize_string(s: str) -> str:
    """
    Normaliza una cadena eliminando acentos y convirtiéndola a minúsculas.

    :param s: Cadena a normalizar.
    :return: Cadena normalizada.
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').strip()

def obtener_estaciones(sector: Optional[str] = None, activo: Optional[bool] = None) -> list[models.Estacion]:
    """
    Obtiene estaciones de la base de datos, con filtros opcionales por sector y estado.

    :param sector: Sector para filtrar (opcional).
    :param activo: Estado activo/inactivo para filtrar (opcional).
    :return: Lista de estaciones.
    """
    with SessionLocal() as db:
        query = db.query(models.Estacion)
        if sector:
            sector_norm = normalize_string(sector)
            query = query.filter(models.Estacion.localidad.ilike(f"%{sector_norm}%"))
        if activo is not None:
            query = query.filter(models.Estacion.activo == activo)
        estaciones = query.all()
        return estaciones

def obtener_estacion_por_id(estacion_id: int) -> Optional[models.Estacion]:
    """
    Obtiene una estación por su ID.

    :param estacion_id: ID de la estación.
    :return: Instancia de la estación o None si no se encuentra.
    """
    with SessionLocal() as db:
        estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
        return estacion

def eliminar_estacion(estacion_id: int) -> dict:
    """
    Elimina una estación de la base de datos y su imagen asociada en Supabase.

    :param estacion_id: ID de la estación a eliminar.
    :return: Diccionario con mensaje de resultado.
    """
    with SessionLocal() as db:
        estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
        if not estacion:
            logging.warning(f"Estación {estacion_id} no encontrada para eliminar")
            return {"mensaje": f"Estación {estacion_id} no encontrada"}

        try:
            # Eliminar imagen asociada si existe
            if estacion.imagen:
                try:
                    bucket = "estaciones"
                    filename = estacion.imagen.split(f"/{bucket}/")[-1]
                    supabase.storage.from_(bucket).remove([filename])
                    logging.info(f"Imagen de estación eliminada: {filename}")
                except Exception as e:
                    logging.error(f"Error eliminando imagen de estación: {e}")

            db.delete(estacion)
            db.commit()
            return {"mensaje": "Estación eliminada"}
        except Exception as e:
            logging.error(f"Error eliminando estación {estacion_id}: {e}")
            db.rollback()
            return {"mensaje": f"Error eliminando estación: {str(e)}"}

def actualizar_estado_estacion(estacion_id: int, nuevo_estado: bool) -> dict:
    """
    Actualiza el estado (activo/inactivo) de una estación.

    :param estacion_id: ID de la estación a actualizar.
    :param nuevo_estado: Nuevo estado (True para activo, False para inactivo).
    :return: Diccionario con mensaje de resultado.
    """
    with SessionLocal() as db:
        estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
        if not estacion:
            logging.warning(f"Estación {estacion_id} no encontrada para actualizar estado")
            return {"mensaje": f"Estación {estacion_id} no encontrada"}

        try:
            estacion.activo = nuevo_estado
            db.commit()
            return {"mensaje": f"Estado de estación actualizado a {'activo' if nuevo_estado else 'inactivo'}"}
        except Exception as e:
            logging.error(f"Error actualizando estado de estación {estacion_id}: {e}")
            db.rollback()
            return {"mensaje": f"Error actualizando estado de estación: {str(e)}"}

def actualizar_id_estacion(estacion_id: int, nuevo_id: int) -> dict:
    """
    Actualiza el ID de una estación.

    :param estacion_id: ID actual de la estación.
    :param nuevo_id: Nuevo ID para la estación.
    :return: Diccionario con mensaje de resultado.
    """
    with SessionLocal() as db:
        estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
        if not estacion:
            logging.warning(f"Estación {estacion_id} no encontrada para actualizar ID")
            return {"mensaje": f"Estación {estacion_id} no encontrada"}

        try:
            estacion.id = nuevo_id
            db.commit()
            return {"mensaje": f"ID de estación actualizado a {nuevo_id}"}
        except IntegrityError as e:
            logging.error(f"Error de integridad actualizando ID de estación {estacion_id}: {e}")
            db.rollback()
            return {"mensaje": f"Error actualizando ID: {str(e)}"}
        except Exception as e:
            logging.error(f"Error inesperado actualizando ID de estación {estacion_id}: {e}")
            db.rollback()
            return {"mensaje": f"Error actualizando ID: {str(e)}"}

def crear_estacion(estacion: dict, imagen_bytes: Optional[bytes] = None, imagen_filename: Optional[str] = None) -> Optional[models.Estacion]:
    """
    Crea una nueva estación en la base de datos.

    :param estacion: Diccionario con los datos de la estación.
    :param imagen_bytes: Bytes de la imagen a subir (opcional).
    :param imagen_filename: Nombre del archivo de la imagen (opcional).
    :return: Instancia de la estación creada o None si falla.
    """
    imagen_url = None
    if imagen_bytes and imagen_filename:
        try:
            imagen_url = subir_imagen("estaciones", imagen_filename, imagen_bytes)
        except Exception as e:
            logging.error(f"Error subiendo imagen de estación: {e}")
            return None

    with SessionLocal() as db:
        try:
            nueva_estacion = models.Estacion(
                nombre_estacion=normalize_string(estacion.get("nombre_estacion", "")),
                localidad=normalize_string(estacion.get("localidad", "")),
                rutas_asociadas=estacion.get("rutas_asociadas"),
                activo=estacion.get("activo", True),
                imagen=imagen_url
            )
            db.add(nueva_estacion)
            db.commit()
            db.refresh(nueva_estacion)
            return nueva_estacion
        except Exception as e:
            logging.error(f"Error creando estación en la base de datos: {e}")
            db.rollback()
            return None

async def crear_estacion_async(estacion: dict, imagen: Optional[UploadFile]) -> Optional[models.Estacion]:
    """
    Crea una nueva estación de forma asíncrona, subiendo la imagen a Supabase si se proporciona.

    :param estacion: Diccionario con los datos de la estación.
    :param imagen: Archivo de imagen para subir (opcional).
    :return: Instancia de la estación creada o None si falla.
    """
    imagen_url = None
    if imagen:
        try:
            result = await save_file(imagen, to_supabase=True)
            if "url" in result:
                imagen_url = result["url"]["publicUrl"] if isinstance(result["url"], dict) else result["url"]
            else:
                logging.error(f"Error al subir imagen de estación: {result.get('error', 'Desconocido')}")
                return None
        except Exception as e:
            logging.error(f"Excepción al subir imagen de estación: {e}")
            return None

    def db_task():
        with SessionLocal() as db:
            try:
                nueva_estacion = models.Estacion(
                    nombre_estacion=normalize_string(estacion.get("nombre_estacion", "")),
                    localidad=normalize_string(estacion.get("localidad", "")),
                    rutas_asociadas=estacion.get("rutas_asociadas"),
                    activo=estacion.get("activo", True),
                    imagen=imagen_url
                )
                db.add(nueva_estacion)
                db.commit()
                db.refresh(nueva_estacion)
                return nueva_estacion
            except Exception as e:
                logging.error(f"Error creando estación en la base de datos: {e}")
                return None

    return await asyncio.to_thread(db_task)

def actualizar_imagen_estacion(estacion_id: int, imagen_url: str) -> Optional[models.Estacion]:
    """
    Actualiza la imagen de una estación en la base de datos.

    :param estacion_id: ID de la estación a actualizar.
    :param imagen_url: Nueva URL de la imagen.
    :return: Instancia de la estación actualizada o None si no se encuentra.
    """
    with SessionLocal() as db:
        estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
        if not estacion:
            logging.warning(f"Estación {estacion_id} no encontrada para actualizar imagen")
            return None
        
        try:
            estacion.imagen = imagen_url
            db.commit()
            db.refresh(estacion)
            return estacion
        except Exception as e:
            logging.error(f"Error actualizando imagen de estación {estacion_id}: {e}")
            db.rollback()
            return None

def actualizar_estacion(estacion_id: int, update_data: dict) -> Optional[models.Estacion]:
    """
    Actualiza una estación en la base de datos, manejando la eliminación de la imagen antigua si se proporciona una nueva.

    :param estacion_id: ID de la estación a actualizar.
    :param update_data: Diccionario con los datos a actualizar.
    :return: Instancia de la estación actualizada o None si no se encuentra o falla.
    """
    logging.info(f"Actualizar estación {estacion_id} con datos: {update_data}")
    
    with SessionLocal() as db:
        estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion_id).first()
        if not estacion:
            logging.warning(f"Estación {estacion_id} no encontrada para actualizar")
            return None

        try:
            # Eliminar imagen antigua si se proporciona una nueva
            if "imagen" in update_data and estacion.imagen:
                try:
                    bucket = "estaciones"
                    filename = estacion.imagen.split(f"/{bucket}/")[-1]
                    supabase.storage.from_(bucket).remove([filename])
                    logging.info(f"Imagen antigua de estación eliminada: {filename}")
                except Exception as e:
                    logging.error(f"Error eliminando imagen antigua de estación: {e}")

            # Validar atributos antes de actualizar
            valid_attributes = {c.name for c in models.Estacion.__table__.columns}
            for key, value in update_data.items():
                if key not in valid_attributes:
                    logging.warning(f"Atributo {key} no válido para Estacion")
                    continue
                setattr(estacion, key, value)

            db.commit()
            db.refresh(estacion)
            return estacion

        except IntegrityError as e:
            logging.error(f"Error de integridad actualizando estación {estacion_id}: {e}")
            db.rollback()
            return None
        except Exception as e:
            logging.error(f"Error inesperado actualizando estación {estacion_id}: {e}")
            db.rollback()
            return None