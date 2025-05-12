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

# ---------------------- ESTACIONES ----------------------

@app.post("/estaciones/", response_model=schemas.Estacion)
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db)):
    return crud.crear_estacion(db, estacion)

@app.get("/estaciones/", response_model=list[schemas.Estacion])
def listar_estaciones(db: Session = Depends(get_db)):
    return crud.obtener_estaciones(db)

@app.get("/estaciones/{id}", response_model=schemas.Estacion)
def obtener_estacion(id: int, db: Session = Depends(get_db)):
    estacion = crud.obtener_estacion_por_id(db, id)
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return estacion

@app.delete("/estaciones/{id}")
def eliminar_estacion(id: int, db: Session = Depends(get_db)):
    return crud.eliminar_estacion(db, id)

# ---------------------- PÁGINA PRINCIPAL ----------------------

@app.get("/")
def root():
    return {"mensaje": "API de TransMilenio funcionando"}
