from fastapi import FastAPI, Depends, HTTPException, Request, Response, UploadFile, File, Form, Body
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

# ---------------------- ENDPOINT HISTORIAL ----------------------

@app.get("/historial", response_model=List[dict])
def obtener_historial():
    return historial_eliminados

# ---------------------- BUSES ----------------------

@app.post("/buses", response_model=BusResponse)
async def crear_bus_con_imagen(
    nombre_bus: str = Form(...),
    tipo: str = Form(...),
    activo: bool = Form(...),
    imagen: UploadFile = File(...)
):
    imagen_bytes = await imagen.read()
    imagen_filename = imagen.filename
    bus_data = {
        "nombre_bus": nombre_bus,
        "tipo": tipo.lower().strip(),
        "activo": activo
    }
    nuevo_bus = crud.crear_bus(bus_data, imagen_bytes=imagen_bytes, imagen_filename=imagen_filename)
    if not nuevo_bus:
        raise HTTPException(status_code=500, detail="No se pudo crear el bus.")
    return BusResponse.from_orm(nuevo_bus)

@app.delete("/buses/{id}")
def eliminar_bus(id: int):
    bus = crud.obtener_bus_por_id(id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    historial_eliminados.append({"tipo": "bus", "datos": bus.__dict__})
    resultado = crud.eliminar_bus(id)
    return Response(status_code=204)

@app.get("/buses/", response_model=list[dict])
def listar_buses(tipo: Optional[str] = None, activo: Optional[bool] = None):
    return crud.obtener_buses(tipo=tipo, activo=activo)

@app.get("/buses/{id}", response_model=dict)
def obtener_bus(id: int):
    bus = crud.obtener_bus_por_id(id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return {k: v for k, v in bus.__dict__.items() if not k.startswith('_')}

# ---------------------- ESTACIONES ----------------------

@app.post("/estaciones", response_model=EstacionResponse)
async def crear_estacion_con_imagen(
    nombre_estacion: str = Form(...),
    localidad: str = Form(...),
    rutas_asociadas: str = Form(...),
    activo: bool = Form(...),
    imagen: UploadFile = File(...)
):
    imagen_bytes = await imagen.read()
    imagen_filename = imagen.filename
    estacion_data = {
        "nombre_estacion": nombre_estacion,
        "localidad": localidad,
        "rutas_asociadas": rutas_asociadas,
        "activo": activo
    }
    nueva_estacion = crud.crear_estacion(estacion_data, imagen_bytes=imagen_bytes, imagen_filename=imagen_filename)
    if not nueva_estacion:
        raise HTTPException(status_code=500, detail="No se pudo crear la estación.")
    return EstacionResponse.from_orm(nueva_estacion)

@app.delete("/estaciones/{id}")
def eliminar_estacion(id: int):
    estacion = crud.obtener_estacion_por_id(id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    historial_eliminados.append({"tipo": "estacion", "datos": estacion.__dict__})
    resultado = crud.eliminar_estacion(id)
    return Response(status_code=204)

@app.get("/estaciones/", response_model=list[dict])
def listar_estaciones(sector: Optional[str] = None, activo: Optional[bool] = None):
    return crud.obtener_estaciones(sector=sector, activo=activo)

@app.get("/estaciones/{id}", response_model=dict)
def obtener_estacion(id: int):
    estacion = crud.obtener_estacion_por_id(id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return {k: v for k, v in estacion.__dict__.items() if not k.startswith('_')}
