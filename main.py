from fastapi import FastAPI, Depends, HTTPException, Request, Response, UploadFile, File, Form, Body, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import crud
import models
from schemas import Bus as BusSchema, Estacion as EstacionSchema, BusResponse, EstacionResponse
from schemas import BusUpdateForm, EstacionUpdateForm 
from db import SessionLocal, engine, async_session, get_db
from supabase_client import supabase, save_file
from update_functions import actualizar_bus_db_form, actualizar_estacion_db_form, get_supabase_path_from_url
import uuid
import logging
from datetime import datetime
from update_functions import *

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Endpoint para obtener bus por ID
@app.get("/buses/{bus_id}", response_model=BusSchema)
def get_bus_by_id(bus_id: int):
    bus = crud.obtener_bus_por_id(bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return bus

# Endpoint para obtener estación por ID
@app.get("/estaciones/{estacion_id}", response_model=EstacionSchema)
def get_estacion_by_id(estacion_id: int):
    estacion = crud.obtener_estacion_por_id(estacion_id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return estacion

# Configuración para plantillas HTML
templates = Jinja2Templates(directory="templates")
app.mount("/static/css", StaticFiles(directory="css"), name="css")
app.mount("/static/js", StaticFiles(directory="js"), name="js")
app.mount("/static/img", StaticFiles(directory="img"), name="img")

# Base de datos

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- HISTORIAL DE ELIMINADOS ----------------------

historial_eliminados = []

# ---------------------- RUTAS HTML ----------------------

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("CrudAppPage.html", {"request": request})

@app.get("/operations", response_class=HTMLResponse)
async def operations_page(request: Request):
    return templates.TemplateResponse("OperationsPage.html", {"request": request})

@app.get("/create", response_class=HTMLResponse)
async def create_page(request: Request):
    return templates.TemplateResponse("CreatePage.html", {"request": request})

@app.get("/read", response_class=HTMLResponse)
async def read_page(request: Request):
    return templates.TemplateResponse("ReadPage.html", {"request": request})

@app.get("/update", response_class=HTMLResponse)
async def update_page(request: Request):
    return templates.TemplateResponse("EditUnifiedPage.html", {"request": request})

@app.get("/edit", response_class=HTMLResponse)
async def edit_page(request: Request, bus_id: Optional[int] = None, estacion_id: Optional[int] = None, db: Session = Depends(get_db)):
    bus = None
    estacion = None
    if bus_id is not None:
        bus = crud.obtener_bus_por_id(bus_id)
        if not bus:
            raise HTTPException(status_code=404, detail="Bus no encontrado")
    if estacion_id is not None:
        estacion = crud.obtener_estacion_por_id(estacion_id)
        if not estacion:
            raise HTTPException(status_code=404, detail="Estación no encontrada")
    return templates.TemplateResponse("EditUnifiedPage.html", {"request": request, "bus": bus, "estacion": estacion})

@app.get("/delete", response_class=HTMLResponse)
async def delete_page(request: Request):
    return templates.TemplateResponse("DeletePage.html", {"request": request})

@app.get("/historial", response_class=HTMLResponse)
async def historial_page(request: Request):
    return templates.TemplateResponse("HistorialPage.html", {"request": request})

@app.get("/developer-info", response_class=HTMLResponse)
async def developer_info_page(request: Request):
    return templates.TemplateResponse("DeveloperInfoPage.html", {"request": request})

@app.get("/planning", response_class=HTMLResponse)
async def planning_page(request: Request):
    return templates.TemplateResponse("PlanningPage.html", {"request": request})

@app.get("/design", response_class=HTMLResponse)
async def design_page(request: Request):
    return templates.TemplateResponse("DesignPage.html", {"request": request})

# ---------------------- ENDPOINT HISTORIAL ----------------------

@app.get("/api/historial", response_model=List[dict])
def obtener_historial():
    filtered_historial = []
    for item in historial_eliminados:
        if item["tipo"] == "bus":
            detalles = item.get("detalles", {})
            filtered_historial.append({
                "tipo": "bus",
                "id": detalles.get("id"),
                "nombre_bus": detalles.get("nombre_bus"),
                "tipo_bus": detalles.get("tipo")
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

# ---------------------- BUSES ----------------------

@app.post("/buses", response_model=BusResponse, status_code=status.HTTP_201_CREATED)
async def crear_bus_con_imagen(
    nombre_bus: str = Form(...),
    tipo: str = Form(...),
    activo: bool = Form(...),
    imagen: UploadFile = File(...)
):
    nuevo_bus = await crud.crear_bus_async(
        {
            "nombre_bus": nombre_bus,
            "tipo": tipo.lower().strip(),
            "activo": activo
        },
        imagen
    )
    if not nuevo_bus:
        raise HTTPException(status_code=500, detail="No se pudo crear el bus.")
    return BusResponse.from_orm(nuevo_bus)

@app.post("/estaciones", response_model=EstacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_estacion_con_imagen(
    nombre_estacion: str = Form(...),
    localidad: str = Form(...),
    rutas_asociadas: str = Form(...),
    activo: bool = Form(...),
    imagen: UploadFile = File(...)
):
    """
    Endpoint para crear una estación con imagen de forma asíncrona.
    """
    nueva_estacion = await crud.crear_estacion_async(
        {
            "nombre_estacion": nombre_estacion,
            "localidad": localidad,
            "rutas_asociadas": rutas_asociadas,
            "activo": activo
        },
        imagen
    )
    if not nueva_estacion:
        raise HTTPException(status_code=500, detail="No se pudo crear la estación.")
    return EstacionResponse.from_orm(nueva_estacion)

@app.get("/buses/{bus_id}", response_model=BusResponse)
def obtener_bus_por_id_endpoint(bus_id: int):
    bus = crud.obtener_bus_por_id(bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return BusResponse.from_orm(bus)

@app.get("/buses/", response_model=List[BusSchema])
def listar_buses(bus_id: Optional[int] = None, tipo: Optional[str] = None, activo: Optional[str] = None):
    # Convertir activo de string a bool si es necesario
    if activo is not None:
        if activo.lower() == "true":
            activo_bool = True
        elif activo.lower() == "false":
            activo_bool = False
        else:
            activo_bool = None
    else:
        activo_bool = None
    buses = crud.obtener_buses(bus_id=bus_id, tipo=tipo, activo=activo_bool)
    return buses

@app.get("/estaciones/{estacion_id}", response_model=EstacionResponse)
def obtener_estacion_por_id_endpoint(estacion_id: int):
    estacion = crud.obtener_estacion_por_id(estacion_id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return EstacionResponse.from_orm(estacion)

@app.get("/estaciones/", response_model=List[EstacionSchema])
def listar_estaciones(estacion_id: Optional[int] = None, sector: Optional[str] = None, activo: Optional[str] = None):
    # Convertir activo de string a bool si es necesario
    if activo is not None:
        if activo.lower() == "true":
            activo_bool = True
        elif activo.lower() == "false":
            activo_bool = False
        else:
            activo_bool = None
    else:
        activo_bool = None
    estaciones = crud.obtener_estaciones(estacion_id=estacion_id, sector=sector, activo=activo_bool)
    return estaciones

@app.put("/buses/{bus_id}/estado")
def actualizar_estado_bus_endpoint(bus_id: int, activo: bool):
    resultado = crud.actualizar_estado_bus(bus_id, activo)
    if not resultado:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return resultado

@app.put("/estaciones/{estacion_id}/estado")
def actualizar_estado_estacion_endpoint(estacion_id: int, activo: bool):
    resultado = crud.actualizar_estado_estacion(estacion_id, activo)
    if not resultado:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return resultado


@app.delete("/buses/{bus_id}")
def eliminar_bus_endpoint(bus_id: int):
    # Recuperar los detalles del bus antes de eliminar para el registro histórico
    bus_to_delete = crud.obtener_bus_por_id(bus_id)
    if not bus_to_delete:
        raise HTTPException(status_code=404, detail="Bus no encontrado")

    resultado = crud.eliminar_bus(bus_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Error al eliminar el bus")
    # Agregar al historial_eliminados
    historial_eliminados.append({
        "tipo": "bus",
        "detalles": {"id": bus_to_delete.id, "nombre_bus": bus_to_delete.nombre_bus, "tipo": bus_to_delete.tipo},
        "fecha_hora": datetime.now().isoformat()
    })
    return {"mensaje": "Bus eliminado"}

@app.delete("/estaciones/{estacion_id}")
def eliminar_estacion_endpoint(estacion_id: int):
    # Recuperar los detalles de la estación antes de eliminar para el registro histórico
    estacion_to_delete = crud.obtener_estacion_por_id(estacion_id)
    if not estacion_to_delete:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    resultado = crud.eliminar_estacion(estacion_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Error al eliminar la estación")
    # Agregar al historial_eliminados
    historial_eliminados.append({
        "tipo": "estacion",
        "detalles": {"id": estacion_to_delete.id, "nombre_estacion": estacion_to_delete.nombre_estacion, "localidad": estacion_to_delete.localidad},
        "fecha_hora": datetime.now().isoformat()
    })
    return {"mensaje": "Estación eliminada"}
# Rutas HTML
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("CrudAppPage.html", {"request": request})

@app.get("/update", response_class=HTMLResponse)
async def update_page(request: Request):
    return templates.TemplateResponse("UpdatePage.html", {"request": request})

# Endpoint para actualizar bus (POST)
@app.post("/buses/update/{bus_id}", tags=["Buses"])
async def actualizar_bus_post(
    bus_id: int,
    bus_update: BusUpdateForm = Depends(),
    session: AsyncSession = Depends(async_session)

):
    bus = await actualizar_bus_db_form(bus_id, bus_update, session)
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)
    
@app.post("/estaciones/update/{estacion_id}", tags=["Estaciones"])
async def actualizar_estacion_post(
    estacion_id: int,
    estacion_update: EstacionUpdateForm = Depends(),
    session: AsyncSession = Depends(async_session)
):
    estacion = await actualizar_estacion_db_form( estacion_id, estacion_update, session)
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)  

@app.get("/buses/ids", response_model=List[int])
def obtener_ids_buses(db: Session = Depends(get_db)):
    buses = db.query(models.Bus.id).all()
    return [bus.id for bus in buses]

from pydantic import BaseModel

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

@app.get("/buses/details", response_model=List[BusDetail])
def obtener_detalles_buses(db: Session = Depends(get_db)):
    buses = db.query(models.Bus).all()
    bus_details = []
    for bus in buses:
        bus_details.append(BusDetail(
            id=bus.id,
            nombre_bus=bus.nombre_bus,
            tipo=bus.tipo,
            activo=bus.activo,
            imagen=bus.imagen
        ))
    return bus_details

@app.get("/estaciones/details", response_model=List[EstacionDetail])
def obtener_detalles_estaciones(db: Session = Depends(get_db)):
    estaciones = db.query(models.Estacion).all()
    estacion_details = []
    for estacion in estaciones:
        estacion_details.append(EstacionDetail(
            id=estacion.id,
            nombre_estacion=estacion.nombre_estacion,
            localidad=estacion.localidad,
            rutas_asociadas=estacion.rutas_asociadas,
            activo=estacion.activo,
            imagen=estacion.imagen
        ))
    return estacion_details

@app.get("/estaciones/ids", response_model=List[int])
def obtener_ids_estaciones(db: Session = Depends(get_db)):
    estaciones = db.query(models.Estacion.id).all()
    return [estacion.id for estacion in estaciones]
