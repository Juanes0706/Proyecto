from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    return crud.eliminar_bus(db, id)

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
    return crud.eliminar_estacion(db, id)

@app.put("/estaciones/{id}/estado")
def cambiar_estado_estacion(id: int, activo: bool, db: Session = Depends(get_db)):
    estacion = crud.actualizar_estado_estacion(db, id, activo)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return {"mensaje": f"Estado de estación actualizado a {'activo' if activo else 'inactivo'}"}

@app.get("/")
def root():
    return {"mensaje": "API de TransMilenio funcionando"}
