import logging
from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Bus, Estacion
from app.services.supabase_client import supabase, save_file, delete_file 
from app.schemas import schemas as schemas_schemas
from app.operations import crud

SUPABASE_BUCKET_BUSES = "buses"
SUPABASE_BUCKET_ESTACIONES = "estaciones"

def get_supabase_path_from_url(url: str, bucket_name: str) -> str:
    """Extract the path inside the bucket from a public Supabase URL."""
    parts = url.split(f"/public/{bucket_name}/")
    if len(parts) > 1:
        return parts[-1]
    return ""

async def actualizar_bus_db_form(bus_id: int, bus_update: BusUpdateForm, session: AsyncSession) -> Bus:
    result = await session.execute(select(Bus).where(Bus.id == bus_id))
    bus = result.scalar_one_or_none()
    if bus is None:
        raise HTTPException(status_code=404, detail="Bus no encontrado")

    imagen_actual = bus.imagen
    nueva_imagen_url: Optional[str] = None

    # Subir imagen si viene nueva
    if bus_update.imagen:
        # Pasa el bucket_name a save_file
        resultado = await save_file(bus_update.imagen, to_supabase=True, bucket_name=SUPABASE_BUCKET_BUSES)
        if "url" in resultado:
            nueva_imagen_url = resultado["url"]
            if imagen_actual:
                path_antiguo = get_supabase_path_from_url(imagen_actual, SUPABASE_BUCKET_BUSES)
                if path_antiguo:
                    # Usa la nueva función delete_file para eliminar la imagen antigua
                    await delete_file(path_antiguo, SUPABASE_BUCKET_BUSES)
        else:
            print("Error al subir nueva imagen:", resultado.get("error"))

    for campo in ['nombre_bus', 'tipo', 'activo']:
        valor = getattr(bus_update, campo)
        if valor is not None:
            setattr(bus, campo, valor)

    if nueva_imagen_url is not None:
        bus.imagen = nueva_imagen_url
    elif bus_update.imagen is None and imagen_actual: # Si no se envía nueva imagen y hay una actual, significa que se quiere eliminar
        # Aquí puedes agregar lógica para eliminar la imagen si se envía un campo vacío o un indicador de eliminación
        # Por ahora, si no se envía nueva imagen, la existente se mantiene.
        pass

    session.add(bus)
    await session.commit()
    await session.refresh(bus)
    return bus

async def actualizar_estacion_db_form(estacion_id: int, estacion_update: EstacionUpdateForm, session: AsyncSession) -> Estacion:
    result = await session.execute(select(Estacion).where(Estacion.id == estacion_id))
    estacion = result.scalar_one_or_none()
    if estacion is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    imagen_actual = estacion.imagen
    nueva_imagen_url: Optional[str] = None

    if estacion_update.imagen:
        # Pasa el bucket_name a save_file
        resultado = await save_file(estacion_update.imagen, to_supabase=True, bucket_name=SUPABASE_BUCKET_ESTACIONES)
        if "url" in resultado:
            nueva_imagen_url = resultado["url"]
            if imagen_actual:
                # Usa la nueva función delete_file para eliminar la imagen antigua
                await delete_file(imagen_actual, SUPABASE_BUCKET_ESTACIONES)
        else:
            print("Error al subir nueva imagen:", resultado.get("error"))

    for campo in ['nombre_estacion', 'localidad', 'rutas_asociadas', 'activo']:
        valor = getattr(estacion_update, campo)
        if valor is not None:
            setattr(estacion, campo, valor)

    if nueva_imagen_url is not None:
        estacion.imagen = nueva_imagen_url
    elif estacion_update.imagen is None and imagen_actual: # Si no se envía nueva imagen y hay una actual, significa que se quiere eliminar
        # Similar al bus, si no se envía nueva imagen, la existente se mantiene.
        pass

    session.add(estacion)
    await session.commit()
    await session.refresh(estacion)
    return estacion