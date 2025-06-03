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
