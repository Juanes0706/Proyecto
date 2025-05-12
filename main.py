from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- RUTAS ----------------------

@app.post("/rutas/", response_model=schemas.Ruta)
def crear_ruta(ruta: schemas.RutaCreate, db: Session = Depends(get_db)):
    return crud.crear_ruta(db, ruta)

@app.get("/rutas/", response_model=list[schemas.Ruta])
def listar_rutas(db: Session = Depends(get_db)):
    return crud.obtener_rutas(db)

@app.get("/rutas/{id}", response_model=schemas.Ruta)
def obtener_ruta(id: int, db: Session = Depends(get_db)):
    ruta = crud.obtener_ruta_por_id(db, id)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return ruta

@app.delete("/rutas/{id}")
def eliminar_ruta(id: int, db: Session = Depends(get_db)):
    return crud.eliminar_ruta(db, id)

@app.put("/rutas/{id}/estado")
def cambiar_estado_ruta(id: int, activo: bool, db: Session = Depends(get_db)):
    ruta = crud.actualizar_estado_ruta(db, id, activo)
    if not ruta:
        raise HTTPException(status_code=404, detail="Ruta no encontrada")
    return {"mensaje": f"Estado de ruta actualizado a {'activo' if activo else 'inactivo'}"}

# ---------------------- BUSES ----------------------

@app.post("/buses/", response_model=schemas.Bus)
def crear_bus(bus: schemas.BusCreate, db: Session = Depends(get_db)):
    return crud.crear_bus(db, bus)

@app.get("/buses/", response_model=list[schemas.Bus])
def listar_buses(db: Session = Depends(get_db)):
    return crud.obtener_buses(db)

@app.get("/buses/{id}", response_model=schemas.Bus)
def obtener_bus(id: int, db: Session = Depends(get_db)):
    bus = crud.obtener_bus_por_id(db, id)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return bus

@app.delete("/buses/{id}")
def eliminar_bus(id: int, db: Session = Depends(get_db)):
    return crud.eliminar_bus(db, id)

@app.put("/buses/{id}/estado")
def cambiar_estado_bus(id: int, activo: bool, db: Session = Depends(get_db)):
    bus = crud.actualizar_estado_bus(db, id, activo)
    if not bus:
        raise HTTPException(status_code=404, detail="Bus no encontrado")
    return {"mensaje": f"Estado de bus actualizado a {'activo' if activo else 'inactivo'}"}

@app.get("/")
def root():
    return {"mensaje": "API de TransMilenio funcionando"}
