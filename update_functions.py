import logging
from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models
from models import Bus, Estacion
from supabase_client import supabase, save_file
from schemas import * 
from crud import* 

SUPABASE_BUCKET_BUSES = "buses"
SUPABASE_BUCKET_ESTACIONES = "estaciones"

def get_supabase_path_from_url(url: str, bucket_name: str) -> str:
    """Extract the path inside the bucket from a public Supabase URL."""
    parts = url.split(f"/public/{bucket_name}/")
    if len(parts) > 1:
        return parts[-1]
    return ""

async def actualizar_bus_db_form(bus_id: int, bus_update:BusUpdateForm, session: AsyncSession) -> Bus:
    result = await session.execute(select(Bus).where(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    if bus is None:
        raise HTTPException(status_code=404, detail="Bus no encontrado")

    imagen_actual = bus.imagen
    nueva_imagen_url: Optional[str] = None

    if bus_update.imagen:
        resultado = await save_file(bus_update.imagen, to_supabase=True)

        if "url" in resultado:
            nueva_imagen_url = resultado["url"]
            if imagen_actual:
                path_antiguo = get_supabase_path_from_url(imagen_actual, SUPABASE_BUCKET)
                supabase.storage.from_(SUPABASE_BUCKET).remove([path_antiguo])
        else:
            print("Error al subir nueva imagen:", resultado.get("error"))
    for campo in [ 'nombre_bus', 'tipo', 'activo']:
        valor = getattr(bus_update, campo)
        if valor is not None:
            setattr(bus, campo, valor)
    if nueva_imagen_url:
        bus.imagen = nueva_imagen_url

    session.add(bus)
    await session.commit()
    await session.refresh(bus)
    return bus



def get_supabase_path_from_url(url: str, bucket_name: str) -> str:
    """Extract the path inside the bucket from a public Supabase URL."""
    parts = url.split(f"/public/{bucket_name}/")
    if len(parts) > 1:
        return parts[-1]
    return ""

async def actualizar_estacion_db_form(estacion_id: int, estacion_update:EstacionUpdateForm, session: AsyncSession) -> Estacion:
    result = await session.execute(select(Estacion).where(Estacion.id == estacion_id))
    Estacion = result.scalar_one_or_none()
    if Estacion is None:
        raise HTTPException(status_code=404, detail="Estacion no encontrada")

    imagen_actual = Estacion.imagen
    nueva_imagen_url: Optional[str] = None

    if estacion_update.imagen:
        resultado = await save_file(estacion_update.imagen, to_supabase=True)

        if "url" in resultado:
            nueva_imagen_url = resultado["url"]
            if imagen_actual:
                path_antiguo = get_supabase_path_from_url(imagen_actual, SUPABASE_BUCKET)
                supabase.storage.from_(SUPABASE_BUCKET).remove([path_antiguo])
        else:
            print("Error al subir nueva imagen:", resultado.get("error"))
    for campo in [ 'nombre_estacion', 'localidad', 'rutas_asociadas', 'activo']:
        valor = getattr(estacion_update, campo)
        if valor is not None:
            setattr(Estacion, campo, valor)
    if nueva_imagen_url:
        Estacion.imagen_url = nueva_imagen_url

    session.add(Estacion)
    await session.commit()
    await session.refresh(Estacion)
    return Estacion
