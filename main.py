from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import models, schemas, crud
from db import SessionLocal, engine
from supabase_client import supabase
from fastapi import UploadFile, File, Form

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuración para plantillas HTML
templates = Jinja2Templates(directory="templates")
app.mount("/static/css", StaticFiles(directory="css"), name="css")
app.mount("/static/js", StaticFiles(directory="js"), name="js")
app.mount("/static/img", StaticFiles(directory="img"), name="img")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- RUTA PRINCIPAL CON HTML ----------------------

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

from fastapi import Body

@app.put("/buses/{id}", response_model=dict)
async def actualizar_bus(id: int, bus: dict = Body(...)):
    existing_bus = crud.obtener_bus_por_id(id)
    if not existing_bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    update_data = {}
    if "nombre_bus" in bus:
        update_data["nombre_bus"] = bus["nombre_bus"]
    if "tipo" in bus:
        update_data["tipo"] = bus["tipo"].lower().strip()
    if "activo" in bus:
        update_data["activo"] = bus["activo"]
    # Remove image update from here to separate endpoint
    updated_bus = crud.actualizar_bus(id, update_data)
    if not updated_bus:
        raise HTTPException(status_code=500, detail="Error actualizando bus")
    return updated_bus
@app.put("/estaciones/{id}", response_model=dict)
async def actualizar_estacion(id: int, estacion: dict = Body(...)):
    existing_estacion = crud.obtener_estacion_por_id(id)
    if not existing_estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    update_data = {}
    if "nombre_estacion" in estacion:
        update_data["nombre_estacion"] = estacion["nombre_estacion"]
    if "localidad" in estacion:
        update_data["localidad"] = estacion["localidad"]
    if "rutas_asociadas" in estacion:
        update_data["rutas_asociadas"] = estacion["rutas_asociadas"]
    if "activo" in estacion:
        update_data["activo"] = estacion["activo"]
    # Remove image update from here to separate endpoint
    updated_estacion = crud.actualizar_estacion(id, update_data)
    if not updated_estacion:
        raise HTTPException(status_code=500, detail="Error actualizando estación")
    return updated_estacion
