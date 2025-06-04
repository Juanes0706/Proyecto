from fastapi import FastAPI, Depends, HTTPException, Request, Response, UploadFile, File, Form, Body, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import models, crud
from schemas import Bus as BusSchema, Estacion as EstacionSchema, BusResponse, EstacionResponse
from db import SessionLocal, engine, async_session, get_db
from supabase_client import supabase, save_file
from crud import get_supabase_path_from_url
import uuid
import logging
from datetime import datetime

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración para plantillas HTML
templates = Jinja2Templates(directory="templates")
app.mount("/static/css", StaticFiles(directory="css"), name="css")
app.mount("/static/js", StaticFiles(directory="js"), name="js")
app.mount("/static/img", StaticFiles(directory="img"), name="img")

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
    bus_update: crud.BusUpdateForm = Depends(),
    session: AsyncSession = Depends(async_session)
):
    bus = await crud.actualizar_bus_db_form(bus_id, bus_update, session)
    if not bus:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el bus.")
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)

# Endpoint para actualizar estación (POST)
@app.put("/estaciones/update/{estacion_id}", tags=["Estaciones"])
async def actualizar_estacion_post(
    estacion_id: int,
    estacion_update: crud.EstacionUpdateForm = Depends(),
    session: AsyncSession = Depends(async_session)
):
    estacion = await crud.actualizar_estacion_db_form(estacion_id, estacion_update, session)
    if not estacion:
        raise HTTPException(status_code=500, detail="No se pudo actualizar la estación.")
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)
