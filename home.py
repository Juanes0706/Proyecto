# home.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
# from sqlalchemy.orm import Session # Ya no se usa
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
from app.operations import crud
from app import models
from app.schemas.schemas import Bus as BusSchema, Estacion as EstacionSchema, BusResponse, EstacionResponse
from app.schemas.schemas import BusUpdateForm, EstacionUpdateForm, BusCreateForm, EstacionCreateForm
from app.database.db import async_session, get_async_db # Importar get_async_db
from app.services.update_functions import actualizar_estacion_db_form, actualizar_bus_db_form
import logging
from datetime import datetime

router = APIRouter()

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

historial_eliminados = []


# -------------------- HTML ROUTES --------------------

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root_html(request: Request):
    return templates.TemplateResponse("CrudAppPage.html", {"request": request})

@router.get("/create", response_class=HTMLResponse)
async def create_html(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@router.get("/update", response_class=HTMLResponse)
async def update_html(request: Request):
    return templates.TemplateResponse("update.html", {"request": request})

@router.get("/delete", response_class=HTMLResponse)
async def delete_html(request: Request):
    return templates.TemplateResponse("delete.html", {"request": request})


# -------------------- BUS API --------------------
@router.get("/buses", response_model=List[BusResponse], tags=["Buses"])
async def get_buses(
    bus_id: Optional[int] = None,
    tipo: Optional[str] = None,
    activo: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_db) 
):
    buses = await crud.obtener_buses(session, bus_id, tipo, activo) 
    return [BusResponse.from_orm(bus) for bus in buses]

@router.post("/buses", response_model=BusResponse, status_code=status.HTTP_201_CREATED, tags=["Buses"])
async def create_bus(
    bus_create: BusCreateForm = Depends(),
    session: AsyncSession = Depends(get_async_db) 
):
    new_bus = await crud.crear_bus( 
        session,
        bus_create.nombre_bus,
        bus_create.tipo,
        bus_create.activo,
        bus_create.imagen
    )
    if not new_bus:
        raise HTTPException(status_code=400, detail="Error al crear bus")
    return BusResponse.from_orm(new_bus)

@router.delete("/buses/{bus_id}", tags=["Buses"])
async def delete_bus(
    bus_id: int,
    session: AsyncSession = Depends(get_async_db) # Usar get_async_db
):
    bus_to_delete = await crud.obtener_buses(session, bus_id=bus_id) 
    if not bus_to_delete:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    
    bus_obj = bus_to_delete[0] if bus_to_delete else None

    if not bus_obj:
        raise HTTPException(status_code=404, detail="Bus no encontrado")

    resultado = await crud.eliminar_bus(session, bus_id) 
    if not resultado:
        raise HTTPException(status_code=404, detail="Error al eliminar el bus")
    
    historial_eliminados.append({
        "tipo": "bus",
        "id": bus_obj.id,
        "nombre_bus": bus_obj.nombre_bus,
        "tipo_bus": bus_obj.tipo,
        "fecha_hora": datetime.now().isoformat()
    })
    return {"mensaje": "Bus eliminado"}

@router.post("/buses/update/{bus_id}", tags=["Buses"])
async def actualizar_bus_post(
    bus_id: int,
    bus_update: BusUpdateForm = Depends(),
    session: AsyncSession = Depends(get_async_db) 
):
    await actualizar_bus_db_form(bus_id, bus_update, session)
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)


# -------------------- ESTACION API --------------------
@router.get("/estaciones", response_model=List[EstacionResponse], tags=["Estaciones"])
async def get_estaciones(
    estacion_id: Optional[int] = None,
    localidad: Optional[str] = None,
    activo: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_db) 
):
    estaciones = await crud.obtener_estaciones(session, estacion_id, localidad, activo) 
    return [EstacionResponse.from_orm(estacion) for estacion in estaciones]

@router.post("/estaciones", response_model=EstacionResponse, status_code=status.HTTP_201_CREATED, tags=["Estaciones"])
async def create_estacion(
    estacion_create: EstacionCreateForm = Depends(),
    session: AsyncSession = Depends(get_async_db) # Usar get_async_db
):
    new_estacion = await crud.crear_estacion( 
        session,
        estacion_create.nombre_estacion,
        estacion_create.localidad,
        estacion_create.rutas_asociadas,
        estacion_create.activo,
        estacion_create.imagen
    )
    if not new_estacion:
        raise HTTPException(status_code=400, detail="Error al crear estación")
    return EstacionResponse.from_orm(new_estacion)

@router.delete("/estaciones/{estacion_id}", tags=["Estaciones"])
async def delete_estacion(
    estacion_id: int,
    session: AsyncSession = Depends(get_async_db) 
):
    estacion_to_delete_list = await crud.obtener_estaciones(session, estacion_id=estacion_id) 
    if not estacion_to_delete_list:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    estacion_obj = estacion_to_delete_list[0] if estacion_to_delete_list else None

    if not estacion_obj:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    resultado = await crud.eliminar_estacion(session, estacion_id) 
    if not resultado:
        raise HTTPException(status_code=404, detail="Error al eliminar la estación")
    
    historial_eliminados.append({
        "tipo": "estacion",
        "id": estacion_obj.id,
        "nombre_estacion": estacion_obj.nombre_estacion,
        "localidad": estacion_obj.localidad,
        "fecha_hora": datetime.now().isoformat()
    })
    return {"mensaje": "Estación eliminada"}

@router.post("/estaciones/update/{estacion_id}", tags=["Estaciones"])
async def actualizar_estacion_post(
    estacion_id: int,
    estacion_update: EstacionUpdateForm = Depends(),
    session: AsyncSession = Depends(get_async_db) 
):
    await actualizar_estacion_db_form(estacion_id, estacion_update, session)
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)


# -------------------- Historial API --------------------
class HistorialItem(BaseModel):
    tipo: str
    id: int
    nombre_bus: Optional[str] = None
    tipo_bus: Optional[str] = None
    nombre_estacion: Optional[str] = None
    localidad: Optional[str] = None
    fecha_hora: str

@router.get("/historial", response_model=List[HistorialItem], tags=["Historial"])
async def get_historial():
    return historial_eliminados