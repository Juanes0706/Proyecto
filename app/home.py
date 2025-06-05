from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel
from app.operations import crud
import models
from app.schemas import Bus as BusSchema, Estacion as EstacionSchema, BusResponse, EstacionResponse
from app.schemas import BusUpdateForm, EstacionUpdateForm 
from app.db import SessionLocal, engine, async_session, get_db
from app.services import *
from app.services import actualizar_estacion_db_form, actualizar_bus_db_form
import logging
from datetime import datetime

router = APIRouter()

# Crear tablas
models.Base.metadata.create_all(bind=engine)

# Configuración para plantillas HTML y archivos estáticos
templates = Jinja2Templates(directory="templates")

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

# ---------------------- RUTAS HTML ----------------------

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("CrudAppPage.html", {"request": request})

@router.get("/operations", response_class=HTMLResponse)
async def operations_page(request: Request):
    return templates.TemplateResponse("OperationsPage.html", {"request": request})

@router.get("/create", response_class=HTMLResponse)
async def create_page(request: Request):
    return templates.TemplateResponse("CreatePage.html", {"request": request})

@router.get("/read", response_class=HTMLResponse)
async def read_page(request: Request):
    return templates.TemplateResponse("ReadPage.html", {"request": request})

@router.get("/update", response_class=HTMLResponse)
async def update_page(request: Request):
    return templates.TemplateResponse("UpdatePage.html", {"request": request})

@router.get("/edit", response_class=HTMLResponse)
async def edit_page(request: Request, bus_id: Optional[int] = None, estacion_id: Optional[int] = None, db: Session = Depends(get_db)):
    bus = crud.obtener_bus_por_id(bus_id) if bus_id is not None else None
    if bus_id is not None and not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")

    estacion = crud.obtener_estacion_por_id(estacion_id) if estacion_id is not None else None
    if estacion_id is not None and not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    return templates.TemplateResponse("EditUnifiedPage.html", {"request": request, "bus": bus, "estacion": estacion})

@router.get("/delete", response_class=HTMLResponse)
async def delete_page(request: Request):
    return templates.TemplateResponse("DeletePage.html", {"request": request})

@router.get("/historial", response_class=HTMLResponse)
async def historial_page(request: Request):
    return templates.TemplateResponse("HistorialPage.html", {"request": request})

@router.get("/developer-info", response_class=HTMLResponse)
async def developer_info_page(request: Request):
    return templates.TemplateResponse("DeveloperInfoPage.html", {"request": request})

@router.get("/planning", response_class=HTMLResponse)
async def planning_page(request: Request):
    return templates.TemplateResponse("PlanningPage.html", {"request": request})

@router.get("/design", response_class=HTMLResponse)
async def design_page(request: Request):
    return templates.TemplateResponse("DesignPage.html", {"request": request})

# ---------------------- ENDPOINTS API ----------------------

# BUSES

@router.post("/buses", response_model=BusResponse, status_code=status.HTTP_201_CREATED)
async def crear_bus_con_imagen(nombre_bus: str = Form(...), tipo: str = Form(...), activo: bool = Form(...), imagen: UploadFile = File(...)):
    nuevo_bus = await crud.crear_bus_async({"nombre_bus": nombre_bus, "tipo": tipo.lower().strip(), "activo": activo}, imagen)
    if not nuevo_bus:
        raise HTTPException(status_code=500, detail="No se pudo crear el bus.")
    return BusResponse.from_orm(nuevo_bus)

