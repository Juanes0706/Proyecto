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
from app.schemas.schemas import BusUpdateForm, EstacionUpdateForm 
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
app.mount("/static/img", StaticFiles(directory="img"), name="img")

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
async def home(request: Request):
    return templates.TemplateResponse("inicio.html", {"request": request})

@router.get("/crear_estacion", response_class=HTMLResponse)
async def crear_estacion_page(request: Request):
    return templates.TemplateResponse("crear_estacion.html", {"request": request})

@router.get("/crear_bus", response_class=HTMLResponse)
async def crear_bus_page(request: Request):
    return templates.TemplateResponse("crear_bus.html", {"request": request})

@router.get("/editar_estacion", response_class=HTMLResponse)
async def editar_estacion_page(request: Request):
    return templates.TemplateResponse("editar_estacion.html", {"request": request})

@router.get("/editar_bus", response_class=HTMLResponse)
async def editar_bus_page(request: Request):
    return templates.TemplateResponse("editar_bus.html", {"request": request})

@router.get("/eliminar_estacion", response_class=HTMLResponse)
async def eliminar_estacion_page(request: Request):
    return templates.TemplateResponse("eliminar_estacion.html", {"request": request})

@router.get("/eliminar_bus", response_class=HTMLResponse)
async def eliminar_bus_page(request: Request):
    return templates.TemplateResponse("eliminar_bus.html", {"request": request})

@router.get("/historial_estaciones", response_class=HTMLResponse)
async def historial_estaciones_page(request: Request, db: Session = Depends(get_db)):
    estaciones = crud.obtener_estaciones_eliminadas()
    return templates.TemplateResponse("historial_eliminados_estacion.html", {"request": request, "estaciones": estaciones})

@router.get("/historial_buses", response_class=HTMLResponse)
async def historial_buses_page(request: Request, db: Session = Depends(get_db)):
    buses = crud.obtener_buses_eliminados()
    return templates.TemplateResponse("historial_eliminados_bus.html", {"request": request, "buses": buses})

@router.get("/desarrollador", response_class=HTMLResponse)
async def desarrollador_page(request: Request):
    return templates.TemplateResponse("desarrollador.html", {"request": request})

@router.get("/diseno", response_class=HTMLResponse)
async def diseno_page(request: Request):
    return templates.TemplateResponse("diseno.html", {"request": request})
