# crud.py
import logging
import unicodedata
from typing import Optional, List
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession # Usar AsyncSession
from sqlalchemy.future import select # Para consultas asíncronas
from sqlalchemy import func
from app.models.models import Bus, Estacion
from app.services.supabase_client import supabase, save_file

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
async def obtener_buses(
    session: AsyncSession, 
    bus_id: Optional[int] = None,
    tipo: Optional[str] = None,
    activo: Optional[bool] = None
) -> List[Bus]:
    query = select(Bus)
    if bus_id is not None:
        query = query.where(Bus.id == bus_id)
    if tipo is not None:
        query = query.where(Bus.tipo == tipo)
    if activo is not None:
        query = query.where(Bus.activo == activo)
    
    result = await session.execute(query)
    return result.scalars().all()

async def crear_bus(
    session: AsyncSession,
    nombre_bus: str,
    tipo: str,
    activo: bool,
    imagen: Optional[UploadFile] = None
) -> Optional[Bus]:
    try:
        new_bus = Bus(
            nombre_bus=nombre_bus,
            tipo=tipo,
            activo=activo,
            imagen=None
        )

        if imagen:
            result = await save_file(imagen, to_supabase=True, bucket_name=SUPABASE_BUCKET_ESTACIONES)
            if "url" in result:
                new_bus.imagen = result["url"]
            else:
                logging.error(f"Error al subir imagen para bus: {result.get('error', 'Unknown error')}")
                return None

        session.add(new_bus)
        await session.commit()
        await session.refresh(new_bus)
        return new_bus
    except Exception as e:
        logging.error(f"Error creando bus en la base de datos: {e}")
        await session.rollback() 
        return None

async def eliminar_bus(session: AsyncSession, bus_id: int) -> bool: 
    bus = await session.execute(select(Bus).where(Bus.id == bus_id))
    bus_to_delete = bus.scalar_one_or_none()
    if bus_to_delete:
        if bus_to_delete.imagen:
            try:
                path_to_delete = get_supabase_path_from_url(bus_to_delete.imagen, SUPABASE_BUCKET_BUSES)
                if path_to_delete:
                    supabase.storage.from_(SUPABASE_BUCKET_BUSES).remove([path_to_delete])
                    logging.info(f"Imagen {path_to_delete} eliminada de Supabase.")
            except Exception as e:
                logging.error(f"Error al eliminar imagen de Supabase para bus {bus_id}: {e}")
        
        await session.delete(bus_to_delete)
        await session.commit()
        return True
    return False

async def actualizar_estado_bus(session: AsyncSession, bus_id: int, nuevo_estado: bool) -> Optional[Bus]: 
    result = await session.execute(select(Bus).where(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    if not bus:
        return None
    bus.activo = nuevo_estado
    await session.commit()
    await session.refresh(bus)
    return bus

async def actualizar_imagen_bus(session: AsyncSession, bus_id: int, imagen_url: str) -> Optional[Bus]: 
    result = await session.execute(select(Bus).where(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    if not bus:
        return None
    bus.imagen = imagen_url
    await session.commit()
    await session.refresh(bus)
    return bus

async def get_all_bus_ids(session: AsyncSession) -> List[int]: 
    result = await session.execute(select(Bus.id))
    return result.scalars().all()


# ---------------------- ESTACION CRUD ----------------------
async def obtener_estaciones(
    session: AsyncSession, 
    estacion_id: Optional[int] = None,
    localidad: Optional[str] = None,
    activo: Optional[bool] = None
) -> List[Estacion]:
    query = select(Estacion)
    if estacion_id is not None:
        query = query.where(Estacion.id == estacion_id)
    if localidad is not None:
        query = query.where(func.lower(func.trim(Estacion.localidad)) == func.lower(func.trim(localidad)))
    if activo is not None:
        query = query.where(Estacion.activo == activo)
    
    query = query.order_by(Estacion.id.desc())
    result = await session.execute(query)
    return result.scalars().all()

async def crear_estacion(
    session: AsyncSession, 
    nombre_estacion: str,
    localidad: str,
    rutas_asociadas: str,
    activo: bool,
    imagen: Optional[UploadFile] = None
) -> Optional[Estacion]:
    try:
        nueva_estacion = Estacion(
            nombre_estacion=nombre_estacion,
            localidad=localidad,
            rutas_asociadas=rutas_asociadas,
            activo=activo,
            imagen=None
        )

        if imagen:
            result = await save_file(imagen, to_supabase=True, bucket_name=SUPABASE_BUCKET_ESTACIONES)
            if "url" in result:
                nueva_estacion.imagen = result["url"]
            else:
                logging.error(f"Error al subir imagen para estación: {result.get('error', 'Unknown error')}")
                return None

        session.add(nueva_estacion)
        await session.commit()
        await session.refresh(nueva_estacion)
        return nueva_estacion
    except Exception as e:
        logging.error(f"Error creando estación en la base de datos: {e}")
        await session.rollback() 
        return None

async def eliminar_estacion(session: AsyncSession, estacion_id: int) -> bool: 
    estacion = await session.execute(select(Estacion).where(Estacion.id == estacion_id))
    estacion_to_delete = estacion.scalar_one_or_none()
    if estacion_to_delete:
        if estacion_to_delete.imagen:
            try:
                path_to_delete = get_supabase_path_from_url(estacion_to_delete.imagen, SUPABASE_BUCKET_ESTACIONES)
                if path_to_delete:
                    supabase.storage.from_(SUPABASE_BUCKET_ESTACIONES).remove([path_to_delete])
                    logging.info(f"Imagen {path_to_delete} eliminada de Supabase.")
            except Exception as e:
                logging.error(f"Error al eliminar imagen de Supabase para estación {estacion_id}: {e}")
        
        await session.delete(estacion_to_delete)
        await session.commit()
        return True
    return False

async def actualizar_estado_estacion(session: AsyncSession, estacion_id: int, nuevo_estado: bool) -> Optional[Estacion]: 
    result = await session.execute(select(Estacion).where(Estacion.id == estacion_id))
    estacion = result.scalar_one_or_none()
    if not estacion:
        return None
    estacion.activo = nuevo_estado
    await session.commit()
    await session.refresh(estacion)
    return estacion

async def actualizar_imagen_estacion(session: AsyncSession, estacion_id: int, imagen_url: str) -> Optional[Estacion]: 
    result = await session.execute(select(Estacion).where(Estacion.id == estacion_id))
    estacion = result.scalar_one_or_none()
    if not estacion:
        return None
    estacion.imagen = imagen_url
    await session.commit()
    await session.refresh(estacion)
    return estacion

async def get_all_estacion_ids(session: AsyncSession) -> List[int]: 
    result = await session.execute(select(Estacion.id))
    return result.scalars().all()