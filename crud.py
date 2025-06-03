import logging
from supabase_client import supabase
from sqlalchemy.orm import Session
from db import SessionLocal
import models

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
    return estacion
