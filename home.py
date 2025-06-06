# home.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
from app.operations import crud
from app import models 
from app.schemas.schemas import Bus as BusSchema, Estacion as EstacionSchema, BusResponse, EstacionResponse
from app.schemas.schemas import BusUpdateForm, EstacionUpdateForm, BusCreateForm, EstacionCreateForm
from app.database.db import get_async_db 
from app.services.update_functions import actualizar_estacion_db_form, actualizar_bus_db_form
import logging
from datetime import datetime
from fastapi.templating import Jinja2Templates

router = APIRouter()

class CreateBusResponse(BaseModel):
    message: str
    bus: BusResponse

class CreateEstacionResponse(BaseModel):
    message: str
    estacion: EstacionResponse

templates = Jinja2Templates(directory="templates")

historial_eliminados = []


# -------------------- HTML ROUTES --------------------

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root_html(request: Request):
    return templates.TemplateResponse("CrudAppPage.html", {"request": request})

@router.get("/create", response_class=HTMLResponse, tags=["HTML Pages"])
async def create_html(request: Request):
    return templates.TemplateResponse("CreatePage.html", {"request": request}) # Cambiado a CreatePage.html

@router.get("/update", response_class=HTMLResponse, tags=["HTML Pages"])
async def update_html(request: Request):
    return templates.TemplateResponse("UpdatePage.html", {"request": request}) # Cambiado a UpdatePage.html

@router.get("/delete", response_class=HTMLResponse, tags=["HTML Pages"])
async def delete_html(request: Request):
    return templates.TemplateResponse("DeletePage.html", {"request": request}) # Cambiado a DeletePage.html

@router.get("/read", response_class=HTMLResponse, tags=["HTML Pages"])
async def read_html(request: Request, session: AsyncSession = Depends(get_async_db)):
    """Muestra una página HTML con la lista de buses y estaciones."""
    buses = await crud.obtener_buses(session)
    estaciones = await crud.obtener_estaciones(session)
    return templates.TemplateResponse(
        "ReadPage.html", 
        {"request": request, "buses": buses, "estaciones": estaciones}
    )

@router.get("/informacion-del-proyecto", response_class=HTMLResponse, tags=["HTML Pages"])
async def project_info_html(request: Request):
    """Muestra una página HTML con información sobre el proyecto."""
    return templates.TemplateResponse("informacion_del_proyecto.html", {"request": request})

@router.get("/developer-info", response_class=HTMLResponse, tags=["HTML Pages"])
async def developer_info_html(request: Request):
    """Muestra una página HTML con información del desarrollador."""
    return templates.TemplateResponse("DeveloperInfoPage.html", {"request": request})

@router.get("/planning", response_class=HTMLResponse, tags=["HTML Pages"])
async def planning_html(request: Request):
    """Muestra una página HTML con la planificación del proyecto."""
    return templates.TemplateResponse("PlanningPage.html", {"request": request})

@router.get("/design", response_class=HTMLResponse, tags=["HTML Pages"])
async def design_html(request: Request):
    """Muestra una página HTML con el diseño del proyecto."""
    return templates.TemplateResponse("DesignPage.html", {"request": request})

@router.get("/historial", response_class=HTMLResponse, tags=["HTML Pages"])
async def historial_html(request: Request):
    """Muestra la página HTML del historial de eliminaciones."""
    return templates.TemplateResponse("HistorialPage.html", {"request": request})

@router.get("/edit-bus/{bus_id}", response_class=HTMLResponse, tags=["HTML Pages"])
async def edit_bus_html(request: Request, bus_id: int, session: AsyncSession = Depends(get_async_db)):
    """Muestra la página de edición unificada para un bus específico."""
    buses = await crud.obtener_buses(session, bus_id=bus_id) # Usa obtener_buses
    bus = buses[0] if buses else None # Obtiene el primer bus si existe
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado para edición.")
    return templates.TemplateResponse("EditUnifiedPage.html", {"request": request, "bus": bus})

@router.get("/edit", response_class=HTMLResponse, tags=["HTML Pages"])
async def edit_redirect(request: Request, bus_id: int = None, estacion_id: int = None):
    """Redirige la ruta /edit?bus_id= o /edit?estacion_id= a la ruta correcta para compatibilidad."""
    if bus_id is not None:
        return RedirectResponse(url=f"/edit-bus/{bus_id}", status_code=302)
    elif estacion_id is not None:
        return RedirectResponse(url=f"/edit-estacion/{estacion_id}", status_code=302)
    else:
        raise HTTPException(status_code=400, detail="Se requiere el parámetro bus_id o estacion_id")

@router.get("/edit-estacion/{estacion_id}", response_class=HTMLResponse, tags=["HTML Pages"])
async def edit_estacion_html(request: Request, estacion_id: int, session: AsyncSession = Depends(get_async_db)):
    """Muestra la página de edición unificada para una estación específica."""
    estaciones = await crud.obtener_estaciones(session, estacion_id=estacion_id) # Usa obtener_estaciones
    estacion = estaciones[0] if estaciones else None # Obtiene la primera estación si existe
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada para edición.")
    return templates.TemplateResponse("EditUnifiedPage.html", {"request": request, "estacion": estacion})