@app.delete("/buses/{id}")
def eliminar_bus(id: int):
    resultado = crud.eliminar_bus(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return {"mensaje": resultado.get("mensaje", "Bus eliminado")}

@app.delete("/buses/{id}")
def eliminar_bus(id: int):
    resultado = crud.eliminar_bus(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return {"mensaje": resultado.get("mensaje", "Bus eliminado")}

@app.delete("/estaciones/{id}")
def eliminar_estacion(id: int):
    resultado = crud.eliminar_estacion(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return {"mensaje": resultado.get("mensaje", "Estación eliminada")}

@app.delete("/estaciones/{id}")
def eliminar_estacion(id: int):
    resultado = crud.eliminar_estacion(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return {"mensaje": resultado.get("mensaje", "Estación eliminada")}

@app.put("/estaciones/{id}", response_model=dict)
async def actualizar_estacion(id: int, estacion: dict = Body(...)):
    existing_estacion = crud.obtener_estacion_por_id(id)
    if not existing_estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    update_data = {}
    if "nombre_estacion" in estacion:
        update_data["nombre_estacion"] = estacion["nombre_estacion"]
    if "localidad" in estacion:
        update_data["localidad"] = estacion["localidad"]
    if "rutas_asociadas" in estacion:
        update_data["rutas_asociadas"] = estacion["rutas_asociadas"]
    if "activo" in estacion:
        update_data["activo"] = estacion["activo"]
    # Remove image update from here to separate endpoint
    updated_estacion = crud.actualizar_estacion(id, update_data)
    if not updated_estacion:
        raise HTTPException(status_code=500, detail="Error actualizando estación")
    return updated_estacion

@app.delete("/buses/{id}")
def eliminar_bus(id: int):
    resultado = crud.eliminar_bus(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return Response(status_code=204)

@app.delete("/buses/{id}")
def eliminar_bus(id: int):
    resultado = crud.eliminar_bus(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return {"mensaje": resultado.get("mensaje", "Bus eliminado")}

@app.delete("/estaciones/{id}")
def eliminar_estacion(id: int):
    resultado = crud.eliminar_estacion(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return Response(status_code=204)

@app.delete("/estaciones/{id}")
def eliminar_estacion(id: int):
    resultado = crud.eliminar_estacion(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Estación no encontrada")

@app.put("/estaciones/{id}", response_model=dict)
async def actualizar_estacion(id: int, estacion: dict = Body(...)):
    existing_estacion = crud.obtener_estacion_por_id(id)
    if not existing_estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    update_data = {}
    if "nombre_estacion" in estacion:
        update_data["nombre_estacion"] = estacion["nombre_estacion"]
    if "localidad" in estacion:
        update_data["localidad"] = estacion["localidad"]
    if "rutas_asociadas" in estacion:
        update_data["rutas_asociadas"] = estacion["rutas_asociadas"]
    if "activo" in estacion:
        update_data["activo"] = estacion["activo"]
    # Remove image update from here to separate endpoint
    response = supabase.table("estaciones").update(update_data).eq("id", id).execute()
    if response.error:
        raise HTTPException(status_code=500, detail="Error actualizando estación")
    return response.data[0]

@app.get("/delete", response_class=HTMLResponse)
async def delete_page(request: Request):
    return templates.TemplateResponse("DeletePage.html", {"request": request})

# ---------------------- BUSES ----------------------

from fastapi import File, UploadFile, Form
from typing import Optional
from fastapi import HTTPException
import uuid
import logging

@app.post("/buses", response_model=dict)
async def crear_bus_con_imagen(
    nombre_bus: str = Form(...),
    tipo: str = Form(...),
    activo: bool = Form(...),
    imagen: UploadFile = File(...)
):
    try:
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

        return {"mensaje": "Bus creado exitosamente", "bus": nuevo_bus}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el bus: {str(e)}")

@app.post("/estaciones", response_model=dict)
async def crear_estacion_con_imagen(
    nombre_estacion: str = Form(...),
    localidad: str = Form(...),
    rutas_asociadas: str = Form(...),
    activo: bool = Form(...),
    imagen: UploadFile = File(...)
):
    try:
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

        return {"mensaje": "Estación creada exitosamente", "estacion": nueva_estacion}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la estación: {str(e)}")

@app.post("/buses/", response_model=dict)
async def crear_bus(
    nombre_bus: str = Form(...),
    tipo: str = Form(...),
    activo: bool = Form(...)
):
    bus_data = {
        "nombre_bus": nombre_bus,
        "tipo": tipo.lower().strip(),
        "activo": activo,
        "imagen": None
    }
    created_bus = crud.crear_bus(bus_data)
    if not created_bus:
        raise HTTPException(status_code=500, detail="Error creating bus")
    return created_bus

@app.get("/buses/", response_model=list[dict])
def listar_buses(tipo: Optional[str] = None, activo: Optional[bool] = None):
    return crud.obtener_buses(tipo=tipo, activo=activo)

@app.get("/buses/{id}", response_model=dict)
def obtener_bus(id: int):
    bus = crud.obtener_bus_por_id(id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return bus

@app.delete("/buses/{id}")
def eliminar_bus(id: int):
    resultado = crud.eliminar_bus(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return Response(status_code=204)

@app.put("/buses/{id}/estado")
def cambiar_estado_bus(id: int, activo: bool):
    resultado = crud.actualizar_estado_bus(id, activo)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return resultado

# ---------------------- ESTACIONES ----------------------

@app.post("/estaciones/", response_model=dict)
async def crear_estacion(
    nombre_estacion: str = Form(...),
    localidad: str = Form(...),
    rutas_asociadas: str = Form(...),
    activo: bool = Form(...)
):
    estacion_data = {
        "nombre_estacion": nombre_estacion,
        "localidad": localidad,
        "rutas_asociadas": rutas_asociadas,
        "activo": activo,
        "imagen": None
    }
    created_estacion = crud.crear_estacion(estacion_data)
    if not created_estacion:
        raise HTTPException(status_code=500, detail="Error creating estación")
    return created_estacion

@app.get("/estaciones/", response_model=list[dict])
def listar_estaciones(sector: Optional[str] = None, activo: Optional[bool] = None):
    return crud.obtener_estaciones(sector=sector, activo=activo)

@app.get("/estaciones/{id}", response_model=dict)
def obtener_estacion(id: int):
    estacion = crud.obtener_estacion_por_id(id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return estacion

@app.delete("/estaciones/{id}")
def eliminar_estacion(id: int):
    resultado = crud.eliminar_estacion(id)
    if resultado is None or ("error" in resultado and resultado["error"]):
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return Response(status_code=204)

@app.put("/estaciones/{id}/estado")
def cambiar_estado_estacion(id: int, activo: bool):
    resultado = crud.actualizar_estado_estacion(id, activo)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return resultado

@app.put("/estaciones/{id}/id")
def cambiar_id_estacion(id: int, nuevo_id: int):
    resultado = crud.actualizar_id_estacion(id, nuevo_id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return resultado

@app.get("/localidades", response_model=list[str])
def listar_localidades():
    response = supabase.table("estaciones").select("localidad", count="exact", distinct=True).execute()
    if response.error:
        raise HTTPException(status_code=500, detail="Error fetching localidades")
    return [loc["localidad"] for loc in response.data]
