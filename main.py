from fastapi import FastAPI, Depends, HTTPException, Request, Response, UploadFile, File, Form, Body, status, Query 
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
from datetime import datetime
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db import async_session
from schemas import BusUpdateForm, EstacionUpdateForm
from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from db import get_db
from models import Estacion  
from schemas import EstacionResponse
from supabase_client import supabase, save_file


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

@app.post("/buses/update/{bus_id}", tags=["Buses"])
async def actualizar_bus_post(
    bus_id: int,
    bus_update: BusUpdateForm = Depends(),
    session: AsyncSession = Depends(async_session),
    local_kw: Optional[str] = Query(None) # <--- AÑADE ESTA LÍNEA
):
    # Llama a la función asíncrona correcta y pasa el objeto directamente
    bus = await crud.actualizar_bus_db_form(bus_id, bus_update, session)
    if not bus:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el bus.")
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/estaciones/update/{estacion_id}", tags=["Estaciones"])
async def actualizar_estacion_post(
    estacion_id: int,
    estacion_update: EstacionUpdateForm = Depends(),
    session: AsyncSession = Depends(async_session),
    local_kw: Optional[str] = Query(None) # <--- AÑADE ESTA LÍNEA
):
    # Llama a la función asíncrona correcta y pasa el objeto directamente
    estacion = await crud.actualizar_estacion_db_form(estacion_id, estacion_update, session)
    if not estacion:
        raise HTTPException(status_code=500, detail="No se pudo actualizar la estación.")
    return RedirectResponse(url="/update", status_code=status.HTTP_303_SEE_OTHER)

@app.put("/estaciones/{estacion_id}", response_model=EstacionResponse)
def actualizar_estacion_db_form(
    estacion_id: int,
    nombre: str = Form(...),
    ubicacion: str = Form(...),
    descripcion: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    estacion = db.query(Estacion).filter(Estacion.id == estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    estacion.nombre = nombre
    estacion.ubicacion = ubicacion
    estacion.descripcion = descripcion

    if imagen:
        # Elimina imagen anterior si existe
        if estacion.imagen_url:
            try:
                supabase_path = get_supabase_path_from_url(estacion.imagen_url)
                supabase.storage.from_("transmilenio").remove([supabase_path])
            except Exception as e:
                print("Error eliminando imagen anterior:", e)

        estacion.imagen_url = save_file(imagen, "transmilenio")

    db.commit()
    db.refresh(estacion)
    return estacion

@app.put("/update/{id}", response_model=BusOut)
async def actualizar_bus_db_form(
    id: int,
    nombre_bus: str = Form(...),
    tipo: str = Form(...),
    activo: bool = Form(...),
    imagen: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    bus_db = db.query(BusDB).filter(BusDB.id == id).first()
    if not bus_db:
        raise HTTPException(status_code=404, detail="Bus no encontrado")

    imagen_actual = bus_db.imagen
    url_imagen = None

    if imagen:
        try:
            resultado = await save_file(imagen, to_supabase=True)
            url_imagen = resultado["url"]
        except Exception as e:
            logging.error(f"Error subiendo nueva imagen: {e}")
            raise HTTPException(status_code=500, detail="Error subiendo nueva imagen")

    if imagen_actual and url_imagen:
        try:
            path_antiguo = get_supabase_path_from_url(imagen_actual, SUPABASE_BUCKET_BUSES)
            if path_antiguo:
                supabase.storage.from_(SUPABASE_BUCKET_BUSES).remove([path_antiguo])
        except Exception as e:
            logging.error(f"Error eliminando imagen anterior: {e}")

    bus_db.nombre_bus = nombre_bus
    bus_db.tipo = tipo
    bus_db.activo = activo
    if url_imagen:
        bus_db.imagen = url_imagen

    db.commit()
    db.refresh(bus_db)
    return bus_db