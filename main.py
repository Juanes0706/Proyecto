from fastapi import FastAPI, Depends, HTTPException, Request, Response, UploadFile, File, Form, Body, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
import models, crud
from schemas import Bus as BusSchema, Estacion as EstacionSchema, BusResponse, EstacionResponse
from db import SessionLocal, engine
from supabase_client import supabase
import uuid
import logging

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Endpoint to get bus by ID
@app.get("/buses/{bus_id}", response_model=BusSchema)
def get_bus_by_id(bus_id: int):
    bus = crud.obtener_bus_por_id(bus_id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return bus

# Endpoint to get estacion by ID
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
    return templates.TemplateResponse("UpdatePage.html", {"request": request})

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
            filtered_historial.append({"tipo": "bus", "id": item["detalles"].get("id")})
        elif item["tipo"] == "estacion":
            filtered_historial.append({"tipo": "estacion", "id": item["detalles"].get("id")})
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
    # Convert activo from string to bool if needed
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
def listar_estaciones(sector: Optional[str] = None, activo: Optional[str] = None):
    # Convert activo from string to bool if needed
    if activo is not None:
        if activo.lower() == "true":
            activo_bool = True
        elif activo.lower() == "false":
            activo_bool = False
        else:
            activo_bool = None
    else:
        activo_bool = None
    estaciones = crud.obtener_estaciones(sector=sector, activo=activo_bool)
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

from datetime import datetime

@app.delete("/buses/{bus_id}")
def eliminar_bus_endpoint(bus_id: int):
    resultado = crud.eliminar_bus(bus_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    # Add to historial_eliminados
    historial_eliminados.append({
        "tipo": "bus",
        "detalles": resultado,
        "fecha_hora": datetime.now().isoformat()
    })
    return resultado

@app.delete("/estaciones/{estacion_id}")
def eliminar_estacion_endpoint(estacion_id: int):
    resultado = crud.eliminar_estacion(estacion_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    # Add to historial_eliminados
    historial_eliminados.append({
        "tipo": "estacion",
        "detalles": resultado,
        "fecha_hora": datetime.now().isoformat()
    })
    return resultado

@app.put("/buses/{bus_id}", response_model=BusResponse)
async def actualizar_bus_endpoint(
    bus_id: int,
    nombre_bus: Optional[str] = Form(None),
    tipo: Optional[str] = Form(None),
    activo: Optional[bool] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    update_data = {}
    if nombre_bus is not None:
        update_data["nombre_bus"] = nombre_bus
    if tipo is not None:
        update_data["tipo"] = tipo.lower().strip()
    if activo is not None:
        update_data["activo"] = activo

    if imagen:
        result = await crud.save_file(imagen, to_supabase=True)
        if "url" in result:
            imagen_url = result["url"]["publicUrl"] if isinstance(result["url"], dict) else result["url"]
            update_data["imagen"] = imagen_url

    updated_bus = crud.actualizar_bus(bus_id, update_data)
    if not updated_bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return BusResponse.from_orm(updated_bus)

@app.put("/estaciones/{estacion_id}", response_model=EstacionResponse)
async def actualizar_estacion_endpoint(
    estacion_id: int,
    nombre_estacion: Optional[str] = Form(None),
    localidad: Optional[str] = Form(None),
    rutas_asociadas: Optional[str] = Form(None),
    activo: Optional[bool] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    update_data = {}
    if nombre_estacion is not None:
        update_data["nombre_estacion"] = nombre_estacion
    if localidad is not None:
        update_data["localidad"] = localidad
    if rutas_asociadas is not None:
        update_data["rutas_asociadas"] = rutas_asociadas
    if activo is not None:
        update_data["activo"] = activo

    if imagen:
        result = await crud.save_file(imagen, to_supabase=True)
        if "url" in result:
            imagen_url = result["url"]["publicUrl"] if isinstance(result["url"], dict) else result["url"]
            update_data["imagen"] = imagen_url

    updated_estacion = crud.actualizar_estacion(estacion_id, update_data)
    if not updated_estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return EstacionResponse.from_orm(updated_estacion)