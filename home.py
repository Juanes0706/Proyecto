from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
from app.operations import crud
from app import models
from app.schemas.schemas import Bus as BusSchema, Estacion as EstacionSchema, BusResponse, EstacionResponse
from app.schemas.schemas import BusUpdateForm, EstacionUpdateForm, BusCreateForm, EstacionCreateForm
from app.database.db import SessionLocal, engine, async_session, get_db, Base
from app.services import *
from app.services.update_functions import actualizar_estacion_db_form, actualizar_bus_db_form
import logging
from datetime import datetime

router = APIRouter()

# Crear tablas
Base.metadata.create_all(bind=engine)

# Configuración para plantillas HTML y archivos estáticos
templates = Jinja2Templates(directory="templates")

# Mount static files
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static/css", StaticFiles(directory="static/css"), name="css")
app.mount("/static/js", StaticFiles(directory="static/js"), name="js")

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- MODELOS DETALLE ----------------------

class BusDetail(BaseModel):
    id: int
    nombre_bus: str
    tipo: str
    activo: bool
    imagen: str | None = None

class EstacionDetail(BaseModel):
    id: int
    nombre_estacion: str
    localidad: str
    rutas_asociadas: str
    activo: bool
    imagen: str | None = None

# ---------------------- HISTORIAL ----------------------

historial_eliminados = []

@router.get("/api/historial", response_model=List[dict])
def obtener_historial():
    filtered_historial = []
    for item in historial_eliminados:
        if item["tipo"] == "bus":
            detalles = item.get("detalles", {})
            filtered_historial.append({
                "tipo": "bus",
                "id": detalles.get("id"),
                "nombre_bus": detalles.get("nombre_bus"),
                "tipo": detalles.get("tipo")
            })
        elif item["tipo"] == "estacion":
            detalles = item.get("detalles", {})
            filtered_historial.append({
                "tipo": "estacion",
                "id": detalles.get("id"),
                "nombre_estacion": detalles.get("nombre_estacion"),
                "localidad": detalles.get("localidad")
            })
    return filtered_historial

# -------------------- HTML ROUTES --------------------

@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root_html(request: Request):
    return templates.TemplateResponse("CrudAppPage.html", {"request": request})

@router.get("/create", response_class=HTMLResponse, include_in_schema=False)
async def create_page(request: Request):
    return templates.TemplateResponse("CreatePage.html", {"request": request})

@router.get("/read", response_class=HTMLResponse, include_in_schema=False)
async def read_page(request: Request):
    return templates.TemplateResponse("ReadPage.html", {"request": request})

@router.get("/update", response_class=HTMLResponse, include_in_schema=False)
async def update_selection_page(request: Request):
    return templates.TemplateResponse("UpdatePage.html", {"request": request})

@router.get("/edit", response_class=HTMLResponse, include_in_schema=False)
async def edit_unified_page(request: Request, bus_id: Optional[int] = None, estacion_id: Optional[int] = None, db: Session = Depends(get_db)):
    bus_data = None
    estacion_data = None
    if bus_id:
        bus_data = crud.obtener_bus_por_id(bus_id, db)
        if not bus_data:
            raise HTTPException(status_code=404, detail="Bus no encontrado")
    elif estacion_id:
        estacion_data = crud.obtener_estacion_por_id(estacion_id, db)
        if not estacion_data:
            raise HTTPException(status_code=404, detail="Estación no encontrada")

    return templates.TemplateResponse("EditUnifiedPage.html", {
        "request": request,
        "bus": bus_data,
        "estacion": estacion_data
    })


@router.get("/delete", response_class=HTMLResponse, include_in_schema=False)
async def delete_page(request: Request):
    return templates.TemplateResponse("DeletePage.html", {"request": request})

@router.get("/historial", response_class=HTMLResponse, include_in_schema=False)
async def historial_page(request: Request):
    return templates.TemplateResponse("HistorialPage.html", {"request": request})

@router.get("/developer-info", response_class=HTMLResponse, include_in_schema=False)
async def developer_info_page(request: Request):
    return templates.TemplateResponse("DeveloperInfoPage.html", {"request": request})

@router.get("/planning", response_class=HTMLResponse, include_in_schema=False)
async def planning_page(request: Request):
    return templates.TemplateResponse("PlanningPage.html", {"request": request})

@router.get("/design", response_class=HTMLResponse, include_in_schema=False)
async def design_page(request: Request):
    return templates.TemplateResponse("DesignPage.html", {"request": request})


# -------------------- API ROUTES (Buses) --------------------

