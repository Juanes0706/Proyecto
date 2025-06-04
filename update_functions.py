import logging
from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models
from models import Bus, Estacion
from supabase_client import supabase, save_file

SUPABASE_BUCKET_BUSES = "buses"
SUPABASE_BUCKET_ESTACIONES = "estaciones"

def get_supabase_path_from_url(url: str, bucket_name: str) -> str:
    """Extract the path inside the bucket from a public Supabase URL."""
    parts = url.split(f"/public/{bucket_name}/")
    if len(parts) > 1:
        return parts[-1]
    return ""

async def actualizar_bus_db_form(bus_id: int, bus_update, session: AsyncSession):
    result = await session.execute(select(Bus).where(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    if bus is None:
        raise HTTPException(status_code=404, detail="Bus no encontrado")

    imagen_actual = bus.imagen
    nueva_imagen_url: Optional[str] = None

    if bus_update.imagen:
        try:
            resultado = await save_file(bus_update.imagen, to_supabase=True)

            if "url" in resultado:
                if isinstance(resultado["url"], dict) and "publicUrl" in resultado["url"]:
                    nueva_imagen_url = resultado["url"]["publicUrl"]
                else:
                    nueva_imagen_url = resultado["url"]

                if imagen_actual:
                    try:
                        path_antiguo = get_supabase_path_from_url(imagen_actual, SUPABASE_BUCKET_BUSES)
                        if path_antiguo:
                            supabase.storage.from_(SUPABASE_BUCKET_BUSES).remove([path_antiguo])
                            logging.info(f"Imagen antigua de bus eliminada: {path_antiguo}")
                    except Exception as e:
                        logging.error(f"Error eliminando imagen antigua de bus: {e}")
            else:
                logging.error(f"Error al subir nueva imagen para bus {bus_id}: {resultado.get('error')}")
        except Exception as e:
            logging.error(f"Excepción al subir nueva imagen para bus {bus_id}: {e}")

    # Update fields, treating empty strings as None
    if bus_update.nombre_bus is not None and bus_update.nombre_bus != "":
        bus.nombre_bus = bus_update.nombre_bus
    if bus_update.tipo is not None and bus_update.tipo != "":
        bus.tipo = bus_update.tipo
    if bus_update.activo is not None and bus_update.activo != "":
        bus.activo = bus_update.activo.lower() == 'true'

    if nueva_imagen_url:
        bus.imagen = nueva_imagen_url

    session.add(bus)
    await session.commit()
    await session.refresh(bus)
    return bus

async def actualizar_estacion_db_form(estacion_id: int, estacion_update, session: AsyncSession):
    result = await session.execute(select(Estacion).where(Estacion.id == estacion_id))
    estacion = result.scalar_one_or_none()
    if estacion is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    imagen_actual = estacion.imagen
    nueva_imagen_url: Optional[str] = None

    if estacion_update.imagen:
        try:
            resultado = await save_file(estacion_update.imagen, to_supabase=True)

            if "url" in resultado:
                if isinstance(resultado["url"], dict) and "publicUrl" in resultado["url"]:
                    nueva_imagen_url = resultado["url"]["publicUrl"]
                else:
                    nueva_imagen_url = resultado["url"]

                if imagen_actual:
                    try:
                        path_antiguo = get_supabase_path_from_url(imagen_actual, SUPABASE_BUCKET_ESTACIONES)
                        if path_antiguo:
                            supabase.storage.from_(SUPABASE_BUCKET_ESTACIONES).remove([path_antiguo])
                            logging.info(f"Imagen antigua de estación eliminada: {path_antiguo}")
                    except Exception as e:
                        logging.error(f"Error eliminando imagen antigua de estación: {e}")
            else:
                logging.error(f"Error al subir nueva imagen para estación {estacion_id}: {resultado.get('error')}")
        except Exception as e:
            logging.error(f"Excepción al subir nueva imagen para estación {estacion_id}: {e}")

    # Update fields, treating empty strings as None
    if estacion_update.nombre_estacion is not None and estacion_update.nombre_estacion != "":
        estacion.nombre_estacion = estacion_update.nombre_estacion
    if estacion_update.localidad is not None and estacion_update.localidad != "":
        estacion.localidad = estacion_update.localidad
    if estacion_update.rutas_asociadas is not None and estacion_update.rutas_asociadas != "":
        estacion.rutas_asociadas = estacion_update.rutas_asociadas
    if estacion_update.activo is not None and estacion_update.activo != "":
        estacion.activo = estacion_update.activo.lower() == 'true'

    if nueva_imagen_url:
        estacion.imagen = nueva_imagen_url

    session.add(estacion)
    await session.commit()
    await session.refresh(estacion)
    return estacion