@router.get("/edit-estacion", response_class=HTMLResponse, tags=["HTML Pages"])
async def edit_estacion_redirect(request: Request, estacion_id: int = None):
    """Redirige la ruta /edit-estacion?estacion_id= a /edit-estacion/{estacion_id} para compatibilidad."""
    if estacion_id is not None:
        return RedirectResponse(url=f"/edit-estacion/{estacion_id}", status_code=302)
    else:
        raise HTTPException(status_code=400, detail="Se requiere el parámetro estacion_id")


# -------------------- BUS API --------------------
@router.get("/buses", response_model=List[BusResponse], tags=["Buses API"])
async def get_buses_api(
    bus_id: Optional[int] = None,
    tipo: Optional[str] = None,
    activo: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_db)
):
    buses = await crud.obtener_buses(session, bus_id, tipo, activo)
    return [BusResponse.from_orm(bus) for bus in buses]

@router.get("/buses/ids", response_model=List[int], tags=["Buses API"])
async def get_bus_ids_api(session: AsyncSession = Depends(get_async_db)):
    """Devuelve una lista de IDs de todos los buses."""
    ids = await crud.get_all_bus_ids(session)
    return ids

@router.get("/buses/details", response_model=List[BusResponse], tags=["Buses API"])
async def get_bus_details_api(session: AsyncSession = Depends(get_async_db)):
    """Devuelve una lista de buses con detalles para la selección de eliminación."""
    buses = await crud.obtener_buses(session)
    return [BusResponse.from_orm(bus) for bus in buses]


@router.post("/buses", status_code=status.HTTP_303_SEE_OTHER, tags=["Buses API"])
async def create_bus_api(
    bus_create: BusCreateForm = Depends(),
    session: AsyncSession = Depends(get_async_db)
):
    new_bus = await crud.crear_bus(
        session, # Pasa la sesión
        bus_create.nombre_bus,
        bus_create.tipo,
        bus_create.activo,
        bus_create.imagen
    )
    if not new_bus:
        raise HTTPException(status_code=400, detail="Error al crear bus")
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)

@router.delete("/buses/{bus_id}", tags=["Buses API"])
async def delete_bus_api(
    bus_id: int,
    session: AsyncSession = Depends(get_async_db)
):
    bus_to_delete_list = await crud.obtener_buses(session, bus_id=bus_id)
    if not bus_to_delete_list:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    
    bus_obj = bus_to_delete_list[0]

    resultado = await crud.eliminar_bus(session, bus_id) # Pasa la sesión
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

@router.post("/buses/update/{bus_id}", tags=["Buses API"])
async def actualizar_bus_post(
    bus_id: int,
    bus_update: BusUpdateForm = Depends(),
    session: AsyncSession = Depends(get_async_db)
):
    await actualizar_bus_db_form(bus_id, bus_update, session) # Pasa la sesión
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)


# -------------------- ESTACION API --------------------
@router.get("/estaciones", response_model=List[EstacionResponse], tags=["Estaciones API"])
async def get_estaciones_api(
    estacion_id: Optional[int] = None,
    localidad: Optional[str] = None,
    activo: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_db)
):
    estaciones = await crud.obtener_estaciones(session, estacion_id, localidad, activo)
    return [EstacionResponse.from_orm(estacion) for estacion in estaciones]

@router.get("/estaciones/ids", response_model=List[int], tags=["Estaciones API"])
async def get_estacion_ids_api(session: AsyncSession = Depends(get_async_db)):
    """Devuelve una lista de IDs de todas las estaciones."""
    ids = await crud.get_all_estacion_ids(session)
    return ids

@router.get("/estaciones/details", response_model=List[EstacionResponse], tags=["Estaciones API"])
async def get_estacion_details_api(session: AsyncSession = Depends(get_async_db)):
    """Devuelve una lista de estaciones con detalles para la selección de eliminación."""
    estaciones = await crud.obtener_estaciones(session)
    return [EstacionResponse.from_orm(estacion) for estacion in estaciones]


@router.post("/estaciones", status_code=status.HTTP_303_SEE_OTHER, tags=["Estaciones API"])
async def create_estacion_api(
    estacion_create: EstacionCreateForm = Depends(),
    session: AsyncSession = Depends(get_async_db)
):
    new_estacion = await crud.crear_estacion(
        session, # Pasa la sesión
        estacion_create.nombre_estacion,
        estacion_create.localidad,
        estacion_create.rutas_asociadas,
        estacion_create.activo,
        estacion_create.imagen
    )
    if not new_estacion:
        raise HTTPException(status_code=400, detail="Error al crear estación")
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)

@router.delete("/estaciones/{estacion_id}", tags=["Estaciones API"])
async def delete_estacion_api(
    estacion_id: int,
    session: AsyncSession = Depends(get_async_db)
):
    estacion_to_delete_list = await crud.obtener_estaciones(session, estacion_id=estacion_id)
    if not estacion_to_delete_list:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    
    estacion_obj = estacion_to_delete_list[0]

    resultado = await crud.eliminar_estacion(session, estacion_id) # Pasa la sesión
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

@router.post("/estaciones/update/{estacion_id}", tags=["Estaciones API"])
async def actualizar_estacion_post(
    estacion_id: int,
    estacion_update: EstacionUpdateForm = Depends(),
    session: AsyncSession = Depends(get_async_db)
):
    await actualizar_estacion_db_form(estacion_id, estacion_update, session) # Pasa la sesión
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

@router.get("/api/historial", response_model=List[HistorialItem], tags=["Historial API"])
async def get_historial():
    return historial_eliminados