# Endpoint para crear un nuevo bus desde formulario HTML
@router.post("/buses", response_class=HTMLResponse, tags=["Buses"])
async def crear_bus_post(
    bus_create: BusCreateForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        # Pasa los datos del formulario directamente a la función de creación
        bus_data = {
            "nombre_bus": bus_create.nombre_bus,
            "tipo": bus_create.tipo,
            "activo": bus_create.activo,
        }
        nuevo_bus = await crud.crear_bus_con_imagen(bus_data, bus_create.imagen)
        if nuevo_bus:
            # Redirige a la página de lectura o muestra un mensaje de éxito
            return RedirectResponse(url="/read", status_code=status.HTTP_303_SEE_OTHER)
        raise HTTPException(status_code=400, detail="Error al crear el bus")
    except Exception as e:
        logging.error(f"Error en crear_bus_post: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")


@router.get("/buses/", response_model=List[BusResponse], tags=["Buses"])
def obtener_buses_api(
    bus_id: Optional[int] = None,
    tipo: Optional[str] = None,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    buses = crud.obtener_buses(bus_id=bus_id, tipo=tipo, activo=activo, db=db)
    if not buses and (bus_id is not None or tipo is not None or activo is not None):
        return [] # Return empty list if no filters match
    elif not buses:
        raise HTTPException(status_code=404, detail="No se encontraron buses")
    return buses

@router.get("/buses/ids", response_model=List[int], tags=["Buses"])
def get_all_bus_ids(db: Session = Depends(get_db)):
    ids = crud.get_all_bus_ids(db)
    return ids

@router.get("/buses/details", response_model=List[BusResponse], tags=["Buses"])
def get_all_bus_details(db: Session = Depends(get_db)):
    details = crud.get_all_bus_details(db)
    return details

@router.delete("/buses/{bus_id}", tags=["Buses"])
def eliminar_bus_endpoint(bus_id: int):
    bus_to_delete = crud.obtener_bus_por_id(bus_id) # Need a session for this
    if not bus_to_delete:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    resultado = crud.eliminar_bus(bus_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Error al eliminar el bus")
    # Store minimal details for history
    historial_eliminados.append({"tipo": "bus", "id": bus_to_delete.id, "nombre_bus": bus_to_delete.nombre_bus, "tipo_bus": bus_to_delete.tipo, "fecha_hora": datetime.now().isoformat()})
    return {"mensaje": "Bus eliminado"}

@router.post("/buses/update/{bus_id}", tags=["Buses"])
async def actualizar_bus_post(bus_id: int, bus_update: BusUpdateForm = Depends(), session: AsyncSession = Depends(async_session)):
    await actualizar_bus_db_form(bus_id, bus_update, session)
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)


# -------------------- API ROUTES (Estaciones) --------------------

# Endpoint para crear una nueva estación desde formulario HTML
@router.post("/estaciones", response_class=HTMLResponse, tags=["Estaciones"])
async def crear_estacion_post(
    estacion_create: EstacionCreateForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        estacion_data = {
            "nombre_estacion": estacion_create.nombre_estacion,
            "localidad": estacion_create.localidad,
            "rutas_asociadas": estacion_create.rutas_asociadas,
            "activo": estacion_create.activo,
        }
        nueva_estacion = await crud.crear_estacion_con_imagen(estacion_data, estacion_create.imagen)
        if nueva_estacion:
            return RedirectResponse(url="/read", status_code=status.HTTP_303_SEE_OTHER)
        raise HTTPException(status_code=400, detail="Error al crear la estación")
    except Exception as e:
        logging.error(f"Error en crear_estacion_post: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")


@router.get("/estaciones/", response_model=List[EstacionResponse], tags=["Estaciones"])
def obtener_estaciones_api(
    estacion_id: Optional[int] = None,
    sector: Optional[str] = None, # Changed from localidad to sector as per your crud.py
    activo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    estaciones = crud.obtener_estaciones(db, estacion_id=estacion_id, sector=sector, activo=activo)
    if not estaciones and (estacion_id is not None or sector is not None or activo is not None):
        return [] # Return empty list if no filters match
    elif not estaciones:
        raise HTTPException(status_code=404, detail="No se encontraron estaciones")
    return estaciones


@router.get("/estaciones/ids", response_model=List[int], tags=["Estaciones"])
def get_all_estacion_ids(db: Session = Depends(get_db)):
    ids = crud.get_all_estacion_ids(db)
    return ids

@router.get("/estaciones/details", response_model=List[EstacionResponse], tags=["Estaciones"])
def get_all_estacion_details(db: Session = Depends(get_db)):
    details = crud.get_all_estacion_details(db)
    return details


@router.delete("/estaciones/{estacion_id}", tags=["Estaciones"])
def eliminar_estacion_endpoint(estacion_id: int):
    estacion_to_delete = crud.obtener_estacion_por_id(estacion_id) # Need a session for this
    if not estacion_to_delete:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    resultado = crud.eliminar_estacion(estacion_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Error al eliminar la estación")
    # Store minimal details for history
    historial_eliminados.append({"tipo": "estacion", "id": estacion_to_delete.id, "nombre_estacion": estacion_to_delete.nombre_estacion, "localidad": estacion_to_delete.localidad, "fecha_hora": datetime.now().isoformat()})
    return {"mensaje": "Estación eliminada"}

@router.post("/estaciones/update/{estacion_id}", tags=["Estaciones"])
async def actualizar_estacion_post(estacion_id: int, estacion_update: EstacionUpdateForm = Depends(), session: AsyncSession = Depends(async_session)):
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

@router.get("/api/historial", response_model=List[HistorialItem], tags=["Historial"])
async def get_historial_eliminados():
    return historial_eliminados