@router.get("/buses/{bus_id}", response_model=BusResponse)
def obtener_bus_por_id_endpoint(bus_id: int):
    bus = crud.obtener_bus_por_id(bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return BusResponse.from_orm(bus)

@router.get("/buses/", response_model=List[BusSchema])
def listar_buses(bus_id: Optional[int] = None, tipo: Optional[str] = None, activo: Optional[str] = None):
    activo_bool = None
    if activo is not None:
        activo_bool = True if activo.lower() == "true" else False if activo.lower() == "false" else None
    return crud.obtener_buses(bus_id=bus_id, tipo=tipo, activo=activo_bool)

@router.put("/buses/{bus_id}/estado")
def actualizar_estado_bus_endpoint(bus_id: int, activo: bool):
    resultado = crud.actualizar_estado_bus(bus_id, activo)
    if not resultado:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return resultado

@router.delete("/buses/{bus_id}")
def eliminar_bus_endpoint(bus_id: int):
    bus_to_delete = crud.obtener_bus_por_id(bus_id)
    if not bus_to_delete:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    resultado = crud.eliminar_bus(bus_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Error al eliminar el bus")
    historial_eliminados.append({"tipo": "bus", "detalles": {"id": bus_to_delete.id, "nombre_bus": bus_to_delete.nombre_bus, "tipo": bus_to_delete.tipo}, "fecha_hora": datetime.now().isoformat()})
    return {"mensaje": "Bus eliminado"}

@router.post("/buses/update/{bus_id}", tags=["Buses"])
async def actualizar_bus_post(bus_id: int, bus_update: BusUpdateForm = Depends(), session: AsyncSession = Depends(async_session)):
    await actualizar_bus_db_form(bus_id, bus_update, session)
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/buses/ids", response_model=List[int])
def obtener_ids_buses(db: Session = Depends(get_db)):
    return [bus.id for bus in db.query(models.Bus.id).all()]

@router.get("/buses/details", response_model=List[BusDetail])
def obtener_detalles_buses(db: Session = Depends(get_db)):
    return [BusDetail(**bus.__dict__) for bus in db.query(models.Bus).all()]

# ESTACIONES

@router.post("/estaciones", response_model=EstacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_estacion_con_imagen(nombre_estacion: str = Form(...), localidad: str = Form(...), rutas_asociadas: str = Form(...), activo: bool = Form(...), imagen: UploadFile = File(...)):
    nueva_estacion = await crud.crear_estacion_async({"nombre_estacion": nombre_estacion, "localidad": localidad, "rutas_asociadas": rutas_asociadas, "activo": activo}, imagen)
    if not nueva_estacion:
        raise HTTPException(status_code=500, detail="No se pudo crear la estación.")
    return EstacionResponse.from_orm(nueva_estacion)

@router.get("/estaciones/{estacion_id}", response_model=EstacionResponse)
def obtener_estacion_por_id_endpoint(estacion_id: int):
    estacion = crud.obtener_estacion_por_id(estacion_id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return EstacionResponse.from_orm(estacion)

@router.get("/estaciones/", response_model=List[EstacionSchema])
def listar_estaciones(estacion_id: Optional[int] = None, sector: Optional[str] = None, activo: Optional[str] = None):
    activo_bool = None
    if activo is not None:
        activo_bool = True if activo.lower() == "true" else False if activo.lower() == "false" else None
    return crud.obtener_estaciones(estacion_id=estacion_id, sector=sector, activo=activo_bool)

@router.put("/estaciones/{estacion_id}/estado")
def actualizar_estado_estacion_endpoint(estacion_id: int, activo: bool):
    resultado = crud.actualizar_estado_estacion(estacion_id, activo)
    if not resultado:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return resultado

@router.delete("/estaciones/{estacion_id}")
def eliminar_estacion_endpoint(estacion_id: int):
    estacion_to_delete = crud.obtener_estacion_por_id(estacion_id)
    if not estacion_to_delete:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    resultado = crud.eliminar_estacion(estacion_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Error al eliminar la estación")
    historial_eliminados.append({"tipo": "estacion", "detalles": {"id": estacion_to_delete.id, "nombre_estacion": estacion_to_delete.nombre_estacion, "localidad": estacion_to_delete.localidad}, "fecha_hora": datetime.now().isoformat()})
    return {"mensaje": "Estación eliminada"}

@router.post("/estaciones/update/{estacion_id}", tags=["Estaciones"])
async def actualizar_estacion_post(estacion_id: int, estacion_update: EstacionUpdateForm = Depends(), session: AsyncSession = Depends(async_session)):
    await actualizar_estacion_db_form(estacion_id, estacion_update, session)
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/estaciones/details", response_model=List[EstacionDetail])
def obtener_detalles_estaciones(db: Session = Depends(get_db)):
    return [EstacionDetail(**est.__dict__) for est in db.query(models.Estacion).all()]

@router.get("/estaciones/ids", response_model=List[int])
def obtener_ids_estaciones(db: Session = Depends(get_db)):
    return [est.id for est in db.query(models.Estacion.id).all()]
