from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import models, schemas, crud
from db import SessionLocal, engine

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

@app.get("/delete", response_class=HTMLResponse)
async def delete_page(request: Request):
    return templates.TemplateResponse("DeletePage.html", {"request": request})

# ---------------------- BUSES ----------------------

@app.post("/buses/", response_model=schemas.Bus)
def crear_bus(bus: schemas.BusCreate, db: Session = Depends(get_db)):
    return crud.crear_bus(db, bus)

@app.get("/buses/", response_model=list[schemas.Bus])
def listar_buses(tipo: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.obtener_buses(db, tipo=tipo)

@app.get("/buses/{id}", response_model=schemas.Bus)
def obtener_bus(id: int, db: Session = Depends(get_db)):
    bus = crud.obtener_bus_por_id(db, id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return bus

@app.delete("/buses/{id}")
def eliminar_bus(id: int, db: Session = Depends(get_db)):
    resultado = crud.eliminar_bus(db, id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return resultado

@app.put("/buses/{id}/estado")
def cambiar_estado_bus(id: int, activo: bool, db: Session = Depends(get_db)):
    bus = crud.actualizar_estado_bus(db, id, activo)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return {"mensaje": f"Estado de bus actualizado a {'activo' if activo else 'inactivo'}"}

# ---------------------- ESTACIONES ----------------------

@app.post("/estaciones/", response_model=schemas.Estacion)
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db)):
    return crud.crear_estacion(db, estacion)

@app.get("/estaciones/", response_model=list[schemas.Estacion])
def listar_estaciones(sector: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.obtener_estaciones(db, sector=sector)

@app.get("/estaciones/{id}", response_model=schemas.Estacion)
def obtener_estacion(id: int, db: Session = Depends(get_db)):
    estacion = crud.obtener_estacion_por_id(db, id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return estacion

@app.delete("/estaciones/{id}")
def eliminar_estacion(id: int, db: Session = Depends(get_db)):
    resultado = crud.eliminar_estacion(db, id)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return resultado

@app.put("/estaciones/{id}/estado")
def cambiar_estado_estacion(id: int, activo: bool, db: Session = Depends(get_db)):
    estacion = crud.actualizar_estado_estacion(db, id, activo)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return {"mensaje": f"Estado de estación actualizado a {'activo' if activo else 'inactivo'}"}

@app.put("/estaciones/{id}/id")
def cambiar_id_estacion(id: int, nuevo_id: int, db: Session = Depends(get_db)):
    estacion = crud.actualizar_id_estacion(db, id, nuevo_id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return {"mensaje": f"ID de estación actualizado a {nuevo_id}"}
